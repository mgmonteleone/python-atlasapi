from isodate import Duration, duration_isoformat


class AtlasGranularities(object):
    """Helper class to create ISO 8601 durations to pass to the API

    To add more possible granularities, add them here.

    """
    MINUTE = duration_isoformat(Duration(minutes=1))
    FIVE_MINUTE = duration_isoformat(Duration(minutes=5))
    HOUR = duration_isoformat(Duration(hours=1))
    DAY = duration_isoformat(Duration(days=1))


class AtlasPeriods(object):
    """Helper class to create ISO 8601 durations to send to the Atlas period parameter.

    To add more periods, add them here.


    """
    HOURS_1 = duration_isoformat(Duration(hours=1))
    HOURS_8 = duration_isoformat(Duration(hours=8))
    HOURS_24 = duration_isoformat(Duration(hours=24))
    HOURS_48 = duration_isoformat(Duration(hours=48))
    WEEKS_1 = duration_isoformat(Duration(weeks=1))
    MONTHS_1 = duration_isoformat(Duration(months=1))
    MONTHS_2 = duration_isoformat(Duration(months=2))
    YEARS_1 = duration_isoformat(Duration(years=1))
    YEARS_2 = duration_isoformat(Duration(years=2))




print(AtlasPeriods.MONTHS_2)