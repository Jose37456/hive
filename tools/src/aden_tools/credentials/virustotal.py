"""VirusTotal API credentials."""

from .base import CredentialSpec

VIRUSTOTAL_CREDENTIALS = {
    "virustotal": CredentialSpec(
        env_var="VIRUSTOTAL_API_KEY",
        tools=["vt_scan_ip", "vt_scan_domain", "vt_scan_hash"],
        node_types=[],
        required=True,
        startup_required=False,
        help_url="https://www.virustotal.com/gui/join-us",
        description="API key for VirusTotal threat intelligence (IP, domain, file hash scanning)",
        direct_api_key_supported=True,
        api_key_instructions="""To get a VirusTotal API key:
1. Go to https://www.virustotal.com/gui/join-us and create a free community account
2. Verify your email address and log in
3. Click on your profile icon (top right) and select "API Key"
4. Copy the alphanumeric API key provided

Free tier: 500 requests/day, 4 requests/minute""",
        health_check_endpoint="https://www.virustotal.com/api/v3/domains/google.com",
        credential_id="virustotal",
        credential_key="api_key",
    ),
}
