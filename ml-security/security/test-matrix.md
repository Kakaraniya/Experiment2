# Security test matrix

| No. | Security test | Tool / method | Expected result |
|---:|---|---|---|
| 1 | Dependency analysis | pip-audit | Known vulnerable dependencies/CVEs are reported |
| 2 | Source-code scan | Bandit | Insecure Python patterns are reported |
| 3 | Secret detection | Gitleaks | Fake classroom secrets are detected; final scan is clean after removal |
| 4 | Container build | Docker | Battery thermal ML image builds |
| 5 | Container vulnerability scan | Trivy | Image CVEs and severity are reported |
| 6 | Container secret scan | Trivy | Secrets embedded in the image are reported if present |
| 7 | Container misconfiguration scan | Trivy | Image configuration findings are reported |
| 8 | No-token prediction | FastAPI/Swagger | HTTP 401 |
| 9 | Valid token prediction | FastAPI/Swagger | HTTP 200 with predicted temperature and abnormal flag |
| 10 | Invalid token prediction | FastAPI/Swagger | HTTP 401 |
| 11 | Expired token prediction | FastAPI/Swagger | HTTP 401 |
| 12 | Re-scan after remediation | Same tools | Findings are reduced/resolved where applicable |
