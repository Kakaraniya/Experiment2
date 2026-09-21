$ErrorActionPreference = "Stop"

if (-not $env:JWT_SECRET_KEY -or $env:JWT_SECRET_KEY.Length -lt 32) {
    throw "Set JWT_SECRET_KEY to a random value of at least 32 characters first."
}

Write-Host "1. Start the API in another PowerShell window: uvicorn src.app:app --reload"
Write-Host "2. Open http://127.0.0.1:8000/docs"
Write-Host "3. POST /token with username=student and password=student123"
Write-Host "4. Copy the access_token and click Authorize in Swagger."
Write-Host "5. POST /predict with a battery sensor reading."
Write-Host "6. Repeat /predict without a token and with an invalid token; both must return 401."
Write-Host "7. For an expired-token test, use a JWT whose exp claim is in the past."
