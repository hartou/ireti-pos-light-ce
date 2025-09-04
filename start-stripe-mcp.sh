#!/bin/bash

# Stripe MCP Server Startup Script
# This script starts the Stripe MCP server with the appropriate tools for the POS system

echo "🚀 Starting Stripe MCP Server for Ireti POS Light..."

# Load environment variables
source .env

# Start MCP server with POS-relevant tools
npx @stripe/mcp \
  --api-key="$STRIPE_SECRET_KEY" \
  --tools="paymentIntents.read,refunds.create,customers.create,customers.read,products.create,products.read,prices.read,balance.read"
