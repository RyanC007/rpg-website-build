# RPG Website — Contributor Guide

**Repo:** `RyanC007/rpg-website-build`
**Staging URL:** https://ryanc007.github.io/rpg-website-build/
**Last updated:** April 2026

---

## Branch Structure

| Branch | Purpose |
| :--- | :--- |
| `gh-pages` | Live staging site — auto-deployed, never edit directly |
| `main` | Approved source of truth — merge into this to trigger a deploy |
| `ryan/work` | Ryan's working branch |
| `marcela/work` | Marcela's working branch |

**Rule:** Never push directly to `main` or `gh-pages`. Always work on your branch and open a Pull Request.

---

## How to Make a Change (Step by Step)

### 1. Always start from your branch

Ryan's instance:
```bash
cd /home/ubuntu/rpg-ghpages
git checkout ryan/work
git pull origin main  # sync with latest approved code first
```

Marcela's instance:
```bash
cd /home/ubuntu/rpg-ghpages
git checkout marcela/work
git pull origin main  # sync with latest approved code first
```

### 2. Make your changes

Edit any HTML file in the site directory. For example:
```bash
# Edit the About page
nano /home/ubuntu/rpg-ghpages/about/index.html
```

### 3. Commit your changes

```bash
git add -A
git commit -m "Brief description of what changed (e.g., Update About page hero copy)"
git push origin ryan/work   # or marcela/work
```

### 4. Open a Pull Request

```bash
gh pr create --base main --title "What you changed" --body "Brief description"
```

Or go to https://github.com/RyanC007/rpg-website-build/pulls and click "New pull request".

### 5. Review and merge

- The other person reviews the PR (or Ryan approves solo for minor changes)
- Click "Merge pull request" in GitHub
- GitHub Actions automatically deploys to `gh-pages` within 60 seconds
- Staging URL updates automatically

---

## Conflict Resolution

If two people edit the same file at the same time, Git will flag a merge conflict. To resolve:

```bash
git checkout ryan/work
git pull origin main
# Git will show the conflicting file with markers like <<<<<<< and >>>>>>>
# Edit the file to keep the correct version
git add -A
git commit -m "Resolve merge conflict on [filename]"
git push origin ryan/work
```

When in doubt, call it out in the PR description and let Ryan make the final call.

---

## Deploying to Hostinger (When Ready)

When Hostinger is provisioned, run the deploy script from `main`:

```bash
git checkout main
git pull origin main
bash /home/ubuntu/rpg-build/deploy.sh
```

This pushes the entire site to Hostinger via SFTP. Fill in your FTP credentials in `deploy.sh` first.

---

## Quick Reference

| Task | Command |
| :--- | :--- |
| Switch to your branch | `git checkout ryan/work` |
| Sync with latest main | `git pull origin main` |
| Stage all changes | `git add -A` |
| Commit | `git commit -m "message"` |
| Push your branch | `git push origin ryan/work` |
| Open a PR | `gh pr create --base main` |
| Check branch status | `git status` |
| See recent commits | `git log --oneline -10` |
