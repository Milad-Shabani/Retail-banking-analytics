@echo off
setlocal enabledelayedexpansion

set REPO_NAME=Retail-banking-analytics
set GITHUB_USER=Milad-Shabani
set DESCRIPTION=Retail Banking Analytics -- end-to-end retail banking business analytics, financial planning, credit risk, churn ^& forecasting case study (synthetic data).

echo ==^> Initializing git repository
if not exist ".git" (
  git init
  git branch -M main
)

echo ==^> Staging and committing files
git add .
git commit -m "Initial commit: Retail Banking Analytics business intelligence case study"

echo ==^> Creating GitHub repository (if it doesn't already exist)
gh repo view %GITHUB_USER%/%REPO_NAME% >nul 2>&1
if errorlevel 1 (
  gh repo create %GITHUB_USER%/%REPO_NAME% --public --source=. --remote=origin --description "%DESCRIPTION%"
) else (
  git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git 2>nul
)

echo ==^> Pushing to GitHub
git push -u origin main
if errorlevel 1 (
  echo ==^> Remote already has content that conflicts with this initial commit ^(e.g. a README created on GitHub^).
  echo ==^> Force-pushing local project as the source of truth for this publish...
  git push -u origin main --force
)

echo ==^> Setting topics
gh repo edit %GITHUB_USER%/%REPO_NAME% --add-topic business-intelligence --add-topic data-analytics --add-topic python --add-topic forecasting --add-topic financial-modeling --add-topic credit-risk --add-topic machine-learning --add-topic optimization --add-topic banking --add-topic portfolio-project

echo ==^> Enabling GitHub Pages (served from the 'docs' folder)
gh api -X PUT repos/%GITHUB_USER%/%REPO_NAME%/pages -f "source[branch]=main" -f "source[path]=/docs" >nul 2>&1

gh repo edit %GITHUB_USER%/%REPO_NAME% --homepage "https://%GITHUB_USER%.github.io/%REPO_NAME%/"

echo ==^> Done.
echo Repo:      https://github.com/%GITHUB_USER%/%REPO_NAME%
echo Dashboard: https://%GITHUB_USER%.github.io/%REPO_NAME%/  (after the pages build runs)
