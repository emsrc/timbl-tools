"""
Timbl-tools exceptions
"""

class TimblToolsError(Exception):
    pass


class TimblServerError(TimblToolsError):
    pass


class TimblClientError(TimblToolsError):
    pass