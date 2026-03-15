"""
JSON/YAML Validation and Conversion Tool.

Provides agents with reliable JSON and YAML validation, optional JSON Schema
checking, and bidirectional JSON<->YAML conversion. No external API required.
"""

from __future__ import annotations

import json

import yaml
from fastmcp import FastMCP

_MAX_INPUT_BYTES = 1_000_000  # 1 MB — guard against oversized inputs


def _check_size(content: str) -> str | None:
    """Return an error string if content is too large, else None."""
    if len(content.encode("utf-8")) > _MAX_INPUT_BYTES:
        return f"Input too large (>{_MAX_INPUT_BYTES // 1024} KB); reduce size before validating."
    return None


def register_tools(mcp: FastMCP) -> None:
    """Register JSON/YAML tools with the MCP server."""

    @mcp.tool()
    def validate_json(content: str, schema: dict | None = None) -> dict:
        """
        Validate a JSON string, optionally against a JSON Schema.

        Args:
            content: JSON string to validate.
            schema: Optional JSON Schema dict. If provided, the parsed JSON is
                    validated against this schema using jsonschema.

        Returns:
            On success:  {"valid": True, "data": <parsed object>}
            On failure:  {"valid": False, "error": "<description>"}
        """
        size_error = _check_size(content)
        if size_error:
            return {"valid": False, "error": size_error}

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            return {"valid": False, "error": f"JSON parse error: {exc}"}

        if schema is not None:
            try:
                import jsonschema

                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.ValidationError as exc:
                return {"valid": False, "error": f"Schema validation error: {exc.message}"}
            except jsonschema.SchemaError as exc:
                return {"valid": False, "error": f"Invalid schema: {exc.message}"}
            except Exception as exc:
                return {"valid": False, "error": f"Validation error: {exc}"}

        return {"valid": True, "data": data}

    @mcp.tool()
    def validate_yaml(content: str) -> dict:
        """
        Validate a YAML string.

        Args:
            content: YAML string to validate.

        Returns:
            On success:  {"valid": True, "data": <parsed object>}
            On failure:  {"valid": False, "error": "<description>"}
        """
        size_error = _check_size(content)
        if size_error:
            return {"valid": False, "error": size_error}

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            return {"valid": False, "error": f"YAML parse error: {exc}"}

        return {"valid": True, "data": data}

    @mcp.tool()
    def json_to_yaml(content: str) -> dict:
        """
        Convert a JSON string to YAML format.

        Args:
            content: Valid JSON string to convert.

        Returns:
            On success:  {"yaml": "<yaml string>"}
            On failure:  {"error": "<description>"}
        """
        size_error = _check_size(content)
        if size_error:
            return {"error": size_error}

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            return {"error": f"JSON parse error: {exc}"}

        try:
            result = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            return {"yaml": result}
        except Exception as exc:
            return {"error": f"YAML conversion error: {exc}"}

    @mcp.tool()
    def yaml_to_json(content: str, indent: int = 2) -> dict:
        """
        Convert a YAML string to JSON format.

        Args:
            content: Valid YAML string to convert.
            indent: JSON indentation level (default 2). Use 0 for compact output.

        Returns:
            On success:  {"json": "<json string>"}
            On failure:  {"error": "<description>"}
        """
        size_error = _check_size(content)
        if size_error:
            return {"error": size_error}

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            return {"error": f"YAML parse error: {exc}"}

        try:
            indent_val = max(0, indent)
            result = json.dumps(data, indent=indent_val or None, ensure_ascii=False)
            return {"json": result}
        except Exception as exc:
            return {"error": f"JSON conversion error: {exc}"}
