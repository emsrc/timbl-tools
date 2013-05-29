"""
Support for logging
"""

import logging

def file_logger(log_name, filename, mode="w", level=logging.DEBUG):
    """
    Convenience function to create a logger that writes to a file
    """
    formatter= logging.Formatter("#%(levelname)s - %(name)s - %(message)s")
    handler = logging.FileHandler(filename, mode=mode)
    handler.setFormatter(formatter)
    logger = logging.getLogger(log_name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger