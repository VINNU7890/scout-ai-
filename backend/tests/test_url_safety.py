import pytest

from backend.app.utils.url_safety import SSRFValidationError, is_safe_url, validate_url


def test_safe_urls():
    assert is_safe_url("https://example.com") is True
    assert is_safe_url("https://www.google.com/search?q=test") is True


def test_unsafe_schemes():
    assert is_safe_url("ftp://example.com") is False
    assert is_safe_url("file:///etc/passwd") is False
    assert is_safe_url("gopher://evil.com") is False
    assert is_safe_url("javascript:alert(1)") is False


def test_private_and_loopback_ips():
    assert is_safe_url("http://127.0.0.1:8000") is False
    assert is_safe_url("http://localhost:3000") is False
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False
    assert is_safe_url("http://10.0.0.1/admin") is False
    assert is_safe_url("http://192.168.1.1/") is False
    assert is_safe_url("http://[::1]/") is False


def test_validate_url_exception():
    with pytest.raises(SSRFValidationError):
        validate_url("http://127.0.0.1:8000/api")
