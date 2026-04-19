import urllib.request
import urllib.parse
import re


def lookup(query):
    title = urllib.parse.quote(query.replace(' ', '_'))
    url = f"https://nethackwiki.com/wiki/{title}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as r:
            html = r.read().decode('utf-8', errors='ignore')
    except Exception:
        return None

    match = re.search(r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>(.*?)<h2', html, re.S)
    if not match:
        return None
    text = re.sub(r'<[^>]+>', '', match.group(1))
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text[:800] if text else None
