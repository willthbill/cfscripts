import requests as req
import json
handle = input("Codeforces handle: ")
contestID = input("Contest ID: ")
rankrange = int(input("Rank range (0-10000): "))
url = "https://codeforces.com/api/contest.ratingChanges?contestId={}".format(contestID) 
response = req.get(url)
contestants = json.loads(response.content)["result"]
goal_rating = -1 
for contestant in contestants:
    if contestant["handle"] == handle:
        goal_rating = contestant["oldRating"]
        break
if goal_rating == -1:
    print("Invalid input")
    exit(0)
relevants = []
for contestant in contestants:
    rating = contestant["oldRating"] 
    if abs(rating - goal_rating) <= rankrange: 
        relevants.append(contestant)
for i, rel in enumerate(relevants[::-1]):
    print(len(relevants) - i, ": ", rel["handle"], "@", rel["oldRating"], "(actual rank:", str(rel["rank"])+")","  -->  ",rel["newRating"])
rank = -1
for i, rel in enumerate(relevants):
    if rel["handle"] == handle:
        rank = i + 1
print()
print("Showing results for", handle, "in", relevants[0]["contestName"], "(id: {})".format(contestID))
print("Your rating:", goal_rating)
print("New rating:", relevants[rank-1]["newRating"])
print("Compared to rating within the range: [{},{}]".format(goal_rating - rankrange, goal_rating + rankrange))
print("Rank: ", rank, " / ", len(relevants))
print()

