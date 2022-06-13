import requests as req
import json
import datetime
from rich.table import Table
from rich.console import Group
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.layout import Layout
from datetime import datetime
from time import sleep
import sys

from rating_calculator import CodeforcesRatingCalculator

class NoRatingChangesError(Exception):
    pass

def set_status(status):
    if GROUP is None: return
    GROUP._renderables = [status, TABLE]
    GROUP._render = None

def get_results(url):
    while True:
        set_status("fetching ... {}".format(url))
        res = req.get(url)
        content = json.loads(res.content)
        set_status("fetching {} {}".format(content["status"], url))
        sleep(0.2)
        if content["status"] == "OK":
            return content["result"]
        elif content["comment"] == "contestId: Rating changes are unavailable for this contest":
            raise NoRatingChangesError(url)
        else:
            sleep(0.5)
            set_status("retrying")
            sleep(0.5)

def get_contests():
    url="https://codeforces.com/api/contest.list?gym=false"
    return get_results(url)

def get_contest_map():
    contests = get_contests()
    mp = {}
    for contest in contests:
        mp[contest["id"]] = contest
    return mp

def get_rating_changes_for_user():
    url = "https://codeforces.com/api/user.rating?handle={}".format(HANDLE)
    return get_results(url)

class RatingTracker:
    def __init__(self):
        rating_changes = get_rating_changes_for_user()
        self.ratings = [
            (int(rt["ratingUpdateTimeSeconds"]), int(rt["newRating"]))
            for rt in rating_changes
        ]
        self.ratings.sort()

    def get_rating_at_time(self, sec):
        if len(self.ratings) == 0: return 1500
        if sec < self.ratings[0][0]: return 1500
        for i in range(len(self.ratings) - 1):
            if self.ratings[i][0] <= sec < self.ratings[i+1][0]:
                return self.ratings[i][1]
        return self.ratings[-1][1]

def get_submissions(handle):
    url = "https://codeforces.com/api/user.status?handle={}&from=1&count=1000000".format(handle)
    return get_results(url)

def get_participated_contest_ids():
    submissions = get_submissions(HANDLE)
    contest_ids = {}
    for submission in submissions:
        if "contestId" not in submission: continue;
        contest_id = submission["contestId"]
        type = submission["author"]["participantType"]
        if (type == "CONTESTANT" or type == "VIRTUAL" or type == "OUT_OF_COMPETITION") and contest_id in CONTEST_MP and len(submission["author"]["members"]) == 1:
            start_time = submission["author"]["startTimeSeconds"]# if "startTimeSeconds" in submission["author"] else 0
            contest_ids[contest_id] = start_time
    l = [(id, contest_ids[id]) for id in contest_ids]
    l.sort(key=lambda t: t[1])
    return l

def get_rating_changes(contest_id):
    url = "https://codeforces.com/api/contest.ratingChanges?contestId={}".format(contest_id)
    return get_results(url)

def get_standings(contest_id):
    url = "https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1000000&showUnofficial=true".format(contest_id)
    results = get_results(url)
    return results["contest"], results["problems"], results["rows"]

def get_ratedlist():
    url = "https://codeforces.com/api/user.ratedList?activeOnly=true&includeRetired=false"
    return get_results(url)

def get_performance(contest_id):
    contest, problems, standings = get_standings(contest_id)
    contestants = {}
    participation_type = None
    rank = None
    for stand in standings:
        type = stand["party"]["participantType"]
        if type == "PRACTICE": continue
        members = stand["party"]["members"] 
        if len(members) == 1:
            handle = members[0]["handle"]
            points = stand["points"]
            penalty = stand["penalty"]
            if type == "CONTESTANT":
                if handle not in contestants:
                    contestants[handle] = [handle, 1e100, 1e100, 1e100] # handle, points, penalty, rating
                contestants[handle][1] = points
                contestants[handle][2] = penalty
            if handle == HANDLE:
                start_time = int(stand["party"]["startTimeSeconds"])
                rating = RATING_TRACKER.get_rating_at_time(start_time)
                contestants[handle] = [handle, points, penalty, rating]
                participation_type = type
                rank = stand["rank"]

    rating_changes = None
    try:
        rating_changes = get_rating_changes(contest_id) # this fails for old/unusual contests
    except NoRatingChangesError:
        # unrated or old contest
        return {
            "contest_id" : contest_id,
            "contest_name" : contest["name"],
            "handle" : HANDLE,
            "points" : contestants[HANDLE][1],
            "penalty" : contestants[HANDLE][2],
            "rating" : contestants[HANDLE][3],
            "rank" : rank,
            "delta" : "unknown",
            "performance" : "unknown",
            "participation_type" : participation_type.lower(),
        }

    if len(rating_changes) == 0: # if a contest has just ended
        ratings = get_ratedlist() # we assume their current rating was used during the contest
        for user in ratings:
            handle = user["handle"]
            if handle in contestants:
                contestants[handle][3] = user["rating"]
        # then remove people who participated for the first time
        handles_to_include = [HANDLE]
        for handle in contestants:
            if contestants[handle][3] != 1e100:
                handles_to_include.append(handle)
        new_contestants = {}
        for handle in handles_to_include:
            new_contestants[handle] = contestants[handle]
        contestants = new_contestants
    else:
        handles_to_include = [HANDLE]
        for rt in rating_changes:
            handle = rt["handle"]
            if handle not in contestants: continue # some people are not in ranking but in rating change. Why is that?
            handles_to_include.append(handle)
            rating = rt["oldRating"]
            contestants[handle][3] = rating
        new_contestants = {}
        for handle in handles_to_include:
            new_contestants[handle] = contestants[handle]
        contestants = new_contestants

    assert(HANDLE in contestants)
    for handle in contestants:
        assert(contestants[handle][0] == handle)
        assert(contestants[handle][1] != 1e100)
        assert(contestants[handle][2] != 1e100)
        assert(contestants[handle][3] != 1e100)

    calculator = CodeforcesRatingCalculator(contestants.values())
    rated_contestants = calculator.contestants
    rated_contestants.sort(key=lambda con: con.rank)
    for con in rated_contestants:
        if con.party == HANDLE:
            return {
                "contest_id" : contest_id,
                "contest_name" : contest["name"],
                "handle" : HANDLE,
                "points" : con.points,
                "penalty" : con.penalty,
                "rating" : con.rating,
                "rank" : rank,
                "delta" : con.delta,
                "performance" : con.rating + con.delta * 4,
                "participation_type" : participation_type.lower(),
            }
    assert(False);

def get_color(rating):
    if type(rating) == str: return "grey"
    if rating < 1200: return "#a6a6a6"
    if rating < 1400: return "#69f562"
    if rating < 1600: return "#1cccd9"
    if rating < 1900: return "#0d7eff"
    if rating < 2100: return "#cc5ccc"
    if rating < 2300: return "#ffbb45"
    if rating < 2400: return "#e08e00"
    if rating < 2600: return "#ff1935"
    if rating < 3000: return "#ff1200"
    return "#8c0011"

def get_table():
    table=Table(
        title="CodeForces Participations of {}".format(HANDLE),
        title_style="on_default",
        show_lines=True,
        highlight=True,
    )
    table.add_column("contest name")
    table.add_column("contest id")
    table.add_column("participation type")
    table.add_column("participation time")
    table.add_column("handle")
    table.add_column("points | penalty")
    table.add_column("old rating")
    table.add_column("rank")
    table.add_column("predicted delta")
    table.add_column("predicted performance")
    return table

def add_row(data):
    performance_color = get_color(data["performance"])
    rating_color = get_color(data["rating"])
    delta_color = "white" if type(data["delta"]) == str else ("#ff0008" if data["delta"] < 0 else ("#15ff00" if data["delta"] > 0 else "white"))
    participation_type_color = "#15ff00" if data["participation_type"] == "contestant" else "#fffb00"
    timestamp = datetime.utcfromtimestamp(data["time"]).strftime('%Y-%m-%d %H:%M:%S')
    TABLE.add_row(
        data["contest_name"],
        str(data['contest_id']),# "https://codeforces.com/contest/{}".format(data["contest_id"]),
        Text(data["participation_type"], style=participation_type_color),
        Text(timestamp),
        Text(data["handle"], style=rating_color),
        "{} | {}".format(data["points"],data["penalty"]),
        Text(str(data["rating"]), style=rating_color),
        str(data["rank"]),
        Text(str(data["delta"]), style=delta_color),
        Text(str(data["performance"]), style=performance_color),
    )

def main():
    global GROUP, HANDLE, CONTEST_MP, RATING_TRACKER, TABLE
    GROUP = None
    HANDLE = Prompt.ask("Codeforces handle")
    CONTEST_MP = get_contest_map()
    contest_ids = get_participated_contest_ids()
    if Confirm.ask("Choose a specific contest?"):
        id = IntPrompt.ask("Contest ID")
        contestpair =  None
        for contest_id, time in contest_ids:
            if contest_id == id:
                contestpair = (contest_id, time)
                break
        if contestpair is None:
            print("Contest not found")
            exit(1)
        contest_ids = [contestpair]
    else:
        amount = IntPrompt.ask(
            "Amount of contests to query (at most {})".format(len(contest_ids)),
            default=5,
            choices=list(map(str, range(1,len(contest_ids) + 1))),
            show_choices=False
        )
        contest_ids = (contest_ids[-amount::])[::-1]
    RATING_TRACKER = RatingTracker()
    TABLE=get_table()
    GROUP = Group("loading...",TABLE)
    with Live(GROUP, refresh_per_second=10, screen=False, transient=False) as live:
        for contest_id, time in contest_ids:
            set_status("Calculating performance for {} -- {} ...".format(CONTEST_MP[contest_id]["name"], contest_id))
            data = get_performance(contest_id)
            data["time"] = time
            add_row(data)
        set_status("finished")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
    sys.exit(0)
