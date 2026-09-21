$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force reports | Out-Null

Write-Host "[1/5] Dependency analysis - pip-audit"
pip-audit -f json -o reports\dependency-report.json

Write-Host "[2/5] Source-code scanning - Bandit"
bandit -r src -f json -o reports\bandit-report.json
bandit -r src -f html -o reports\bandit-report.html

Write-Host "[3/5] Secret detection - Gitleaks"
gitleaks dir . --report-format json --report-path reports\gitleaks-report.json

Write-Host "[4/5] Build container - Docker"
docker build -t battery-thermal-ml:security .

Write-Host "[5/5] Container security - Trivy"
trivy image --format json --output reports\container-report.json battery-thermal-ml:security
trivy image --scanners vuln,secret battery-thermal-ml:security
trivy image --image-config-scanners misconfig battery-thermal-ml:security

Write-Host "Security scan completed. Reports are in .\reports"
