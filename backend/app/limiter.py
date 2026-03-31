from slowapi import Limiter
from fastapi import Request


def _get_real_ip(request: Request) -> str:
    """Return the real client IP.

    nginx sets X-Real-IP to $remote_addr for every request.
    Falls back to the direct ASGI connection address (useful for tests
    and local dev where there is no proxy in front).
    """
    forwarded = request.headers.get("X-Real-IP")
    if forwarded:
        return forwarded
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


limiter = Limiter(key_func=_get_real_ip)
