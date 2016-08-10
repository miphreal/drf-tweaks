from datetime import datetime
from warnings import warn

from django.utils.timezone import localtime, now, utc


def finally_deprecated_on(when, message):
    """Util that allows to define a deprecation warning on logic that's going to be deprecated.
    It requires `when` date parameter (a day when something will be finally deprecated).
    `PendingDeprecationWarning` or `DeprecationWarning` will be generated depending on deprecation date.
    """

    deprecation_day = datetime.strptime(when, '%Y-%m-%d').replace(tzinfo=utc)
    category = PendingDeprecationWarning
    if deprecation_day <= now():
        category = DeprecationWarning

    warn(
        message,
        category,
        stacklevel=2
    )
