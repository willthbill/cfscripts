from .api import get_results

from urllib.parse import quote_plus

# TODO: use urllib everywhere

def get_submissions(handle):
    url = "https://codeforces.com/api/user.status?handle={}&from=1&count=1000000".format(handle)
    return get_results(url, 1)

def get_submissions_for_contest(contest_id, handle=None):
    if handle is None:
        url = "https://codeforces.com/api/contest.status?contestId={}".format(
            quote_plus(str(contest_id)),
        )
    else:
        url = "https://codeforces.com/api/contest.status?contestId={}&handle={}".format(
            quote_plus(str(contest_id)),
            quote_plus(str(handle))
        )
    return get_results(url, 1)
