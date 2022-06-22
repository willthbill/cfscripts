import datetime
from rich.table import Table
from rich.console import Group
from rich.live import Live
from rich.text import Text
from rich.prompt import IntPrompt, Prompt, Confirm
from rich import print
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../..")

from lib.performance import UserPerformanceCalculator
from lib.colors import CFColors
from lib.contests import get_contest_map, get_participated_contest_ids
from lib import printer
from lib.rating import RatingTracker

def set_status(status):
    if GROUP is None: return
    GROUP._renderables = [status, TABLE]
    GROUP._render = None

printer.PRINT=set_status

def get_table(handle):
    table=Table(
        title="CodeForces Rating Simulation for {}".format(handle),
        title_style="on_default",
        show_lines=True,
        highlight=True,
    )
    table.add_column("handle")
    table.add_column("contest name")
    table.add_column("contest id")
    table.add_column("participation type")
    table.add_column("participation time")
    table.add_column("rank")
    table.add_column("points | penalty")
    table.add_column("old rating")
    table.add_column("new rating")
    table.add_column("delta")
    table.add_column("performance")
    return table

def add_row(data):
    performance_color = CFColors.get_rating_color(data["performance"])
    old_rating_color = CFColors.get_rating_color(data["old_rating"])
    new_rating_color = CFColors.get_rating_color(data["new_rating"])
    delta_color = CFColors.get_delta_color(data["delta"])
    participation_type_color = CFColors.get_participation_type_color(data["participation_type"])
    timestamp = datetime.utcfromtimestamp(data["time"]).strftime('%Y-%m-%d %H:%M:%S')
    TABLE.add_row(
        data["handle"],
        data["contest"],
        str(data['contest_id']),
        Text(data["participation_type"], style=participation_type_color),
        timestamp,
        str(data["rank"]),
        "{} | {}".format(data["points"],data["penalty"]),
        Text(str(data["old_rating"]), style=old_rating_color),
        Text(str(data["new_rating"]), style=new_rating_color),
        Text(str(data["delta"]), style=delta_color),
        Text(str(data["performance"]), style=performance_color),
    )

def main():
    global GROUP, TABLE

    GROUP = None

    handle = Prompt.ask("CodeForces handle")
    contest_ids = get_participated_contest_ids(handle)
    amount = IntPrompt.ask(
        "Amount of contests to go back (at most {})".format(len(contest_ids)),
        default=5,
        choices=list(map(str, range(1,len(contest_ids) + 1))),
        show_choices=False
    )
    only_positive = Confirm.ask(
        "Only include positive rating changes",
        default=False,
    )
    contest_ids = (contest_ids[-amount::])
    calculator = UserPerformanceCalculator(handle)
    tracker = RatingTracker(handle)
    old_rating = tracker.get_rating_at_time(contest_ids[0][1])
    contest_map = get_contest_map()
    calculator = UserPerformanceCalculator(handle)

    TABLE = get_table(handle)
    GROUP = Group("loading...", TABLE)

    with Live(GROUP, refresh_per_second=10, screen=False, transient=False, vertical_overflow="visible"):

        for contest_id, time in contest_ids:
            set_status("evaluating {} -- {} ...".format(contest_map[contest_id]["name"], contest_id))
            data = calculator.get_performance(contest_id, old_rating)
            new_rating = old_rating
            if type(data["delta"]) != str:
                if (not only_positive) or data["delta"] > 0:
                    new_rating = old_rating + data["delta"]
            data["old_rating"] = old_rating
            data["new_rating"] = new_rating
            data["time"] = time
            data["contest"] = contest_map[contest_id]["name"]
            add_row(data)
            old_rating = new_rating
        set_status("finished")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(1)
    sys.exit(0)
