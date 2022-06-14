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
import os

from rating_calculator import CodeforcesRatingCalculator

class NoRatingChangesError(Exception):
    pass

def get_results(url, print=None):
    if print is None:
        print = lambda s: s
    while True:
        print("fetching ... {}".format(url))
        res = req.get(url)
        content = json.loads(res.content)
        print("fetching {} {}".format(content["status"], url))
        sleep(0.2)
        if content["status"] == "OK":
            return content["result"]
        elif content["comment"] == "contestId: Rating changes are unavailable for this contest":
            raise NoRatingChangesError(url)
        else:
            sleep(0.5)
            print("retrying")
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

def get_submissions(handle):
    url = "https://codeforces.com/api/user.status?handle={}&from=1&count=1000000".format(handle)
    return get_results(url)

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

class RatingTracker:
    def __init__(self, handle):
        self.handle = handle
        rating_changes = self.get_rating_changes_for_user()
        self.ratings = [
            (int(rt["ratingUpdateTimeSeconds"]), int(rt["newRating"]))
            for rt in rating_changes
        ]
        self.ratings.sort()

    def get_rating_changes_for_user(self):
        url = "https://codeforces.com/api/user.rating?handle={}".format(self.handle)
        return get_results(url)

    def get_rating_at_time(self, sec):
        if len(self.ratings) == 0: return 1500
        if sec < self.ratings[0][0]: return 1500
        for i in range(len(self.ratings) - 1):
            if self.ratings[i][0] <= sec < self.ratings[i+1][0]:
                return self.ratings[i][1]
        return self.ratings[-1][1]

class UserPerformanceCalculator:

    def __init__(self, handle, print=None):
        self.handle = handle
        self.print = print
        self.rating_tracker = RatingTracker(self.handle)

    def get_results(self, url):
        return get_results(url, self.print)

    def get_rating_changes(self, contest_id):
        url = "https://codeforces.com/api/contest.ratingChanges?contestId={}".format(contest_id)
        return self.get_results(url)

    def get_standings(self, contest_id):
        url = "https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1000000&showUnofficial=true".format(contest_id)
        results = self.get_results(url)
        return results["contest"], results["problems"], results["rows"]

    def get_ratedlist(self):
        url = "https://codeforces.com/api/user.ratedList?activeOnly=true&includeRetired=false"
        return self.get_results(url)

    def get_performance(self, contest_id):
        contest, problems, standings = self.get_standings(contest_id)
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
                if handle == self.handle:
                    start_time = int(stand["party"]["startTimeSeconds"])
                    rating = self.rating_tracker.get_rating_at_time(start_time)
                    contestants[handle] = [handle, points, penalty, rating]
                    participation_type = type
                    rank = stand["rank"]

        rating_changes = None
        try:
            rating_changes = self.get_rating_changes(contest_id) # this fails for old/unusual contests
        except NoRatingChangesError:
            # unrated or old contest
            return {
                "contest_id" : contest_id,
                "contest_name" : contest["name"],
                "handle" : self.handle,
                "points" : contestants[self.handle][1],
                "penalty" : contestants[self.handle][2],
                "rating" : contestants[self.handle][3],
                "rank" : rank,
                "delta" : "unknown",
                "performance" : "unknown",
                "participation_type" : participation_type.lower(),
                "result_status" : "unrated/old/unusual",
            }

        result_status = None
        if len(rating_changes) == 0: # if a contest has just ended
            result_status = "just_ended"
            ratings = self.get_ratedlist() # we assume their current rating was used during the contest
            for user in ratings:
                handle = user["handle"]
                if handle in contestants:
                    contestants[handle][3] = user["rating"]
            # then remove people who participated for the first time
            handles_to_include = [self.handle]
            for handle in contestants:
                if contestants[handle][3] != 1e100:
                    handles_to_include.append(handle)
            new_contestants = {}
            for handle in handles_to_include:
                new_contestants[handle] = contestants[handle]
            contestants = new_contestants
        else:
            result_status = "normal"
            handles_to_include = [self.handle]
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

        assert(self.handle in contestants)
        for handle in contestants:
            assert(contestants[handle][0] == handle)
            assert(contestants[handle][1] != 1e100)
            assert(contestants[handle][2] != 1e100)
            assert(contestants[handle][3] != 1e100)

        calculator = CodeforcesRatingCalculator(contestants.values())
        rated_contestants = calculator.contestants
        rated_contestants.sort(key=lambda con: con.rank)
        for con in rated_contestants:
            if con.party == self.handle:
                return {
                    "contest_id" : contest_id,
                    "contest_name" : contest["name"],
                    "handle" : self.handle,
                    "points" : con.points,
                    "penalty" : con.penalty,
                    "rating" : con.rating,
                    "rank" : rank,
                    "delta" : con.delta,
                    "performance" : con.rating + con.delta * 4,
                    "participation_type" : participation_type.lower(),
                    "result_status" : result_status,
                }
        assert(False);

    def get_performance_cached(self, contest_id):
        cache_dir=os.path.expanduser("~/.cache/cftools/virtual_rating")
        os.makedirs(cache_dir, exist_ok=True)
        cache_file="{}/cache.json".format(cache_dir)
        res = None
        data = None
        if os.path.exists(cache_file):
            with open(cache_file, "r") as file:
                data = json.load(file)
                if self.handle in data and str(contest_id) in data[self.handle]:
                    res = data[self.handle][str(contest_id)]
        if res is None:
            res = self.get_performance(contest_id)
        if data is None:
            data = {}
        if self.handle not in data:
            data[self.handle] = {}
        data[self.handle][str(contest_id)] = res
        if res["result_status"] != "just_ended":
            with open(cache_file, "w") as file:
                json.dump(data, file)
        return res

class CFColors:

    @staticmethod
    def get_rating_color(rating):
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

    @staticmethod
    def get_participation_type_color(type):
        return "#11ff00" if type == "contestant" else ("#e5ff00" if type == "virtual" else "#9dff00")

    @staticmethod
    def get_delta_color(delta):
        return "white" if type(delta) == str else ("#ff0008" if delta < 0 else ("#15ff00" if delta > 0 else "white"))
