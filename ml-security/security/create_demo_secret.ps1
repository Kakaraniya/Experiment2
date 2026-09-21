$ErrorActionPreference = "Stop"
Set-Content -Path "security\demo-secret.txt" -Value 'API_KEY="DEMO-FAKE-KEY-123456789"'
Write-Host "Created a fake classroom secret at security\demo-secret.txt"
Write-Host "Run: gitleaks dir . --report-format json --report-path reports\gitleaks-demo.json"
Write-Host "Delete it immediately after the demonstration: Remove-Item security\demo-secret.txt"
