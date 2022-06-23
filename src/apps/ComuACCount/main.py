from requests import get as req_get
from json import loads
from datetime import datetime
from sys import exit

def main():
    handle = input("CodeForces handle: ")
    url = "https://codeforces.com/api/user.status?handle={}".format(handle)
    response = req_get.get(url)
    subs = loads(response.content)["result"][::-1]
    problems = {} 
    for sub in subs:
        problem = str(sub["problem"]["contestId"]) + sub["problem"]["index"]
        if sub["verdict"] == "OK" and problem not in problems:
            problems[problem] = sub["problem"]
            problems[problem]["time"] = int(sub["creationTimeSeconds"])
    days = {}
    for problemID in problems:
        problem = problems[problemID]
        date = datetime.fromtimestamp(problem["time"])
        newtime = problem["time"] - date.hour * 60 * 60 - date.minute * 60 - date.second
        if newtime not in days: days[newtime] = []
        days[newtime].append(problem)
    comu = []
    daynames = []
    for day in days:
        probs = days[day]
        date = datetime.fromtimestamp(day)
        comu.append(len(probs))
        daynames.append(date)
    for i in range(len(comu)-2,-1,-1):
        comu[i] += comu[i+1] 
    print("\nProblem solutions comulative count\n")
    for i in range(len(comu)):
        print("Since", daynames[i].strftime('%b/%d/%Y'), comu[i], "problems were solved")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(1)
    exit(0)
