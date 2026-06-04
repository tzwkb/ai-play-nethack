import urllib.request
import urllib.parse
import re

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'identity',
}

_MIRRORS = [
    'https://nethackwiki.com/wiki/{}',
    'https://alt.nethackwiki.com/wiki/{}',
]


def lookup(query):
    title = urllib.parse.quote(query.replace(' ', '_'))
    for mirror in _MIRRORS:
        url = mirror.format(title)
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode('utf-8', errors='ignore')
        except Exception:
            continue

        # Cloudflare challenge page — try next mirror
        if 'cf-browser-verification' in html or 'Just a moment' in html:
            continue

        match = re.search(r'<div[^>]*class="[^"]*mw-parser-output[^"]*"[^>]*>(.*?)<h2', html, re.S)
        if not match:
            continue
        text = re.sub(r'<[^>]+>', '', match.group(1))
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text[:800] if text else None

    return None
