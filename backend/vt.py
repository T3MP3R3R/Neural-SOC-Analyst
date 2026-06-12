import re
import requests
from config import VT_API_KEY, VT_BASE_URL


def _headers():
    return {"x-apikey": VT_API_KEY}

def _detect_type(query: str) -> str:
    # Auto-detect whether the query is an IP, domain, URL or hash
    query = query.strip()

    if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", query):
        return "ip"

    if re.match(r"^[a-fA-F0-9]{32}$", query) or \
       re.match(r"^[a-fA-F0-9]{40}$", query) or \
       re.match(r"^[a-fA-F0-9]{64}$", query):
        return "hash"

    if re.match(r"^https?://", query):
        return "url"

    # fallback: treat as domain
    return "domain"


def _parse_stats(stats: dict) -> dict:
    # Extract malicious/suspicious counts from VT stats
    return {
        "malicious":  stats.get("malicious", 0),
        "suspicious": stats.get("suspicious", 0),
        "harmless":   stats.get("harmless", 0),
        "undetected": stats.get("undetected", 0),
        "total":      sum(stats.values())
    }


def lookup_ip(ip: str) -> dict:
    res = requests.get(f"{VT_BASE_URL}/ip_addresses/{ip}", headers=_headers(), timeout=10)
    if res.status_code != 200:
        return {"error": f"VT returned {res.status_code}"}

    data  = res.json().get("data", {})
    attrs = data.get("attributes", {})
    stats = _parse_stats(attrs.get("last_analysis_stats", {}))

    return {
        "type":    "ip",
        "query":   ip,
        "stats":   stats,
        "country": attrs.get("country", "unknown"),
        "owner":   attrs.get("as_owner", "unknown"),
        "verdict": "malicious" if stats["malicious"] > 0 else
                   "suspicious" if stats["suspicious"] > 0 else "clean"
    }


def lookup_hash(hash_val: str) -> dict:
    res = requests.get(f"{VT_BASE_URL}/files/{hash_val}", headers=_headers(), timeout=10)
    if res.status_code == 404:
        return {"type": "hash", "query": hash_val, "verdict": "not_found",
                "stats": {}, "name": "unknown"}
    if res.status_code != 200:
        return {"error": f"VT returned {res.status_code}"}

    data  = res.json().get("data", {})
    attrs = data.get("attributes", {})
    stats = _parse_stats(attrs.get("last_analysis_stats", {}))

    return {
        "type":    "hash",
        "query":   hash_val,
        "stats":   stats,
        "name":    attrs.get("meaningful_name", "unknown"),
        "type_tag":attrs.get("type_tag", "unknown"),
        "verdict": "malicious" if stats["malicious"] > 0 else
                   "suspicious" if stats["suspicious"] > 0 else "clean"
    }


def lookup_url(url: str) -> dict:
    import base64
    url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
    res = requests.get(f"{VT_BASE_URL}/urls/{url_id}", headers=_headers(), timeout=10)
    if res.status_code != 200:
        return {"error": f"VT returned {res.status_code}"}

    data  = res.json().get("data", {})
    attrs = data.get("attributes", {})
    stats = _parse_stats(attrs.get("last_analysis_stats", {}))

    return {
        "type":    "url",
        "query":   url,
        "stats":   stats,
        "verdict": "malicious" if stats["malicious"] > 0 else
                   "suspicious" if stats["suspicious"] > 0 else "clean"
    }


def lookup_domain(domain: str) -> dict:
    res = requests.get(f"{VT_BASE_URL}/domains/{domain}", headers=_headers(), timeout=10)
    if res.status_code != 200:
        return {"error": f"VT returned {res.status_code}"}

    data  = res.json().get("data", {})
    attrs = data.get("attributes", {})
    stats = _parse_stats(attrs.get("last_analysis_stats", {}))

    return {
        "type":      "domain",
        "query":     domain,
        "stats":     stats,
        "registrar": attrs.get("registrar", "unknown"),
        "verdict":   "malicious" if stats["malicious"] > 0 else
                     "suspicious" if stats["suspicious"] > 0 else "clean"
    }


def vt_lookup(query: str) -> dict:
    # Main entry point — auto-detects type and runs the right lookup.
    if not VT_API_KEY:
        return {"error": "VT_API_KEY not configured in .env"}

    query = query.strip()
    qtype = _detect_type(query)

    try:
        if qtype == "ip":     return lookup_ip(query)
        if qtype == "hash":   return lookup_hash(query)
        if qtype == "url":    return lookup_url(query)
        if qtype == "domain": return lookup_domain(query)
    except requests.Timeout:
        return {"error": "VirusTotal request timed out"}
    except Exception as e:
        return {"error": str(e)}