"""
Simple focused API integration tests for payments views.
Tests basic functionality first.
"""

import json
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from payments.models import PaymentTransaction, PaymentWebhook


User = get_user_model()


class BasicAPITest(TestCase):
    """Basic API functionality tests."""
    
    def setUp(self):
        """Set up test client and basic data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    @patch('payments.services.requests.post')
    def test_create_payment_intent_basic(self, mock_post):
        """Test basic payment intent creation."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'status': 'requires_payment_method',
            'amount': 2000,
            'currency': 'usd',
            'client_secret': 'pi_test_1234567890_secret_test'
        }
        mock_post.return_value = mock_response
        
        # Test API call
        response = self.client.post(
            '/payments/api/intent/',
            json.dumps({'amount': 20.00, 'currency': 'usd'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['payment_intent']['id'], 'pi_test_1234567890')
    
    @patch('payments.services.requests.get')
    def test_retrieve_payment_intent_basic(self, mock_get):
        """Test basic payment intent retrieval."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'status': 'succeeded',
            'amount': 2000,
            'currency': 'usd',
            'created': 1234567890
        }
        mock_get.return_value = mock_response
        
        # Test API call
        response = self.client.get('/payments/api/intent/pi_test_1234567890/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['payment_intent']['id'], 'pi_test_1234567890')
    
    def test_webhook_signature_verification(self):
        """Test webhook signature verification."""
        # Test with invalid signature
        response = self.client.post(
            '/payments/webhook/',
            json.dumps({'type': 'payment_intent.succeeded'}),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )
        
        self.assertEqual(response.status_code, 400)
        
    def test_payment_form_loads(self):
        """Test that payment form loads correctly."""
        # Test unauthenticated access - should redirect
        response = self.client.get('/payments/form/')
        self.assertEqual(response.status_code, 302)  # Redirects to login
        
        # Test authenticated access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/form/')
        self.assertEqual(response.status_code, 200)
