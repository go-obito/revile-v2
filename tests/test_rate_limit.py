from fastapi import Request

from app.rate_limit import client_ip_from_request


def make_request(peer: str, real_ip: str | None = None) -> Request:
    headers = [(b"x-real-ip", real_ip.encode())] if real_ip else []
    return Request({"type": "http", "method": "POST", "path": "/", "headers": headers, "client": (peer, 443)})


def test_x_real_ip_is_authoritative() -> None:
    assert client_ip_from_request(make_request("198.51.100.9", "1.2.3.4")) == "1.2.3.4"


def test_peer_is_fallback_without_x_real_ip() -> None:
    assert client_ip_from_request(make_request("198.51.100.9")) == "198.51.100.9"
