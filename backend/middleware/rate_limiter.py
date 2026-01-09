"""Rate limiter middleware for FastAPI using slowapi."""

import logging
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)


def validate_rate_limit_string(rate_limit_str: str) -> list:
    """Validate rate limit string format and return list of limits.
    Format should be like "100/minute,1000/hour"

    Args:
    ----
        rate_limit_str: Comma-separated rate limits

    Returns:
    -------
        List of validated rate limit strings

    """
    if not rate_limit_str:
        return ["100/minute", "1000/hour"]

    limits = []
    for limit in rate_limit_str.split(","):
        limit = limit.strip()
        if not limit:
            continue

        # Validate format: number/unit
        parts = limit.split("/")
        if len(parts) != 2:
            logger.warning("Invalid rate limit format: %s, skipping", limit)
            continue

        try:
            count = int(parts[0])
            unit = parts[1].strip().lower()

            # Validate unit is one of the supported units
            valid_units = ["second", "minute", "hour", "day"]
            if unit not in valid_units and unit not in [u + "s" for u in valid_units]:
                logger.warning("Invalid rate limit unit: %s, skipping limit: %s", unit, limit)
                continue

            if count <= 0:
                logger.warning("Rate limit count must be positive: %s, skipping limit: %s", count, limit)
                continue

            limits.append(limit)
        except ValueError:
            logger.warning("Invalid rate limit count: %s, skipping limit: %s", parts[0], limit)
            continue

    # Fallback to defaults if no valid limits found
    if not limits:
        logger.warning("No valid rate limits found, using defaults: 100/minute,1000/hour")
        return ["100/minute", "1000/hour"]

    return limits


# Suppress threading errors from slowapi that can cause OverflowError
# This is a workaround for a known issue in slowapi where invalid timestamps
# can be passed to threading.Timer, causing OverflowError
def handle_threading_exception(args):
    """Handle exceptions in threads to prevent crashes"""
    # args is a threading.ExceptHookArgs named tuple
    exc_type = args.exc_type
    exc_value = args.exc_value
    exc_traceback = args.exc_traceback
    thread = args.thread

    # Only log non-OverflowError exceptions or OverflowErrors that aren't from slowapi timers
    # OverflowError from slowapi timers are expected and can be safely ignored
    if exc_type is OverflowError and "timestamp out of range" in str(exc_value):
        logger.debug("Ignoring slowapi threading OverflowError in thread %s: %s", thread.name, exc_value)
        return

    # Log other threading errors
    logger.error(
        "Unhandled exception in thread %s: %s: %s",
        thread.name,
        exc_type.__name__,
        exc_value,
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def setup_rate_limiter() -> Limiter | None:
    """Initialize rate limiter with configuration from environment.

    Returns
    -------
        Limiter instance or None if initialization fails

    """
    rate_limit_str = os.getenv("RATE_LIMIT_DEFAULT_LIMITS", "100/minute,1000/hour")
    validated_limits = validate_rate_limit_string(rate_limit_str)
    logger.info("Rate limiter configured with limits: %s", validated_limits)

    try:
        limiter = Limiter(key_func=get_remote_address, default_limits=validated_limits)
        return limiter
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to initialize rate limiter: %s, continuing without rate limiting", e)
        return None
