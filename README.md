# Ready, Plan, Grow! — Site Build

**Version:** 1.0 | Built by Scarlett (RPG AI Partner)
**Status:** Pre-deployment — awaiting Hostinger credentials

---

## What's in this repo

This is the complete static HTML site build for `readyplangrow.com`, plus the deployment and automation tooling.

```
rpg-build/
├── site/                        ← The full website (deploy this to Hostinger)
│   ├── index.html               ← Homepage (/)
│   ├── assets/
│   │   ├── css/rpg.css          ← Master RPG design system
│   │   ├── js/rpg.js            ← Nav toggle, FAQ accordion, shared JS
│   │   └── partials.html        ← Nav + footer reference snippets
│   ├── solutions/               ← /solutions
│   ├── smb-content-services/    ← /smb-content-services
│   ├── ai-brand-audit/          ← /ai-brand-audit
│   ├── website-access-audit/    ← /website-access-audit
│   ├── know-your-numbers/       ← /know-your-numbers
│   ├── pitch-deck-review/       ← /pitch-deck-review
│   ├── partner-programs/        ← /partner-programs
│   ├── community/               ← /community
│   ├── join/                    ← /join
│   ├── event-list/              ← /event-list
│   ├── contact/                 ← /contact
│   ├── about/                   ← /about
│   │   ├── marcela-shine/       ← /about/marcela-shine
│   │   └── ryan-cunningham/     ← /about/ryan-cunningham
│   ├── customer-stories/        ← /customer-stories
│   ├── frameworks/              ← /frameworks
│   │   └── brand-360-audit-guide/ ← /frameworks/brand-360-audit-guide
│   └── education/               ← /education
│       ├── customer-growth/     ← /education/customer-growth
│       ├── why-market-research/ ← /education/why-market-research
│       ├── digital-marketing-guide/ ← /education/digital-marketing-guide
│       ├── knowledge-base/      ← /education/knowledge-base
│       └── how-to/              ← /education/how-to
│           ├── chatgpt/         ← /education/how-to/chatgpt
│           ├── claude/          ← /education/how-to/claude
│           └── manus/           ← /education/how-to/manus
├── deploy.sh                    ← SFTP deploy script (Manus → Hostinger)
├── blog_autopublish.py          ← Auto-research + WordPress publish pipeline
├── blog_topic_queue.txt         ← Queue of 30 blog topics (add more anytime)
└── README.md                    ← This file
```

---

## Deploying to Hostinger

### One-time setup

1. Log in to Hostinger hPanel
2. Go to **Hosting → Manage → FTP Accounts**
3. Note your FTP hostname, username, and password
4. Open `deploy.sh` and fill in the four config variables at the top:

```bash
SFTP_HOST="your-hostinger-server.com"
SFTP_USER="your_ftp_username"
SFTP_PASS="your_ftp_password"
REMOTE_PATH="/public_html"
```

5. Make the script executable:
```bash
chmod +x deploy.sh
```

### Deploy the full site

```bash
./deploy.sh
```

### Deploy a single page (after edits)

```bash
./deploy.sh solutions
./deploy.sh education/how-to/chatgpt
./deploy.sh about/marcela-shine
```

---

## WordPress (Blog + Member Area)

WordPress lives at `readyplangrow.com/blog` and handles:
- Blog posts (`/blog/[slug]`)
- Member area (`/starters`, `/premium`)
- Events (`/event-list` — WordPress manages the data, HTML page is the frontend)

### Required WordPress plugins (install via hPanel Auto Installer)

| Plugin | Purpose |
| :--- | :--- |
| Yoast SEO | Meta descriptions, sitemaps, focus keywords |
| MemberPress | Membership tiers, gated content, Stripe billing |
| WPForms | Contact forms, join forms |
| Redirection | 301 redirects from old Wix URLs |
| WP Mail SMTP | Reliable email delivery via SendGrid/Mailgun |
| Wordfence | Security |

---

## Auto Blog Publishing

The `blog_autopublish.py` script researches a topic and publishes a full SEO-optimized post to WordPress automatically.

### One-time setup

1. Install dependencies:
```bash
pip install requests openai beautifulsoup4
```

2. Open `blog_autopublish.py` and fill in the `CONFIG` block:
```python
"wp_url": "https://readyplangrow.com",
"wp_user": "your_wp_username",
"wp_app_password": "xxxx xxxx xxxx xxxx xxxx",  # WP Admin → Users → Application Passwords
"openai_api_key": "sk-..."
```

### Publish from the queue

```bash
python3 blog_autopublish.py
```

### Publish a specific topic

```bash
python3 blog_autopublish.py "How to build a referral program for your small business"
```

### Publish as draft (safe mode — review before going live)

```bash
python3 blog_autopublish.py --draft "Your topic here"
```

### Add topics to the queue

Open `blog_topic_queue.txt` and add one topic per line. The script pops from the top each time it runs.

---

## DNS Cutover Checklist (when ready)

Do NOT switch DNS until all of the following are confirmed:

- [ ] All 26 HTML pages load correctly on Hostinger staging URL
- [ ] WordPress is installed and `/blog` is live
- [ ] MemberPress is configured with Stripe keys
- [ ] WPForms is connected to Kit (ConvertKit)
- [ ] Redirection plugin has all 301 redirects loaded
- [ ] Google Search Console verified on new server
- [ ] SSL certificate active on Hostinger

**DNS switch:** Update nameservers at your domain registrar to point to Hostinger. Propagation takes 24-48 hours. Keep Wix live until propagation is confirmed complete.

---

## Adding new pages (the workflow)

1. Create a new folder in `site/[page-slug]/`
2. Create `index.html` inside it using the existing pages as templates
3. Link `../../assets/css/rpg.css` and `../../assets/js/rpg.js` (adjust depth as needed)
4. Run `./deploy.sh [page-slug]` to push just that page
5. Commit to GitHub

---

## Brand reference

- **Primary color:** `#F5C518` (yellow)
- **Orange:** `#FF681E`
- **Green:** `#5F9C3F`
- **Navy/Dark:** `#1a1a2e`
- **Font:** Poppins (Google Fonts)
- **Voice:** Direct, conversational, anti-BS. No em dashes. No jargon.

---

*Built by Scarlett, AI Partner for Ready, Plan, Grow!*
