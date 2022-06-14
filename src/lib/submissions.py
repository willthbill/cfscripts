from .api import get_results

def get_submissions(handle):
    url = "https://codeforces.com/api/user.status?handle={}&from=1&count=1000000".format(handle)
    return get_results(url)
