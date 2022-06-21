from .api import get_results

def get_problems():
    url="https://codeforces.com/api/problemset.problems"
    result = get_results(url, 2)
    return result["problems"]
