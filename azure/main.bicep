@description('Location for all resources')
param location string = resourceGroup().location

@description('Name of the Container App')
param containerAppName string = 'ireti-pos-app'

@description('Name of the Container Apps Environment')
param containerAppsEnvironmentName string = 'ireti-pos-env'

@description('Container image to deploy')
param containerImage string = 'ghcr.io/hartou/ireti-pos-light-ce:latest'

@description('Django superuser password')
@secure()
param djangoSuperuserPassword string

@description('Stripe secret key')
@secure()
param stripeSecretKey string

@description('Stripe publishable key')
param stripePublishableKey string

@description('Stripe webhook endpoint secret')
@secure()
param stripeWebhookSecret string

// Log Analytics Workspace for Container Apps
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${containerAppsEnvironmentName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppsEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

// Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'django-superuser-password'
          value: djangoSuperuserPassword
        }
        {
          name: 'stripe-secret-key'
          value: stripeSecretKey
        }
        {
          name: 'stripe-webhook-secret'
          value: stripeWebhookSecret
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'ireti-pos'
          image: containerImage
          env: [
            {
              name: 'DJANGO_SUPERUSER_USERNAME'
              value: 'admin'
            }
            {
              name: 'DJANGO_SUPERUSER_EMAIL'
              value: 'admin@example.com'
            }
            {
              name: 'DJANGO_SUPERUSER_PASSWORD'
              secretRef: 'django-superuser-password'
            }
            {
              name: 'STRIPE_SECRET_KEY'
              secretRef: 'stripe-secret-key'
            }
            {
              name: 'STRIPE_PUBLISHABLE_KEY'
              value: stripePublishableKey
            }
            {
              name: 'STRIPE_WEBHOOK_ENDPOINT_SECRET'
              secretRef: 'stripe-webhook-secret'
            }
            {
              name: 'DJANGO_SETTINGS_MODULE'
              value: 'iretilightpos.settings.devlopement'
            }
          ]
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 10
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '30'
              }
            }
          }
        ]
      }
    }
  }
}

@description('The FQDN of the Container App')
output applicationUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'

@description('The resource ID of the Container App')
output containerAppId string = containerApp.id
