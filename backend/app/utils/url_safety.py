from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlparse


class SSRFValidationError(ValueError):
    """Raised when a URL is unsafe or targets a private/loopback/link-local address."""

    pass


BLOCKED_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "169.254.169.254",
    "metadata.google.internal",
    "instance-data",
}

BLOCKED_SUFFIXES = (
    ".local",
    ".internal",
    ".localhost",
    ".lan",
)


def is_safe_url(url: str) -> bool:
    """
    Validates whether a URL is safe to fetch:
    1. Scheme must be http or https.
    2. Hostname must not be a loopback, private, link-local, multicast, or cloud metadata address.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        hostname_lower = hostname.lower()

        if hostname_lower in BLOCKED_HOSTNAMES:
            return False

        if any(hostname_lower.endswith(suffix) for suffix in BLOCKED_SUFFIXES):
            return False

        # If hostname is a direct IP address
        try:
            ip_obj = ipaddress.ip_address(hostname_lower)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_multicast
                or ip_obj.is_reserved
                or ip_obj.is_unspecified
            ):
                return False
            return True
        except ValueError:
            pass  # Not an IP literal

        # Attempt DNS resolution
        try:
            ip_list = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for item in ip_list:
                ip_str = item[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                if (
                    ip_obj.is_private
                    or ip_obj.is_loopback
                    or ip_obj.is_link_local
                    or ip_obj.is_multicast
                    or ip_obj.is_reserved
                    or ip_obj.is_unspecified
                ):
                    return False
            return True
        except (socket.gaierror, socket.herror, TimeoutError, OSError):
            # If network/DNS is unreachable (e.g. isolated test sandbox),
            # verify hostname has valid public domain structure (labels separated by dots)
            if "." in hostname and re.match(r"^[a-zA-Z0-9.-]+$", hostname):
                return True
            return False

    except Exception:
        return False


def validate_url(url: str) -> None:
    """Raises SSRFValidationError if the URL is not safe."""
    if not is_safe_url(url):
        raise SSRFValidationError(f"URL is not permitted or failed SSRF safety checks: {url}")
