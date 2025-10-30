import logging
import hashlib
import hmac
from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# Dependency for API key validation
async def require_api_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> None:
    """
    FastAPI dependency that verifies a provided API key against the
    hex-encoded SHA-256 hash stored in settings.MASTER_API_KEY_SHA256.

    - Header: X-API-Key: <raw api key>
    - Compares using constant-time comparison
    - If MASTER_API_KEY_SHA256 is not configured:
      - In development, bypass with a warning for local/dev scenarios
      - In production, raise 500 to signal server misconfiguration
    """
    logger.debug("Verifying API key...")

    # NOTE: This logic can be changed to use a more secure method of storing the API key, such as a JWT token.
    # NOTE: The API key can be stored in a more secure way, such as in a database.
    expected_hash = (settings.MASTER_API_KEY_SHA256 or "").strip()

    if not expected_hash:
        if not settings.is_production:
            logger.warning("MASTER_API_KEY_SHA256 is not set. Bypassing API key check because not in production.")
            return None
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API key not configured")

    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-API-Key header")

    provided_hash = _sha256_hex(x_api_key)

    if not hmac.compare_digest(provided_hash.lower(), expected_hash.lower()):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")

    # Authenticated. Nothing to return; dependency success is enough.
    return None