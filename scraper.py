"""
RPG Wix Page Scraper
Scrapes all live RPG pages using Playwright headless browser.
Extracts: full rendered HTML, text content, images, colors, fonts, layout structure.
"""

import os
import json
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("/home/ubuntu/rpg-build/scraped")
IMAGES_DIR = Path("/home/ubuntu/rpg-build/assets/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# All pages to scrape from the sitemap
# Format: (slug, url, notes)
PAGES = [
    # Main domain - readyplangrow.com
    ("home",            "https://www.readyplangrow.com/",                          "Homepage"),
    ("join",            "https://www.readyplangrow.com/join",                      "Join page"),
    ("community",       "https://www.readyplangrow.com/community",                 "Community"),
    ("about",           "https://www.readyplangrow.com/about-us",                  "About Us (old URL)"),
    ("contact",         "https://www.readyplangrow.com/contact",                   "Contact"),
    ("customer-stories","https://www.readyplangrow.com/customer-stories",          "Customer Stories"),
    ("how-it-works",    "https://www.readyplangrow.com/how-it-works",              "How It Works (retiring)"),
    ("blog",            "https://www.readyplangrow.com/blog",                      "Blog Index"),

    # Services subdomain
    ("solutions",       "https://services.readyplangrow.com/solutions",            "Solutions Overview"),
    ("smb-content",     "https://services.readyplangrow.com/smb-content-services", "SMB Content Services"),
    ("website-audit",   "https://services.readyplangrow.com/website-access-audit", "Website Access Audit"),
    ("ai-brand-audit",  "https://services.readyplangrow.com/ai-brand-audit",       "AI Brand Audit"),
    ("know-numbers",    "https://services.readyplangrow.com/know-your-numbers",    "Know Your Numbers"),
    ("pitch-deck",      "https://services.readyplangrow.com/pitch-deck-review",    "Pitch Deck Review"),
    ("partner-programs","https://services.readyplangrow.com/partner-programs",     "Partner Programs"),
    ("about-services",  "https://services.readyplangrow.com/about-us",             "About (services subdomain)"),
    ("marcela",         "https://services.readyplangrow.com/marcela-shine",        "Meet Marcela"),
    ("ryan",            "https://services.readyplangrow.com/ryan-cunningham",      "Meet Ryan"),
    ("education",       "https://services.readyplangrow.com/education",            "Education Hub"),
    ("edu-growth",      "https://services.readyplangrow.com/education/customer-growth",         "Customer Growth"),
    ("edu-research",    "https://services.readyplangrow.com/education/why-market-research",     "Why Market Research"),
    ("edu-marketing",   "https://services.readyplangrow.com/education/digital-marketing-guide", "Digital Marketing Guide"),
    ("edu-knowledge",   "https://services.readyplangrow.com/education/knowledge-base",          "Knowledge Base"),

    # Frameworks subdomain
    ("frameworks",      "https://frameworks.readyplangrow.com/",                   "Frameworks Hub"),
    ("brand-360",       "https://frameworks.readyplangrow.com/brand-360-audit-guide", "Brand 360 Audit Guide"),
    ("how-to",          "https://frameworks.readyplangrow.com/how-to",             "How-To Guides Hub"),
    ("how-to-chatgpt",  "https://frameworks.readyplangrow.com/how-to/chatgpt",     "How To ChatGPT"),
    ("how-to-claude",   "https://frameworks.readyplangrow.com/how-to/claude",      "How To Claude"),
    ("how-to-manus",    "https://frameworks.readyplangrow.com/how-to/manus",       "How To Manus"),
]

def scrape_page(page, slug, url, notes):
    """Scrape a single page and save results."""
    print(f"  Scraping: {slug} ({url})")
    result = {
        "slug": slug,
        "url": url,
        "notes": notes,
        "status": "unknown",
        "title": "",
        "meta_description": "",
        "h1": [],
        "h2": [],
        "h3": [],
        "nav_links": [],
        "cta_buttons": [],
        "paragraphs": [],
        "images": [],
        "colors": [],
        "fonts": [],
        "sections": [],
        "full_text": "",
        "html_file": "",
    }

    try:
        response = page.goto(url, wait_until="networkidle", timeout=30000)
        result["status"] = response.status if response else "no_response"
        time.sleep(2)  # Let dynamic content load

        # Title and meta
        result["title"] = page.title()
        meta_desc = page.query_selector('meta[name="description"]')
        if meta_desc:
            result["meta_description"] = meta_desc.get_attribute("content") or ""

        # Headings
        result["h1"] = [el.inner_text().strip() for el in page.query_selector_all("h1") if el.inner_text().strip()]
        result["h2"] = [el.inner_text().strip() for el in page.query_selector_all("h2") if el.inner_text().strip()]
        result["h3"] = [el.inner_text().strip() for el in page.query_selector_all("h3") if el.inner_text().strip()]

        # Paragraphs (meaningful ones only)
        paras = page.query_selector_all("p")
        result["paragraphs"] = [p.inner_text().strip() for p in paras if len(p.inner_text().strip()) > 30][:50]

        # CTA buttons
        buttons = page.query_selector_all("button, a[class*='btn'], a[class*='button'], a[class*='cta']")
        result["cta_buttons"] = list(set([b.inner_text().strip() for b in buttons if b.inner_text().strip() and len(b.inner_text().strip()) < 60]))[:20]

        # Nav links
        nav_els = page.query_selector_all("nav a, header a")
        result["nav_links"] = list(set([n.inner_text().strip() for n in nav_els if n.inner_text().strip()]))[:20]

        # Images (src and alt)
        imgs = page.query_selector_all("img")
        for img in imgs[:30]:
            src = img.get_attribute("src") or ""
            alt = img.get_attribute("alt") or ""
            if src and ("wix" in src or "readyplangrow" in src or src.startswith("http")):
                result["images"].append({"src": src, "alt": alt})

        # Full visible text
        result["full_text"] = page.inner_text("body")[:8000]

        # Save full rendered HTML
        html_content = page.content()
        html_file = OUTPUT_DIR / f"{slug}.html"
        html_file.write_text(html_content, encoding="utf-8")
        result["html_file"] = str(html_file)

        # Screenshot
        screenshot_file = OUTPUT_DIR / f"{slug}.png"
        page.screenshot(path=str(screenshot_file), full_page=True)
        result["screenshot"] = str(screenshot_file)

        print(f"    OK: {result['title'][:60]} | Status: {result['status']}")

    except Exception as e:
        result["status"] = f"error: {str(e)[:100]}"
        print(f"    ERROR: {str(e)[:80]}")

    return result


def main():
    print("=== RPG Wix Scraper Starting ===\n")
    all_results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for slug, url, notes in PAGES:
            result = scrape_page(page, slug, url, notes)
            all_results.append(result)
            # Small delay between pages
            time.sleep(1)

        browser.close()

    # Save all results to JSON
    output_file = OUTPUT_DIR / "scrape_results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n=== Scrape Complete ===")
    print(f"Pages attempted: {len(all_results)}")
    print(f"Successful: {sum(1 for r in all_results if isinstance(r['status'], int) and r['status'] == 200)}")
    print(f"Results saved to: {output_file}")

    # Print summary
    print("\n--- Summary ---")
    for r in all_results:
        status = r['status']
        title = r['title'][:50] if r['title'] else "(no title)"
        print(f"  [{status}] {r['slug']:25s} | {title}")


if __name__ == "__main__":
    main()
