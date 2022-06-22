from urllib.parse import quote_plus
import re

from .api import get_results
from .submissions import get_submissions

def get_contests():
    url="https://codeforces.com/api/contest.list?gym=false"
    return get_results(url, 1)

def get_contest_map():
    contests = get_contests()
    mp = {}
    for contest in contests:
        mp[contest["id"]] = contest
    return mp

def get_contest(contest_id):
    url = "https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1000000&showUnofficial=true".format(
        quote_plus(str(contest_id))
    )
    results = get_results(url, 1)
    return results["contest"]

def get_standings(contest_id):
    url = "https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1000000&showUnofficial=true".format(
        quote_plus(str(contest_id))
    )
    results = get_results(url, 1)
    return results["rows"]

def get_contest_problems(contest_id):
    url = "https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1000000&showUnofficial=true".format(
        quote_plus(str(contest_id))
    )
    results = get_results(url, 1)
    return results["problems"]

def get_participated_contest_ids(handle, contest_map=None):
    if contest_map is None:
        contest_map = get_contest_map()
    submissions = get_submissions(handle)
    contest_ids = {}
    for submission in submissions:
        if "contestId" not in submission: continue;
        contest_id = submission["contestId"]
        type = submission["author"]["participantType"]
        if (type == "CONTESTANT" or type == "VIRTUAL" or type == "OUT_OF_COMPETITION") and contest_id in contest_map and len(submission["author"]["members"]) == 1:
            start_time = submission["author"]["startTimeSeconds"]# if "startTimeSeconds" in submission["author"] else 0
            contest_ids[contest_id] = start_time
    l = [(id, contest_ids[id]) for id in contest_ids]
    l.sort(key=lambda t: t[1])
    return l

def get_contest_number(contest_name):
    res = re.findall(r'#(\d+)', contest_name)
    if len(res) == 0: return None
    if len(res) != 1: return None
    return int(res[0])
