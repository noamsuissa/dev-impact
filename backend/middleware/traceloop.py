"""Traceloop middleware for observability of LLM calls through LiteLLM.
"""

import logging
import os

import litellm
from traceloop.sdk import Traceloop

logger = logging.getLogger(__name__)


def setup_traceloop() -> bool:
    """Initialize Traceloop observability for LiteLLM.

    Returns
    -------
        bool: True if setup was successful, False otherwise

    """
    # Check if API key is provided
    traceloop_api_key = os.getenv("TRACELOOP_API_KEY")
    if not traceloop_api_key:
        logger.debug("TRACELOOP_API_KEY not set - skipping traceloop initialization")
        return False

    try:
        # Initialize Traceloop
        Traceloop.init(
            api_key=traceloop_api_key,
            disable_batch=os.getenv("ENVIRONMENT", "").lower() == "development",
            app_name="dev-impact-api",
        )

        logger.info("Traceloop observability initialized successfully")

        # Set LiteLLM callbacks to send traces to Traceloop
        litellm.success_callback = ["otel"]
        litellm.failure_callback = ["otel"]

        logger.info("LiteLLM callbacks configured: success_callback=['otel'], failure_callback=['otel']")

        return True

    except ImportError:
        logger.error("Traceloop SDK not installed. Install it with: pip install traceloop-sdk")
        return False
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to initialize Traceloop: %s", e, exc_info=True)
        return False
