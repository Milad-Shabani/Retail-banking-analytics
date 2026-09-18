#!/usr/bin/env bash
# Publish this repository to GitHub as a new public repo, with topics and
# GitHub Pages (serving docs/index.html) enabled.
# Requires: git, and the GitHub CLI (`gh`) authenticated (`gh auth login`).
set -euo pipefail

REPO_NAME="Retail-banking-analytics"
GITHUB_USER="Milad-Shabani"
DESCRIPTION="Retail Banking Analytics -- customer intelligence, financial performance, risk, churn & forecasting case study (synthetic data)."

echo "==> Initializing git repository"
if [ ! -d ".git" ]; then
  git init
  git branch -M main
fi

echo "==> Staging and committing files"
git add .
git commit -m "Initial commit: Retail Banking Analytics" || echo "(nothing to commit)"

echo "==> Creating GitHub repository (if it doesn't already exist)"
if ! gh repo view "${GITHUB_USER}/${REPO_NAME}" >/dev/null 2>&1; then
  gh repo create "${GITHUB_USER}/${REPO_NAME}" --public --source=. --remote=origin --description "${DESCRIPTION}"
else
  git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git" 2>/dev/null || true
fi

echo "==> Pushing to GitHub"
if ! git push -u origin main; then
  echo "==> Remote already has content that conflicts with this initial commit (e.g. a README created on GitHub)."
  echo "==> Force-pushing local project as the source of truth for this publish..."
  git push -u origin main --force
fi

echo "==> Setting topics"
gh repo edit "${GITHUB_USER}/${REPO_NAME}" \
  --add-topic business-intelligence \
  --add-topic data-analytics \
  --add-topic python \
  --add-topic forecasting \
  --add-topic financial-modeling \
  --add-topic credit-risk \
  --add-topic machine-learning \
  --add-topic optimization \
  --add-topic banking \
  --add-topic portfolio-project

echo "==> Enabling GitHub Pages (served from the /docs folder on main)"
gh api -X PUT "repos/${GITHUB_USER}/${REPO_NAME}/pages" -f "source[branch]=main" -f "source[path]=/docs" >/dev/null 2>&1 || \
  echo "    (Pages API call failed or already configured — you can also enable it manually: Settings > Pages > Deploy from branch > main /docs)"

gh repo edit "${GITHUB_USER}/${REPO_NAME}" --homepage "https://${GITHUB_USER}.github.io/${REPO_NAME}/"

echo "==> Done."
echo "Repo:      https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo "Dashboard: https://${GITHUB_USER}.github.io/${REPO_NAME}/  (after the Pages build finishes)"
