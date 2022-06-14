import json
import os

from .rating import RatingTracker, get_rating_changes_for_contest, get_ratedlist
from .api import NoRatingChangesError
from .contests import get_standings
from .rating_calculator import CodeforcesRatingCalculator

class UserPerformanceCalculator:

    def __init__(self, handle):
        self.handle = handle
        self.rating_tracker = RatingTracker(self.handle)

    def get_performance(self, contest_id):
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
                if handle == self.handle:
                    start_time = int(stand["party"]["startTimeSeconds"])
                    rating = self.rating_tracker.get_rating_at_time(start_time)
                    contestants[handle] = [handle, points, penalty, rating]
                    participation_type = type
                    rank = stand["rank"]

        rating_changes = None
        try:
            rating_changes = get_rating_changes_for_contest(contest_id) # this fails for old/unusual contests
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
            ratings = get_ratedlist() # we assume their current rating was used during the contest
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
