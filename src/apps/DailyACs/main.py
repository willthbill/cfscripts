import requests as req
import json
import datetime
import sys

def main():
    handle = input("CodeForces handle: ")
    url = "https://codeforces.com/api/user.status?handle={}".format(handle)
    response = req.get(url)
    subs = json.loads(response.content)["result"][::-1]
    problems = {} 
    for sub in subs:
        problem = str(sub["problem"]["contestId"]) + sub["problem"]["index"]
        if sub["verdict"] == "OK" and problem not in problems:
            problems[problem] = sub["problem"]
            problems[problem]["time"] = int(sub["creationTimeSeconds"])
    days = {}
    for problemID in problems:
        problem = problems[problemID]
        date = datetime.datetime.fromtimestamp(problem["time"])
        newtime = problem["time"] - date.hour * 60 * 60 - date.minute * 60 - date.second
        if newtime not in days: days[newtime] = []
        days[newtime].append(problem)
    for day in days:
        probs = days[day]
        date = datetime.datetime.fromtimestamp(day)
        print(date.strftime('%b/%d/%Y')+":", len(probs))
        for problem in probs:
            print("    -", str(problem["rating"]if "rating" in problem else "unrated")+": ", str(problem["contestId"])+problem["index"], problem["name"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(1)
    sys.exit(0)
