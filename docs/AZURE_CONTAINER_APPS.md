# Azure Container Apps Configuration for Ireti POS Light CE

## Deployment Details
- **Service**: Azure Container Apps
- **SKU**: Consumption (Serverless)
- **Container Source**: GitHub Container Registry (GHCR)
- **Image**: `ghcr.io/hartou/ireti-pos-light-ce:latest`

## Resource Configuration

### Container App Settings
```yaml
name: ireti-pos-app
location: eastus
workloadProfile: Consumption
```

### Container Configuration
```yaml
container:
  image: ghcr.io/hartou/ireti-pos-light-ce:latest
  resources:
    cpu: 0.25 cores
    memory: 0.5Gi
  targetPort: 8000
```

### Scaling Configuration
```yaml
scaling:
  minReplicas: 0          # Scale to zero when not used
  maxReplicas: 10         # Scale up based on demand
  rules:
    - name: http-scaling
      http:
        concurrentRequests: 30
```

### Ingress Configuration
```yaml
ingress:
  external: true
  transport: auto
  allowInsecure: false    # HTTPS only
  targetPort: 8000
```

## Environment Variables

### Application Configuration
| Variable | Value | Type |
|----------|--------|------|
| `DJANGO_SUPERUSER_USERNAME` | `admin` | Plain |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` | Plain |
| `DJANGO_SETTINGS_MODULE` | `iretilightpos.settings.devlopement` | Plain |

### Secrets (Stored securely in Azure)
| Variable | Secret Name | Description |
|----------|-------------|-------------|
| `DJANGO_SUPERUSER_PASSWORD` | `superuser-password` | Admin login password |
| `STRIPE_SECRET_KEY` | `stripe-secret-key` | Stripe API secret key |
| `STRIPE_PUBLISHABLE_KEY` | `stripe-publishable-key` | Stripe publishable key |
| `STRIPE_WEBHOOK_ENDPOINT_SECRET` | `stripe-webhook-secret` | Stripe webhook secret |

## Cost Optimization Features

### Consumption SKU Benefits
- ✅ **Scale to Zero**: No cost when not in use
- ✅ **Pay per Use**: Only pay for actual consumption
- ✅ **Auto-scaling**: Handles traffic spikes automatically
- ✅ **No minimum charges**: Start at $0/month

### Resource Limits
- **CPU**: 0.25 cores (sufficient for Django app)
- **Memory**: 0.5Gi (optimized for the container)
- **Max Replicas**: 10 (handles up to ~300 concurrent users)

## Deployment Commands

### Quick Deploy
```bash
./scripts/deploy-azure-containerapp.sh
```

### Manual Deploy
```bash
# Set subscription
az account set --subscription "86c5f895-13b2-4329-8e76-87a91892a809"

# Create resource group
az group create --name "rg-ireti-pos" --location "eastus"

# Create Container Apps environment
az containerapp env create \
  --name "ireti-pos-env" \
  --resource-group "rg-ireti-pos" \
  --location "eastus"

# Deploy container app
az containerapp create \
  --name "ireti-pos-app" \
  --resource-group "rg-ireti-pos" \
  --environment "ireti-pos-env" \
  --image "ghcr.io/hartou/ireti-pos-light-ce:latest" \
  --target-port 8000 \
  --ingress external \
  --cpu 0.25 \
  --memory 0.5Gi \
  --min-replicas 0 \
  --max-replicas 10
```

## Post-Deployment Steps

### 1. Update Stripe Configuration
Replace test keys with production keys:
```bash
az containerapp secret set \
  --name "ireti-pos-app" \
  --resource-group "rg-ireti-pos" \
  --secrets stripe-secret-key=sk_live_YOUR_SECRET_KEY
```

### 2. Configure Custom Domain (Optional)
```bash
az containerapp hostname add \
  --name "ireti-pos-app" \
  --resource-group "rg-ireti-pos" \
  --hostname "pos.yourdomain.com"
```

### 3. Monitor and Scale
- View metrics in Azure Portal
- Set up alerts for high CPU/memory usage
- Configure log analytics for debugging

## Expected Costs

### Consumption SKU Pricing (East US)
- **CPU**: $0.000024/vCPU/second
- **Memory**: $0.000003/GiB/second
- **Requests**: $0.40/million requests

### Monthly Cost Estimates
| Usage Level | CPU Hours | Memory Hours | Requests | Monthly Cost |
|-------------|-----------|--------------|----------|--------------|
| Light (100 users/day) | 50h | 50h | 100K | ~$2-5 |
| Medium (500 users/day) | 200h | 200h | 500K | ~$8-15 |
| Heavy (1000+ users/day) | 500h | 500h | 1M+ | ~$20-40 |

*Costs include scale-to-zero benefits during off-hours*

## Monitoring & Troubleshooting

### View Logs
```bash
az containerapp logs show \
  --name "ireti-pos-app" \
  --resource-group "rg-ireti-pos" \
  --follow
```

### Check Status
```bash
az containerapp show \
  --name "ireti-pos-app" \
  --resource-group "rg-ireti-pos" \
  --query "properties.runningStatus"
```

### Update Container
```bash
az containerapp update \
  --name "ireti-pos-app" \
  --resource-group "rg-ireti-pos" \
  --image "ghcr.io/hartou/ireti-pos-light-ce:latest"
```