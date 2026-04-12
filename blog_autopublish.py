#!/usr/bin/env python3
"""
RPG Auto-Research and Blog Publishing Pipeline
Ready, Plan, Grow! | Version 1.0

WHAT THIS DOES:
  1. Takes a blog topic (or picks one from a queue file)
  2. Researches the topic using Google search and web scraping
  3. Generates a full SEO-optimized blog post using the RPG brand voice
  4. Publishes it to WordPress via the REST API
  5. Logs the result

SETUP:
  pip install requests openai beautifulsoup4
  Set the CONFIG variables below after Hostinger/WordPress is live.

USAGE:
  python3 blog_autopublish.py                          # Uses next topic from queue
  python3 blog_autopublish.py "Your blog topic here"   # Specific topic
  python3 blog_autopublish.py --draft "Topic"          # Publish as draft (safe mode)
"""

import os
import sys
import json
import requests
import datetime
from bs4 import BeautifulSoup

# ============================================================
# CONFIGURATION (fill in after WordPress is live on Hostinger)
# ============================================================

CONFIG = {
    # WordPress REST API
    "wp_url": "https://readyplangrow.com",           # Your WordPress URL
    "wp_user": "your_wp_username",                    # WordPress admin username
    "wp_app_password": "xxxx xxxx xxxx xxxx xxxx",   # WordPress Application Password
                                                       # (WP Admin → Users → Application Passwords)

    # OpenAI (for content generation)
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),

    # Blog settings
    "default_category": "Small Business Tips",        # Default WP category
    "default_author_id": 1,                           # WordPress author ID
    "publish_status": "publish",                      # "publish" or "draft"

    # Topic queue file (one topic per line)
    "topic_queue_file": "blog_topic_queue.txt",

    # RPG Brand Voice Context (loaded into every generation prompt)
    "brand_context": """
You are a content writer for Ready, Plan, Grow! (readyplangrow.com).
Ready, Plan, Grow! helps small business owners grow with clarity, control, and confidence using AI-powered marketing systems.
Co-founders: Marcela Shine (operations/marketing expert) and Ryan Cunningham (AI/e-commerce expert).

BRAND VOICE:
- Direct, conversational, anti-BS, sarcastic but respectful
- No corporate jargon. No fluff. No em dashes.
- Second person ("you"). Active voice. Short paragraphs (2-3 sentences max).
- Educational but not preachy. Empathetic to small business owner struggles.
- Contractions are fine. Sound like a knowledgeable friend, not a consultant.

TARGET READER: Small business owner, 1-10 employees, limited time and budget, overwhelmed by marketing options.

SEO RULES:
- Include the target keyword in the H1, first paragraph, at least 2 H2s, and meta description.
- Use H2 and H3 subheadings to break up the content.
- Aim for 800-1200 words.
- End with a clear CTA linking to a relevant RPG page.
"""
}

# ============================================================
# RESEARCH: Gather context on the topic
# ============================================================

def research_topic(topic: str) -> str:
    """Search Google and scrape top results to gather research context."""
    print(f"  Researching: {topic}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    search_url = f"https://www.google.com/search?q={requests.utils.quote(topic + ' small business')}&num=5"

    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract search result snippets
        snippets = []
        for div in soup.find_all("div", class_=["BNeawe", "s3v9rd", "AP7Wnd"])[:10]:
            text = div.get_text().strip()
            if len(text) > 50:
                snippets.append(text)

        research_context = "\n\n".join(snippets[:5]) if snippets else "No research context available."
        print(f"  Research gathered: {len(snippets)} snippets")
        return research_context

    except Exception as e:
        print(f"  Research warning: {e}. Proceeding without research context.")
        return ""


# ============================================================
# GENERATE: Create the blog post with OpenAI
# ============================================================

def generate_blog_post(topic: str, research_context: str) -> dict:
    """Generate a full blog post using OpenAI GPT."""
    from openai import OpenAI

    client = OpenAI(api_key=CONFIG["openai_api_key"])

    prompt = f"""
{CONFIG["brand_context"]}

TASK: Write a complete, SEO-optimized blog post for Ready, Plan, Grow! on the following topic.

TOPIC: {topic}

RESEARCH CONTEXT (use this to ground the content in real information):
{research_context}

OUTPUT FORMAT (return valid JSON only, no markdown wrapper):
{{
  "title": "The blog post title (H1, includes target keyword)",
  "meta_description": "155-character SEO meta description with keyword",
  "slug": "url-friendly-slug",
  "excerpt": "2-3 sentence excerpt for the blog listing page",
  "content": "Full HTML blog post content using <h2>, <h3>, <p>, <ul>, <li> tags. No inline styles. 800-1200 words. End with a CTA paragraph linking to a relevant RPG page.",
  "tags": ["tag1", "tag2", "tag3"],
  "focus_keyword": "primary SEO keyword"
}}
"""

    print("  Generating blog post with GPT...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2500
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    post_data = json.loads(raw)
    print(f"  Generated: \"{post_data['title']}\"")
    return post_data


# ============================================================
# PUBLISH: Push to WordPress via REST API
# ============================================================

def publish_to_wordpress(post_data: dict, status: str = "publish") -> dict:
    """Publish the generated post to WordPress via REST API."""
    wp_api = f"{CONFIG['wp_url']}/wp-json/wp/v2/posts"

    # Get or create category
    category_id = get_or_create_category(CONFIG["default_category"])

    # Get or create tags
    tag_ids = [get_or_create_tag(tag) for tag in post_data.get("tags", [])]

    payload = {
        "title": post_data["title"],
        "content": post_data["content"],
        "excerpt": post_data.get("excerpt", ""),
        "slug": post_data.get("slug", ""),
        "status": status,
        "categories": [category_id],
        "tags": tag_ids,
        "meta": {
            "_yoast_wpseo_metadesc": post_data.get("meta_description", ""),
            "_yoast_wpseo_focuskw": post_data.get("focus_keyword", ""),
        }
    }

    resp = requests.post(
        wp_api,
        json=payload,
        auth=(CONFIG["wp_user"], CONFIG["wp_app_password"]),
        timeout=30
    )

    if resp.status_code in [200, 201]:
        result = resp.json()
        print(f"  Published: {result.get('link', 'unknown URL')}")
        return result
    else:
        raise Exception(f"WordPress API error {resp.status_code}: {resp.text[:200]}")


def get_or_create_category(name: str) -> int:
    """Get category ID by name, create if it doesn't exist."""
    api = f"{CONFIG['wp_url']}/wp-json/wp/v2/categories"
    resp = requests.get(api, params={"search": name}, auth=(CONFIG["wp_user"], CONFIG["wp_app_password"]))
    cats = resp.json()
    if cats:
        return cats[0]["id"]
    create = requests.post(api, json={"name": name}, auth=(CONFIG["wp_user"], CONFIG["wp_app_password"]))
    return create.json()["id"]


def get_or_create_tag(name: str) -> int:
    """Get tag ID by name, create if it doesn't exist."""
    api = f"{CONFIG['wp_url']}/wp-json/wp/v2/tags"
    resp = requests.get(api, params={"search": name}, auth=(CONFIG["wp_user"], CONFIG["wp_app_password"]))
    tags = resp.json()
    if tags:
        return tags[0]["id"]
    create = requests.post(api, json={"name": name}, auth=(CONFIG["wp_user"], CONFIG["wp_app_password"]))
    return create.json()["id"]


# ============================================================
# QUEUE: Read/write the topic queue file
# ============================================================

def get_next_topic_from_queue() -> str | None:
    """Pop the first topic from the queue file."""
    queue_file = CONFIG["topic_queue_file"]
    if not os.path.exists(queue_file):
        return None
    with open(queue_file, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if not lines:
        return None
    topic = lines[0]
    with open(queue_file, "w") as f:
        f.write("\n".join(lines[1:]) + "\n")
    return topic


def log_result(topic: str, post_url: str, status: str):
    """Append result to the publish log."""
    log_file = "blog_publish_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} | {status} | {topic} | {post_url}\n")


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n=== RPG Auto-Blog Publisher ===\n")

    # Determine publish status
    draft_mode = "--draft" in sys.argv
    publish_status = "draft" if draft_mode else CONFIG["publish_status"]

    # Get topic
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        topic = " ".join(args)
    else:
        topic = get_next_topic_from_queue()
        if not topic:
            print("No topic provided and queue is empty.")
            print(f"Add topics to {CONFIG['topic_queue_file']} (one per line) or pass as argument.")
            sys.exit(1)

    print(f"Topic: {topic}")
    print(f"Status: {publish_status}\n")

    # Step 1: Research
    research = research_topic(topic)

    # Step 2: Generate
    post_data = generate_blog_post(topic, research)

    # Step 3: Publish
    print(f"\n  Publishing to WordPress ({publish_status})...")
    result = publish_to_wordpress(post_data, status=publish_status)
    post_url = result.get("link", "unknown")

    # Step 4: Log
    log_result(topic, post_url, publish_status)

    print(f"\n=== Done ===")
    print(f"  Post URL: {post_url}")
    print(f"  Status: {publish_status}")
    print(f"  Logged to: blog_publish_log.txt\n")


if __name__ == "__main__":
    main()
