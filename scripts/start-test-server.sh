#!/bin/bash
# Start markdown-vault test server for MCP testing

set -e

# Load test environment variables
source .env.test

echo "🚀 Starting markdown-vault test server..."
echo "  - Host: ${MARKDOWN_VAULT_SERVER__HOST}"
echo "  - Port: ${MARKDOWN_VAULT_SERVER__PORT}"
echo "  - Vault: ${MARKDOWN_VAULT_VAULT__PATH}"
echo "  - API Key: ${MARKDOWN_VAULT_API_KEY}"
echo ""

# Start the server
python -m markdown_vault start --config test_config.yaml
