# MLSecOps security testing

This project adapts the battery thermal ML application to the security-testing workflow in the lab manual. The implemented controls use the manual's tools and methods:

- **pip-audit**: dependency vulnerability analysis.
- **Bandit**: Python source-code security scanning.
- **Gitleaks**: hard-coded secret detection.
- **Docker + Trivy**: container build, CVE/secret scanning, and image misconfiguration scanning.
- **FastAPI + JWT**: authentication and access control for prediction endpoints.

## API security

Set a strong local JWT signing key before starting the API. Never commit it:

```powershell
$env:JWT_SECRET_KEY="replace-with-a-random-value-at-least-32-characters"
uvicorn src.app:app --reload
```

For the classroom account, the default username is `student` and the stored password is an Argon2id hash. The lab password is `student123`; override `DEMO_PASSWORD_HASH` for any non-classroom deployment.

Security behavior:

- `GET /health` and `GET /ready` remain available for service monitoring.
- `POST /token` issues a 30-minute bearer JWT after username/password verification.
- `POST /predict` requires a valid JWT.
- `GET /api/dashboard` remains public so the monitoring dashboard can display operational telemetry.
- Missing, invalid, or expired tokens return HTTP 401.

## Security scans

From the project root in PowerShell:

```powershell
pip install -r requirements.txt
pip install pip-audit bandit
.\security\run_security_tests.ps1
```

Install Docker Desktop, Trivy, and Gitleaks separately as described in the lab manual. The script saves JSON/HTML results in `reports/`.

## Safe Gitleaks classroom test

Do not use a real key. Create only the fake test value:

```powershell
.\security\create_demo_secret.ps1
gitleaks dir . --report-format json --report-path reports\gitleaks-demo.json
Remove-Item security\demo-secret.txt
```

After removal, rerun Gitleaks on the project. The permanent source tree does not contain the fake secret.

## Security workflow

1. Install dependencies and generate/train the model.
2. Run pip-audit and Bandit.
3. Run the temporary Gitleaks demonstration, remove the fake secret, then scan again.
4. Build the Docker image.
5. Run Trivy vulnerability, secret, and misconfiguration scans.
6. Start the API with `JWT_SECRET_KEY` set.
7. Verify `/predict` returns 401 without a token, 200 with a valid token, and 401 with an invalid/expired token.
8. Fix findings, rebuild, rescan, and save the reports.

## Observation/report mapping

Use the generated files to fill the lab manual's observation tables:

- `reports/dependency-report.json` → Dependency Analysis table.
- `reports/bandit-report.html` / `reports/bandit-report.json` → Bandit table.
- `reports/gitleaks-report.json` → Secret Detection table.
- `reports/container-report.json` → Container Scan table.
- API test results → API Access Control table.

The lab manual's final workflow is **scan → identify → fix → rebuild → rescan → verify**; the project follows the same sequence. fileciteturn0file0L188-L204

### Kubernetes secret

Create the JWT signing secret outside the repository before applying the deployment:

```powershell
kubectl create secret generic battery-thermal-secrets --from-literal=jwt-secret="<random-32+-character-value>"
```

The deployment reads `JWT_SECRET_KEY` from that Kubernetes Secret rather than storing the signing key in the YAML file.
