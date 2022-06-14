from time import sleep
import json
import requests as req

from . import printer

class NoRatingChangesError(Exception):
    pass

def get_results(url):
    while True:
        printer.PRINT("fetching ... {}".format(url))
        res = req.get(url)
        content = json.loads(res.content)
        printer.PRINT("fetching {} {}".format(content["status"], url))
        if printer.PRINT is not None: sleep(0.2)
        if content["status"] == "OK":
            return content["result"]
        elif content["comment"] == "contestId: Rating changes are unavailable for this contest":
            raise NoRatingChangesError(url)
        else:
            if printer.PRINT is not None: sleep(0.5)
            printer.PRINT("retrying")
            if printer.PRINT is not None: sleep(0.5)
