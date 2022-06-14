import requests as req
import json
import datetime
handle = input("Codeforces handle: ")
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
commu = []
daynames = []
for day in days:
    probs = days[day]
    date = datetime.datetime.fromtimestamp(day)
    print(date.strftime('%b/%d/%Y')+":", len(probs))
    commu.append(len(probs))
    daynames.append(date)
    for problem in probs:
        print("    -", str(problem["rating"]if "rating" in problem else "unrated")+": ", str(problem["contestId"])+problem["index"], problem["name"])
for i in range(len(commu)-2,-1,-1):
    commu[i] += commu[i+1] 
print("\nCommulative problem count\n")
for i in range(len(commu)):
    print("Since", daynames[i].strftime('%b/%d/%Y'), commu[i], "problems were solved")
