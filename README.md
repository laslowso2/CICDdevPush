# WSO2 APIM CI/CD Demo - Domain-based API Repository

APIs are grouped by business domain. Each domain folder contains one subfolder
per API. The GitHub Actions pipeline watches `domains/**` and deploys only the
API that changed - not everything in the repo.

---

## Repository structure

```
api-definitions/
├── .github/
│   └── workflows/
│       └── deploy-api.yml          # Pipeline - triggers on push to domains/**
│
├── domains/
│   ├── security/
│   │   ├── auth-api/               # OAuth2 token service
│   │   ├── identity-api/           # User identity / SCIM
│   │   └── rbac-api/               # Role based access control
│   │
│   ├── finance/
│   │   ├── payments-api/           # Payment processing
│   │   ├── orders-api/             # Customer orders
│   │   └── billing-api/            # Invoicing and billing
│   │
│   └── integration/
│       ├── erp-api/                # ERP connector
│       ├── crm-api/                # CRM connector
│       └── messaging-api/          # Event and queue bridge
│
├── shared/
│   ├── templates/
│   │   └── api-template.yaml       # Base template for new APIs
│   ├── policies/
│   │   └── throttle-tiers.yaml     # Reference for available throttle policies
│   └── params-dev.yaml             # Shared fallback params for dev environment
│
└── docs/
    └── how-to-push-to-github.md    # Developer onboarding guide
```

Each API folder follows the same internal structure:

```
{domain}/{api-name}/
├── Definitions/
│   └── swagger.yaml                # OpenAPI 3.0 spec - developers edit this
├── Meta-information/
│   └── api.yaml                    # Security, tiers, scopes, throttle policies
└── params.yaml                     # (optional) endpoint URLs for this environment
```

---

## Setup

See `docs/how-to-push-to-github.md` for the full guide including:
- Creating the GitHub repo and first push
- Adding GitHub Secrets for APIM credentials
- Self-hosted runner setup for localhost APIM
- Day-to-day developer workflow for adding and updating APIs

---

## Adding a new API

```bash
# Create folders
mkdir -p domains/{domain}/{api-name}/Definitions
mkdir -p domains/{domain}/{api-name}/Meta-information

# Drop in the OpenAPI spec
cp your-spec.yaml domains/{domain}/{api-name}/Definitions/swagger.yaml

# Copy and fill in the template
cp shared/templates/api-template.yaml domains/{domain}/{api-name}/Meta-information/api.yaml

# Commit and push - pipeline deploys only this API
git add domains/{domain}/{api-name}/
git commit -m "feat({domain}): add {api-name} v1.0"
git push
```

---

## GitHub Secrets required

| Secret         | Value                        |
|----------------|------------------------------|
| APIM_HOST      | https://localhost:9443       |
| APIM_USERNAME  | admin                        |
| APIM_PASSWORD  | your APIM password           |
