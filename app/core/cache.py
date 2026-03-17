from cachetools import TTLCache

_seats_cache = TTLCache(maxsize=100, ttl=30)


def get_seats_cache():
    return _seats_cache
