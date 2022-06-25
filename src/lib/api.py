from time import sleep
import json
from requests_cache.session import CachedSession
import requests_cache
import requests as req

from . import printer

_long_session = CachedSession(
    'cf-cache-long',
    backend='filesystem',
    use_cache_dir=True,                # Save files in the default user cache dir
    # cache_control=True,                # Use Cache-Control headers for expiration, if available
    # ignored_parameters=['api_key'],  # TODO: use this if api is used I think
    match_headers=True,                # Match all request headers
)

_short_session = CachedSession(
    'cf-cache-short',
    backend='filesystem',
    use_cache_dir=True,                # Save files in the default user cache dir
    # cache_control=True,                # Use Cache-Control headers for expiration, if available
    # ignored_parameters=['api_key'],  # TODO: use this if api is used I think
    match_headers=True,                # Match all request headers
    expire_after=120 # 2 minutes
)

class NoRatingChangesError(Exception):
    pass

def get_results(url, cache_type=0):
    while True:
        printer.PRINT("fetching ... {}".format(url))

        res = None
        if cache_type == 0:
            with requests_cache.disabled():
                res = req.get(url)
        elif cache_type == 1:
            res = _short_session.get(url)
        else:
            res = _long_session.get(url)

        try:
            content = json.loads(res.content)
        except json.decoder.JSONDecodeError:
            sleep(0.5)
            printer.PRINT("retrying")
            sleep(0.5)
            continue

        printer.PRINT("fetching {} {}".format(content["status"], url))

        if printer.PRINT is not None: sleep(0.2)
        if content["status"] == "OK":
            return content["result"]
        elif content["comment"] == "contestId: Rating changes are unavailable for this contest":
            raise NoRatingChangesError(url)
        else:
            sleep(0.5)
            printer.PRINT("retrying")
            sleep(0.5)
