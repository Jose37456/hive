"""
Country Info Tool — Free country data via restcountries.com.

No API key required. Provides country details including currencies,
languages, timezones, calling codes, flags, and population.

API: https://restcountries.com/v3.1/ (Mozilla Public License 2.0)
"""

from __future__ import annotations

import httpx
from fastmcp import FastMCP

_BASE_URL = "https://restcountries.com/v3.1"
_TIMEOUT = 15.0
_FIELDS = "name,cca2,cca3,currencies,languages,timezones,callingCodes,idd,flags,population,region,subregion,capital"  # noqa: E501


def _fetch(path: str) -> list[dict]:
    """Fetch from restcountries.com and return parsed JSON."""
    url = f"{_BASE_URL}/{path}?fields={_FIELDS}"
    resp = httpx.get(url, timeout=_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else [data]


def register_tools(mcp: FastMCP) -> None:
    """Register country info tools with the MCP server."""

    @mcp.tool()
    def country_get_by_name(name: str) -> dict:
        """
        Get country data by country name (full or partial).

        Args:
            name: Country name to search for (e.g., "Germany", "United States").

        Returns:
            List of matching countries with currency, languages, timezones,
            calling codes, flag URLs, population, region, and capital.
        """
        try:
            results = _fetch(f"name/{name}")
            return {"countries": results, "count": len(results)}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"No country found for name: {name}", "countries": []}
            return {"error": str(e), "countries": []}
        except Exception as e:
            return {"error": str(e), "countries": []}

    @mcp.tool()
    def country_get_by_code(code: str) -> dict:
        """
        Get country data by ISO 2-letter (e.g., "DE") or 3-letter (e.g., "DEU") code.

        Args:
            code: ISO 3166-1 alpha-2 or alpha-3 country code.

        Returns:
            Country data with currency, languages, timezones, calling codes,
            flag URLs, population, region, and capital.
        """
        try:
            results = _fetch(f"alpha/{code}")
            return {"countries": results, "count": len(results)}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": f"No country found for code: {code}", "countries": []}
            return {"error": str(e), "countries": []}
        except Exception as e:
            return {"error": str(e), "countries": []}

    @mcp.tool()
    def country_get_by_currency(currency_code: str) -> dict:
        """
        Find all countries that use a specific currency.

        Args:
            currency_code: ISO 4217 currency code (e.g., "EUR", "USD", "GBP").

        Returns:
            List of countries using that currency, with full country details.
        """
        try:
            results = _fetch(f"currency/{currency_code}")
            return {"countries": results, "count": len(results)}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {
                    "error": f"No countries found for currency: {currency_code}",
                    "countries": [],
                }
            return {"error": str(e), "countries": []}
        except Exception as e:
            return {"error": str(e), "countries": []}
