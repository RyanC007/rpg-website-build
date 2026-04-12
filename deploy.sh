#!/bin/bash
# ============================================================
# RPG SITE DEPLOYMENT SCRIPT
# Manus → Hostinger SFTP Push
# Version: 1.0 | Ready, Plan, Grow!
# ============================================================
# USAGE:
#   ./deploy.sh                    → Deploy entire site
#   ./deploy.sh solutions          → Deploy single page only
#   ./deploy.sh education/how-to   → Deploy nested page
#
# SETUP (one-time):
#   1. Copy this file to your RPG build directory
#   2. Set the four variables below
#   3. chmod +x deploy.sh
#   4. Run: ./deploy.sh
# ============================================================

# ---- CONFIGURATION (fill these in after Hostinger setup) ----
SFTP_HOST="your-hostinger-server.com"       # From Hostinger hPanel → FTP Accounts
SFTP_USER="your_ftp_username"               # From Hostinger hPanel → FTP Accounts
SFTP_PASS="your_ftp_password"               # From Hostinger hPanel → FTP Accounts
REMOTE_PATH="/public_html"                  # Hostinger root (do NOT change unless on subdomain)
LOCAL_SITE_DIR="$(dirname "$0")/site"       # Path to the built site folder

# ---- COLORS FOR OUTPUT ----
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ---- DEPENDENCY CHECK ----
if ! command -v lftp &> /dev/null; then
    echo -e "${ORANGE}Installing lftp (required for SFTP)...${NC}"
    sudo apt-get install -y lftp 2>/dev/null || brew install lftp 2>/dev/null
fi

# ---- SINGLE PAGE DEPLOY ----
if [ -n "$1" ]; then
    PAGE_PATH="$1"
    LOCAL_PAGE="$LOCAL_SITE_DIR/$PAGE_PATH"
    REMOTE_PAGE="$REMOTE_PATH/$PAGE_PATH"

    if [ ! -d "$LOCAL_PAGE" ] && [ ! -f "$LOCAL_PAGE/index.html" ]; then
        echo -e "${RED}Error: Page not found at $LOCAL_PAGE${NC}"
        exit 1
    fi

    echo -e "${ORANGE}Deploying single page: /$PAGE_PATH${NC}"
    lftp -u "$SFTP_USER","$SFTP_PASS" sftp://"$SFTP_HOST" <<EOF
mirror --reverse --delete --verbose "$LOCAL_PAGE" "$REMOTE_PAGE"
quit
EOF
    echo -e "${GREEN}✓ Page deployed: https://readyplangrow.com/$PAGE_PATH${NC}"
    exit 0
fi

# ---- FULL SITE DEPLOY ----
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  RPG Site Deploy → Hostinger${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "  Source: ${LOCAL_SITE_DIR}"
echo -e "  Target: ${SFTP_HOST}${REMOTE_PATH}"
echo ""

# Confirm before full deploy
read -p "Deploy entire site to Hostinger? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

echo -e "${ORANGE}Connecting to Hostinger...${NC}"

lftp -u "$SFTP_USER","$SFTP_PASS" sftp://"$SFTP_HOST" <<EOF
set sftp:auto-confirm yes
set net:timeout 30
set net:max-retries 3

# Mirror the entire site directory to public_html
# --reverse: local → remote
# --delete: remove remote files not in local (keeps server clean)
# --exclude: skip files we don't want on the server
mirror --reverse --delete --verbose \
    --exclude .git \
    --exclude .DS_Store \
    --exclude "*.sh" \
    --exclude "*.md" \
    --exclude "scraped/" \
    "$LOCAL_SITE_DIR" "$REMOTE_PATH"

quit
EOF

DEPLOY_STATUS=$?

echo ""
if [ $DEPLOY_STATUS -eq 0 ]; then
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  ✓ Deploy complete!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo -e "  Live at: https://readyplangrow.com"
    echo ""
    echo -e "  Pages deployed:"
    find "$LOCAL_SITE_DIR" -name "index.html" | sed "s|$LOCAL_SITE_DIR||" | sed "s|/index.html||" | sort | while read -r page; do
        if [ -z "$page" ]; then
            echo -e "    → / (homepage)"
        else
            echo -e "    → $page"
        fi
    done
else
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  ✗ Deploy failed. Check credentials and try again.${NC}"
    echo -e "${RED}============================================${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify SFTP_HOST, SFTP_USER, SFTP_PASS in this script"
    echo "  2. In Hostinger hPanel → FTP Accounts → confirm credentials"
    echo "  3. Ensure your IP is not blocked in Hostinger security settings"
    exit 1
fi
