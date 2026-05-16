import logging
import sys

def setup_enterprise_logging():
    """Configures structured, enterprise-grade logging for the application."""
    root_logger = logging.getLogger()
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(logging.INFO)

    # We use a standard Formatter here, but in production this would often be JSON
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "service": "OmniAgent", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    return root_logger

# Initialize on import
setup_enterprise_logging()
