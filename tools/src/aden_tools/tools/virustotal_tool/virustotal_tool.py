"""
VirusTotal Threat Intelligence Tool

Queries the VirusTotal API v3 to retrieve aggregate anti-virus vendor reports
and reputation scores for suspicious indicators of compromise (IoCs): IP
addresses, domain names, and file hashes.

Requires: VIRUSTOTAL_API_KEY (free community account from virustotal.com)
Rate limits: 500 req/day, 4 req/min (free tier)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import httpx
from fastmcp import FastMCP

if TYPE_CHECKING:
    from aden_tools.credentials import CredentialStoreAdapter

VT_BASE_URL = "https://www.virustotal.com/api/v3"
_TIMEOUT = 30.0


def _get_api_key(credentials: CredentialStoreAdapter | None) -> str | None:
    if credentials is not None:
        return credentials.get("virustotal")
    return os.getenv("VIRUSTOTAL_API_KEY")


def _make_request(
    api_key: str,
    path: str,
) -> dict[str, Any]:
    """Make an authenticated GET request to the VirusTotal API v3."""
    headers = {"x-apikey": api_key, "Accept": "application/json"}
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            resp = client.get(f"{VT_BASE_URL}{path}", headers=headers)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 401:
            return {"error": "Invalid VirusTotal API key. Check VIRUSTOTAL_API_KEY."}
        if resp.status_code == 404:
            return {"error": "Resource not found on VirusTotal."}
        if resp.status_code == 429:
            return {"error": "VirusTotal rate limit exceeded (4 req/min, 500 req/day free tier)."}
        return {"error": f"VirusTotal API error: HTTP {resp.status_code}"}
    except httpx.TimeoutException:
        return {"error": "VirusTotal request timed out."}
    except httpx.HTTPError as exc:
        return {"error": f"VirusTotal request failed: {exc}"}


def _summarize_stats(stats: dict[str, int]) -> dict[str, Any]:
    """Return a concise summary of vendor scan stats."""
    total = sum(stats.values())
    malicious = stats.get("malicious", 0)
    suspicious = stats.get("suspicious", 0)
    return {
        "malicious": malicious,
        "suspicious": suspicious,
        "harmless": stats.get("harmless", 0),
        "undetected": stats.get("undetected", 0),
        "total_engines": total,
        "threat_score": f"{malicious + suspicious}/{total}",
    }


def register_tools(
    mcp: FastMCP,
    credentials: CredentialStoreAdapter | None = None,
) -> None:
    """Register VirusTotal threat intelligence tools with the MCP server."""

    @mcp.tool()
    def vt_scan_ip(ip_address: str) -> dict:
        """
        Retrieve VirusTotal threat intelligence for an IP address.

        Returns aggregate anti-virus vendor verdicts, reputation score,
        ASN, country, and last analysis stats.

        Args:
            ip_address: IPv4 or IPv6 address to look up.

        Returns:
            Dict with vendor stats, reputation, ASN, country, and raw attributes.
        """
        api_key = _get_api_key(credentials)
        if not api_key:
            return {"error": "VIRUSTOTAL_API_KEY is not configured."}

        result = _make_request(api_key, f"/ip_addresses/{ip_address}")
        if "error" in result:
            return result

        attrs = result.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        return {
            "ip_address": ip_address,
            "reputation": attrs.get("reputation", 0),
            "country": attrs.get("country"),
            "asn": attrs.get("asn"),
            "as_owner": attrs.get("as_owner"),
            "network": attrs.get("network"),
            "analysis_stats": _summarize_stats(stats),
            "last_analysis_date": attrs.get("last_analysis_date"),
            "tags": attrs.get("tags", []),
        }

    @mcp.tool()
    def vt_scan_domain(domain: str) -> dict:
        """
        Retrieve VirusTotal threat intelligence for a domain name.

        Returns aggregate anti-virus vendor verdicts, reputation score,
        registrar, creation date, and last analysis stats.

        Args:
            domain: Domain name to look up (e.g., "example.com").

        Returns:
            Dict with vendor stats, reputation, registrar, dates, and categories.
        """
        api_key = _get_api_key(credentials)
        if not api_key:
            return {"error": "VIRUSTOTAL_API_KEY is not configured."}

        result = _make_request(api_key, f"/domains/{domain}")
        if "error" in result:
            return result

        attrs = result.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        return {
            "domain": domain,
            "reputation": attrs.get("reputation", 0),
            "registrar": attrs.get("registrar"),
            "creation_date": attrs.get("creation_date"),
            "last_update_date": attrs.get("last_update_date"),
            "analysis_stats": _summarize_stats(stats),
            "categories": attrs.get("categories", {}),
            "tags": attrs.get("tags", []),
            "last_analysis_date": attrs.get("last_analysis_date"),
        }

    @mcp.tool()
    def vt_scan_hash(file_hash: str) -> dict:
        """
        Retrieve VirusTotal threat intelligence for a file hash.

        Accepts MD5, SHA-1, or SHA-256 hashes. Returns aggregate anti-virus
        vendor verdicts, file type, size, and meaningful names.

        Args:
            file_hash: MD5, SHA-1, or SHA-256 hash of the file.

        Returns:
            Dict with vendor stats, file type, size, names, and tags.
        """
        api_key = _get_api_key(credentials)
        if not api_key:
            return {"error": "VIRUSTOTAL_API_KEY is not configured."}

        result = _make_request(api_key, f"/files/{file_hash}")
        if "error" in result:
            return result

        attrs = result.get("data", {}).get("attributes", {})
        stats = attrs.get("last_analysis_stats", {})
        return {
            "hash": file_hash,
            "sha256": attrs.get("sha256"),
            "sha1": attrs.get("sha1"),
            "md5": attrs.get("md5"),
            "file_type": attrs.get("type_description"),
            "magic": attrs.get("magic"),
            "size": attrs.get("size"),
            "names": attrs.get("names", [])[:10],
            "analysis_stats": _summarize_stats(stats),
            "tags": attrs.get("tags", []),
            "last_analysis_date": attrs.get("last_analysis_date"),
            "first_submission_date": attrs.get("first_submission_date"),
        }
