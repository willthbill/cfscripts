import datetime
from rich.table import Table
from rich.console import Group
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, IntPrompt, Confirm
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../..")

from lib.performance import UserPerformanceCalculator
from lib.colors import CFColors
from lib.contests import get_contest_map, get_participated_contest_ids
from lib import printer

def set_status(status):
    if GROUP is None: return
    GROUP._renderables = [status, TABLE]
    GROUP._render = None

printer.PRINT=set_status

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
    performance_color = CFColors.get_rating_color(data["performance"])
    rating_color = CFColors.get_rating_color(data["rating"])
    delta_color = "white" if type(data["delta"]) == str else ("#ff0008" if data["delta"] < 0 else ("#15ff00" if data["delta"] > 0 else "white"))
    participation_type_color = "#11ff00" if data["participation_type"] == "contestant" else ("#e5ff00" if data["participation_type"] == "virtual" else "#9dff00")
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
    global GROUP, HANDLE, CONTEST_MP, TABLE

    GROUP = None
    HANDLE = Prompt.ask("Codeforces handle")
    CONTEST_MP = get_contest_map()
    contest_ids = get_participated_contest_ids(HANDLE)

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

    TABLE=get_table()
    GROUP = Group("loading...",TABLE)

    calculator = UserPerformanceCalculator(HANDLE)

    with Live(GROUP, refresh_per_second=10, screen=False, transient=False, vertical_overflow="visible"):
        for contest_id, time in contest_ids:
            set_status("Calculating performance for {} -- {} ...".format(CONTEST_MP[contest_id]["name"], contest_id))
            data = calculator.get_performance_cached(contest_id)
            data["time"] = time
            add_row(data)
        set_status("finished")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
    sys.exit(0)
