#!/bin/bash
# GitHub Code Scanning Validation Script
# Validates that all security scanning workflows are properly configured

echo "=== GitHub Code Scanning Validation ==="
echo ""

# Check workflow files exist
WORKFLOWS=(
    "codeql-analysis.yml"
    "security-audit.yml" 
    "dependency-scan.yml"
    "secret-scanning.yml"
)

echo "📁 Checking workflow files..."
for workflow in "${WORKFLOWS[@]}"; do
    if [ -f ".github/workflows/$workflow" ]; then
        echo "✅ $workflow - Found"
    else
        echo "❌ $workflow - Missing"
    fi
done

# Check dependabot configuration
echo ""
echo "📋 Checking Dependabot configuration..."
if [ -f ".github/dependabot.yml" ]; then
    echo "✅ dependabot.yml - Found"
else
    echo "❌ dependabot.yml - Missing"
fi

# Validate YAML syntax
echo ""
echo "🔍 Validating YAML syntax..."
python3 -c "
import yaml
import sys

files = [
    '.github/workflows/codeql-analysis.yml',
    '.github/workflows/security-audit.yml',
    '.github/workflows/dependency-scan.yml', 
    '.github/workflows/secret-scanning.yml',
    '.github/dependabot.yml'
]

all_valid = True
for file in files:
    try:
        with open(file, 'r') as f:
            yaml.safe_load(f)
        print(f'✅ {file} - Valid YAML')
    except Exception as e:
        print(f'❌ {file} - Invalid YAML: {e}')
        all_valid = False

if all_valid:
    print('\n🎉 All YAML files are valid!')
else:
    print('\n🚨 Some YAML files have syntax errors')
    sys.exit(1)
"

# Check PCI compliance script
echo ""
echo "🔒 Checking PCI compliance integration..."
if [ -f "scripts/pci_compliance_check.py" ]; then
    echo "✅ PCI compliance script - Found"
else
    echo "❌ PCI compliance script - Missing"
fi

# Check documentation
echo ""
echo "📚 Checking documentation..."
if [ -f "docs/GITHUB_CODE_SCANNING.md" ]; then
    echo "✅ GitHub Code Scanning documentation - Found"
else
    echo "❌ GitHub Code Scanning documentation - Missing"
fi

echo ""
echo "=== Validation Complete ==="
echo ""
echo "🚀 GitHub Code Scanning deployment is ready!"
echo "📊 Security monitoring will begin when workflows are triggered"
echo "🔍 Check the Security tab after the first workflow runs"