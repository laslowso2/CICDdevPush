# How to push this repo to GitHub

This guide covers everything from creating the GitHub repo to making your first commit
that triggers the CI pipeline. It assumes you have Git installed and a GitHub account.

---

## Part 1 - First time setup (do this once)

### Step 1 - Install Git if you do not have it

```bash
# Check if Git is already installed
git --version

# If not installed:
# Windows:  https://git-scm.com/download/win  (download and run the installer)
# macOS:    brew install git
# Ubuntu:   sudo apt-get install git
```

### Step 2 - Configure Git with your identity

Git stamps every commit with your name and email. Run these once on any new machine.

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

### Step 3 - Create the GitHub repository

1. Go to https://github.com and sign in.
2. Click the **+** icon in the top-right corner and choose **New repository**.
3. Name it `api-definitions` (or whatever fits your naming convention).
4. Set visibility to **Private** (recommended for API definitions).
5. Do NOT tick "Add a README" or "Add .gitignore" - you will push your own files.
6. Click **Create repository**.

GitHub will show you a page with setup instructions. Keep it open - you will need the repo URL in the next step.

### Step 4 - Initialize the local repo and push

Open a terminal in the root of the folder you downloaded (the one containing `.github/`, `domains/`, `shared/`, `README.md`).

```bash
# Initialize Git in the current folder
git init

# Tell Git about your remote GitHub repo
# Replace YOUR-USERNAME and YOUR-REPO-NAME with your actual values
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Stage all files for the first commit
git add .

# Commit with a message
git commit -m "chore: initial repo structure with domain-based API organization"

# Push to GitHub
# -u sets the upstream so future pushes just need: git push
git push -u origin main
```

If Git asks for credentials, use your GitHub username and a Personal Access Token
(not your password - GitHub disabled password auth in 2021).

**Create a Personal Access Token:**
1. Go to GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic).
2. Click Generate new token.
3. Give it a name, set expiry, and check the `repo` scope.
4. Copy the token and use it as the password when Git prompts you.

---

## Part 2 - Set up GitHub Secrets for the pipeline

The pipeline reads APIM credentials from GitHub Secrets so they never appear in code.

1. In your GitHub repo, go to **Settings > Secrets and variables > Actions**.
2. Click **New repository secret** for each of the following:

| Secret name    | Value                              |
|----------------|------------------------------------|
| APIM_HOST      | https://localhost:9443             |
| APIM_USERNAME  | admin                              |
| APIM_PASSWORD  | your APIM admin password           |

**Note on localhost and GitHub Actions:** GitHub-hosted runners run in the cloud and
cannot reach your laptop's localhost:9443. You have two options:

**Option A - Self-hosted runner (recommended for demo):**
A self-hosted runner is a small agent you run on the same machine as APIM. It takes
about five minutes to set up.

1. Go to your repo > Settings > Actions > Runners > New self-hosted runner.
2. Follow the instructions GitHub shows (three commands to download, configure, and start the agent).
3. The runner registers itself and the pipeline will use it automatically.

**Option B - Expose localhost temporarily:**
Use `ngrok` to create a temporary public tunnel to your APIM port.

```bash
# Install ngrok from https://ngrok.com then run:
ngrok http 9443

# It will print something like:
# Forwarding  https://abc123.ngrok.io -> localhost:9443

# Update the APIM_HOST secret to that ngrok URL for the demo.
```

---

## Part 3 - Adding a new API (the developer workflow)

This is the day-to-day flow that a developer follows when they add a new API.

### Step 1 - Create the API folder

```bash
# From the repo root, create the folder for the new API
# Replace {domain} with security, finance, or integration
# Replace {api-name} with a descriptive kebab-case name

mkdir -p domains/{domain}/{api-name}/Definitions
mkdir -p domains/{domain}/{api-name}/Meta-information
```

Example for a new Reporting API in the Finance domain:

```bash
mkdir -p domains/finance/reporting-api/Definitions
mkdir -p domains/finance/reporting-api/Meta-information
```

### Step 2 - Add the OpenAPI spec

Copy the developer's OpenAPI spec from Visual Studio Code into the Definitions folder:

```bash
cp /path/to/reporting-api.yaml domains/finance/reporting-api/Definitions/swagger.yaml
```

Or the developer can create it directly in VS Code and save it to that path.

### Step 3 - Add the API metadata

Copy the shared template and fill in the API-specific values:

```bash
cp shared/templates/api-template.yaml domains/finance/reporting-api/Meta-information/api.yaml
```

Open the file and update the fields marked `# CHANGE THIS`:
- `name` - must be unique in APIM
- `version`
- `context` - the URL path (e.g. `/reporting/1.0`)
- `operations` - one entry per path + verb from the swagger.yaml

### Step 4 (optional) - Add environment-specific params

If the new API has a different backend URL than the shared default, create a params.yaml:

```bash
cp shared/params-dev.yaml domains/finance/reporting-api/params.yaml
# Then edit the URL inside it
```

### Step 5 - Commit and push

```bash
# Stage only the new API folder
git add domains/finance/reporting-api/

# Commit
git commit -m "feat(finance): add reporting-api v1.0"

# Push - this triggers the GitHub Actions pipeline
git push
```

The pipeline will detect that only `domains/finance/reporting-api` changed and
deploy just that API. It will not redeploy every other API in the repo.

### Step 6 - Watch the pipeline run

1. Go to your GitHub repo and click the **Actions** tab.
2. You will see the workflow run appear within a few seconds of the push.
3. Click it to watch the steps in real time.
4. When the run turns green, open https://localhost:9443/devportal and the API
   will be listed under the Finance domain tags.

---

## Part 4 - Updating an existing API

When a developer modifies an OpenAPI spec in VS Code and wants to redeploy:

```bash
# Make the change to the swagger.yaml, then:
git add domains/finance/reporting-api/Definitions/swagger.yaml
git commit -m "fix(finance/reporting): add missing 404 response to /reports/{id}"
git push
```

The pipeline uses `--update` in the apictl import command so it updates the existing
API in APIM rather than creating a duplicate.

---

## Part 5 - Manually trigger a deployment

If you want to deploy an API without making a code change (for example, to recover
from a failed run), go to the Actions tab, select the workflow, click
**Run workflow**, enter the API folder path, and click the green button.

```
Example path to enter:  domains/finance/reporting-api
```

---

## Branching strategy (recommended)

For the demo, pushing directly to main is fine. In a real team setup, use branches:

```bash
# Developer creates a feature branch
git checkout -b feat/finance/reporting-api

# Makes changes, then pushes the branch
git push -u origin feat/finance/reporting-api

# Opens a Pull Request on GitHub
# After review and merge to main, the pipeline deploys automatically
```

This gives you a review gate before anything lands in APIM.
