import json
import re
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS/2.0"}


def _fetch(url, timeout=8):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def _strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "")


def _wiki(query):
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 3,
            "format": "json",
            "utf8": 1,
        }
    )
    data = json.loads(_fetch(url))
    hits = data.get("query", {}).get("search", [])
    if not hits:
        return None
    lines = []
    for h in hits[:3]:
        title = h.get("title", "")
        snippet = _strip_tags(h.get("snippet", ""))
        lines.append(f"- {title}: {snippet}")
    return "WIKIPEDIA RESULTS:\n" + "\n".join(lines)


def _ddg(query):
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    html = _fetch(url)
    results = re.findall(
        r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        html,
        re.S,
    )
    if not results:
        return None
    lines = []
    for href, title, snip in results[:5]:
        t = _strip_tags(title)
        s = _strip_tags(snip)
        lines.append(f"- {t}: {s}")
    return "WEB RESULTS:\n" + "\n".join(lines)


def search_web(query, max_len=2500):
    out = None
    try:
        out = _wiki(query)
    except Exception:
        out = None
    if not out:
        try:
            out = _ddg(query)
        except Exception:
            out = None
    if not out:
        return "No results found for: " + query
    return out[:max_len]