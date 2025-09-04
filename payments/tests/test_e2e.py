"""
End-to-end tests for payment workflow integration.
Tests complete payment and refund workflows from API to database.
"""

import json
import time
from decimal import Decimal
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from payments.models import PaymentTransaction, PaymentRefund, PaymentWebhook


User = get_user_model()


class PaymentWorkflowE2ETest(TestCase):
    """End-to-end tests for complete payment workflows."""
    
    def setUp(self):
        """Set up test environment with users and products."""
        self.client = Client()
        
        # Create test users
        self.customer_user = User.objects.create_user(
            username='customer',
            password='customer123',
            email='customer@example.com'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            email='staff@example.com',
            is_staff=True
        )
        
        # Define test product data for metadata
        self.product_data = {
            'id': '12345',
            'name': 'Test Coffee',
            'price': '15.99'
        }
    
    @patch('payments.services.requests.post')
    @patch('payments.services.requests.get')
    def test_complete_successful_payment_workflow(self, mock_get, mock_post):
        """Test complete workflow: Create → Retrieve → Confirm → Webhook."""
        
        # Step 1: Create Payment Intent
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                'id': 'pi_test_e2e_success',
                'status': 'requires_payment_method',
                'amount': 1599,  # $15.99 in cents
                'currency': 'usd',
                'client_secret': 'pi_test_e2e_success_secret_test'
            }
        )
        
        create_response = self.client.post(
            '/payments/api/intent/',
            json.dumps({
                'amount': 15.99,
                'currency': 'usd',
                'metadata': {'product_id': self.product_data['id']}
            }),
            content_type='application/json'
        )
        
        self.assertEqual(create_response.status_code, 200)
        create_data = create_response.json()
        self.assertTrue(create_data['success'])
        payment_intent_id = create_data['payment_intent']['id']
        local_transaction_id = create_data['local_transaction_id']
        
        # Verify local transaction was created
        transaction = PaymentTransaction.objects.get(id=local_transaction_id)
        self.assertEqual(transaction.stripe_payment_intent_id, payment_intent_id)
        self.assertEqual(transaction.amount, Decimal('15.99'))
        self.assertEqual(transaction.status, 'requires_payment_method')
        
        # Step 2: Retrieve Payment Intent
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                'id': 'pi_test_e2e_success',
                'status': 'requires_confirmation',
                'amount': 1599,
                'currency': 'usd',
                'payment_method': 'pm_card_visa',
                'created': int(time.time())
            }
        )
        
        retrieve_response = self.client.get(f'/payments/api/intent/{payment_intent_id}/')
        
        self.assertEqual(retrieve_response.status_code, 200)
        retrieve_data = retrieve_response.json()
        self.assertTrue(retrieve_data['success'])
        self.assertEqual(retrieve_data['payment_intent']['status'], 'requires_confirmation')
        
        # Step 3: Confirm Payment Intent
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                'id': 'pi_test_e2e_success',
                'status': 'succeeded',
                'amount': 1599,
                'currency': 'usd',
                'charges': {
                    'data': [{
                        'id': 'ch_test_e2e_success',
                        'status': 'succeeded'
                    }]
                }
            }
        )
        
        confirm_response = self.client.post(
            f'/payments/api/confirm/{payment_intent_id}/',
            json.dumps({'return_url': 'https://example.com/return'}),
            content_type='application/json'
        )
        
        self.assertEqual(confirm_response.status_code, 200)
        confirm_data = confirm_response.json()
        self.assertTrue(confirm_data['success'])
        
        # Step 4: Process Success Webhook
        webhook_payload = json.dumps({
            'id': 'evt_e2e_success',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': payment_intent_id,
                    'status': 'succeeded',
                    'amount': 1599,
                    'currency': 'usd'
                }
            },
            'created': int(time.time())
        })
        
        # Mock webhook signature verification
        with patch('payments.services.stripe_service.verify_webhook_signature', return_value=True):
            webhook_response = self.client.post(
                '/payments/webhook/',
                data=webhook_payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='valid_signature'
            )
        
        self.assertEqual(webhook_response.status_code, 200)
        
        # Verify final state
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'succeeded')
        
        # Verify webhook record
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_e2e_success')
        self.assertEqual(webhook.event_type, 'payment_intent.succeeded')
        self.assertTrue(webhook.processed)
    
    @patch('payments.services.requests.post')
    def test_complete_refund_workflow(self, mock_post):
        """Test complete refund workflow: Create payment → Create refund → Webhook."""
        
        # Create initial successful payment
        payment_transaction = PaymentTransaction.objects.create(
            stripe_payment_intent_id='pi_test_refund_workflow',
            amount=Decimal('25.00'),
            currency='USD',
            status='succeeded'
        )
        
        # Step 1: Create refund
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                'id': 'ref_test_e2e_refund',
                'status': 'succeeded',
                'amount': 2500,
                'currency': 'usd',
                'payment_intent': 'pi_test_refund_workflow',
                'reason': 'requested_by_customer'
            }
        )
        
        refund_response = self.client.post(
            '/payments/api/refund/',
            json.dumps({
                'payment_intent_id': 'pi_test_refund_workflow',
                'amount': 25.00
            }),
            content_type='application/json'
        )
        
        self.assertEqual(refund_response.status_code, 200)
        refund_data = refund_response.json()
        self.assertTrue(refund_data['success'])
        
        # Verify local refund record was created
        refund = PaymentRefund.objects.get(
            payment_transaction=payment_transaction
        )
        self.assertEqual(refund.amount, Decimal('25.00'))
        self.assertEqual(refund.status, 'succeeded')
        
        # Step 2: Process refund success webhook
        webhook_payload = json.dumps({
            'id': 'evt_refund_succeeded',
            'type': 'charge.refund.updated',
            'data': {
                'object': {
                    'id': 'ref_test_e2e_refund',
                    'status': 'succeeded',
                    'amount': 2500,
                    'currency': 'usd',
                    'payment_intent': 'pi_test_refund_workflow'
                }
            },
            'created': int(time.time())
        })
        
        # Mock webhook signature verification
        with patch('payments.services.stripe_service.verify_webhook_signature', return_value=True):
            webhook_response = self.client.post(
                '/payments/webhook/',
                data=webhook_payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='valid_signature'
            )
        
        self.assertEqual(webhook_response.status_code, 200)
        
        # Verify webhook was processed
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_refund_succeeded')
        self.assertEqual(webhook.event_type, 'charge.refund.updated')
    
    @patch('payments.services.requests.post')
    def test_payment_failure_workflow(self, mock_post):
        """Test payment failure workflow with proper error handling."""
        
        # Step 1: Create payment intent that will fail
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {
                'id': 'pi_test_failure_workflow',
                'status': 'requires_payment_method',
                'amount': 5000,
                'currency': 'usd',
                'client_secret': 'pi_test_failure_workflow_secret'
            }
        )
        
        create_response = self.client.post(
            '/payments/api/intent/',
            json.dumps({
                'amount': 50.00,
                'currency': 'usd'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(create_response.status_code, 200)
        create_data = create_response.json()
        payment_intent_id = create_data['payment_intent']['id']
        local_transaction_id = create_data['local_transaction_id']
        
        # Step 2: Process failure webhook
        webhook_payload = json.dumps({
            'id': 'evt_payment_failed',
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': payment_intent_id,
                    'status': 'requires_payment_method',
                    'amount': 5000,
                    'currency': 'usd',
                    'last_payment_error': {
                        'message': 'Your card was declined.',
                        'decline_code': 'generic_decline'
                    }
                }
            },
            'created': int(time.time())
        })
        
        # Mock webhook signature verification
        with patch('payments.services.stripe_service.verify_webhook_signature', return_value=True):
            webhook_response = self.client.post(
                '/payments/webhook/',
                data=webhook_payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='valid_signature'
            )
        
        self.assertEqual(webhook_response.status_code, 200)
        
        # Verify transaction status was updated
        transaction = PaymentTransaction.objects.get(id=local_transaction_id)
        self.assertEqual(transaction.status, 'requires_payment_method')
        
        # Verify webhook was processed
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_payment_failed')
        self.assertEqual(webhook.event_type, 'payment_intent.payment_failed')
        self.assertTrue(webhook.processed)
    
    def test_authentication_required_for_dashboard_views(self):
        """Test that dashboard views require proper authentication."""
        
        # Test unauthenticated access to dashboard
        response = self.client.get('/payments/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirects to login
        
        # Test authenticated access
        self.client.login(username='staff', password='staff123')
        response = self.client.get('/payments/dashboard/')
        self.assertEqual(response.status_code, 200)
    
    def test_data_consistency_across_workflow_steps(self):
        """Test that data remains consistent throughout the payment workflow."""
        
        # This test verifies that amounts, currencies, and metadata
        # are preserved correctly across all workflow steps
        
        original_amount = Decimal('42.99')
        original_currency = 'USD'
        original_metadata = {
            'product_id': self.product_data['id'],
            'customer_email': 'test@example.com'
        }
        
        with patch('payments.services.requests.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'id': 'pi_consistency_test',
                    'status': 'requires_payment_method',
                    'amount': int(original_amount * 100),  # Convert to cents
                    'currency': original_currency.lower(),
                    'client_secret': 'pi_consistency_test_secret'
                }
            )
            
            # Create payment intent
            response = self.client.post(
                '/payments/api/intent/',
                json.dumps({
                    'amount': float(original_amount),
                    'currency': original_currency,
                    'metadata': original_metadata
                }),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Verify data consistency in response
            self.assertEqual(
                data['payment_intent']['amount'], 
                int(original_amount * 100)
            )
            self.assertEqual(
                data['payment_intent']['currency'], 
                original_currency.lower()
            )
            
            # Verify data consistency in database
            transaction = PaymentTransaction.objects.get(
                id=data['local_transaction_id']
            )
            self.assertEqual(transaction.amount, original_amount)
            self.assertEqual(transaction.currency, original_currency)
            self.assertEqual(
                transaction.metadata['product_id'], 
                original_metadata['product_id']
            )
