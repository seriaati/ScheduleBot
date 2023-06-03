import datetime

from pytz import timezone


def get_dt_now() -> datetime.datetime:
    """
    This function returns the current datetime with the timezone set to "Asia/Taipei".

    Returns:
        datetime.datetime: The current datetime with the timezone set to "Asia/Taipei".
    """
    return datetime.datetime.now(tz=timezone("Asia/Taipei"))
