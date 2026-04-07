import ipaddress
import os

from slowapi import Limiter
from fastapi import Request

# Comma-separated list of trusted proxy CIDRs. Requests from these addresses
# are allowed to set X-Real-IP; all others use the direct connection address.
# Defaults to loopback + RFC1918 ranges (covers Docker/Nginx deployments).
_TRUSTED_PROXIES_RAW = os.getenv(
    "TRUSTED_PROXIES",
    "127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16",
)

_trusted_networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
for _part in _TRUSTED_PROXIES_RAW.split(","):
    _part = _part.strip()
    if _part:
        try:
            _trusted_networks.append(ipaddress.ip_network(_part, strict=False))
        except ValueError:
            pass


def _get_real_ip(request: Request) -> str:
    """Return the real client IP.

    Only trusts X-Real-IP when the connection originates from a configured
    trusted proxy (loopback / RFC1918 by default, i.e. our Nginx container).
    Falls back to the direct ASGI connection address for local dev and any
    request that did not come through a trusted proxy.
    """
    client_host = request.client.host if request.client else "127.0.0.1"
    try:
        client_addr = ipaddress.ip_address(client_host)
    except ValueError:
        return client_host

    if any(client_addr in net for net in _trusted_networks):
        forwarded = request.headers.get("X-Real-IP")
        if forwarded:
            return forwarded

    return client_host


limiter = Limiter(key_func=_get_real_ip)
