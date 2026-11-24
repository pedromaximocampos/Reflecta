class ShareUnavailable(Exception):
    """A share or its source is unavailable to the current actor."""


class ShareIneligible(Exception):
    """The source exists but does not satisfy sharing invariants."""


class ActivityLimitReached(Exception):
    """The shared access has reached its professional guidance limit."""


class ProfessionalActivityNotFound(Exception):
    """The activity does not belong to the authenticated user."""
