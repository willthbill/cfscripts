from urllib.parse import quote_plus

from .api import get_results

class RatingTracker:
    def __init__(self, handle):
        self.handle = handle
        rating_changes = get_rating_changes_for_user(self.handle)
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

def get_rating_changes_for_contest(contest_id):
    url = "https://codeforces.com/api/contest.ratingChanges?contestId={}".format(
        quote_plus(str(contest_id))
    )
    return get_results(url, 2)

def get_rating_changes_for_user(handle):
    url = "https://codeforces.com/api/user.rating?handle={}".format(
        quote_plus(str(handle)),
    )
    return get_results(url, 1)

def get_ratedlist():
    url = "https://codeforces.com/api/user.ratedList?activeOnly=true&includeRetired=false"
    return get_results(url, 1)
