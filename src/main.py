from os import system
from textwrap import wrap, dedent
from sys import exit

from scripts.ComuACCount.main import main as main_comuaccount
from scripts.DailyACs.main import main as main_dailyacs
from scripts.RangeRank.main import main as main_rangerank
from scripts.UnsolvedContestProblems.main import main as main_unsolvedcontestproblems
from scripts.VirtualPerformance.main import main as main_virtualperformance
from scripts.WhatIf.main import main as main_whatif

me="by William Bille Meyling (cf: WillTheBill, github: willthbill)"

# name
# function/command
# description
# credit
scripts = [
        (
            "Comulative AC count",
            main_comuaccount,
            """
            Count how many problems were solved since a specific date.
            """,
            me,
        ),
        (
            "Daily ACs",
            main_dailyacs,
            """
            Finds problems solved on each day along with their rating.
            """,
            me,
        ),
        (
            "Range rank",
            main_rangerank,
            """
            In an official contest, where did you rank among the contestants within a given rating range around your rating (the rating at the time of participating).
            """,
            me,
        ),
        (
            "Unsolved Contest Problems",
            main_unsolvedcontestproblems,
            """
            Find unsolved problems from contests with at least one submission. Why? Because you don't want to spoil nice unsolved virtuals. Handles div1/div2 contests where a problem occurs in both.
            """,
            me
        ),
        (
            "Virtual Performance",
            main_virtualperformance,
            "Calculate rank/delta/performance of virtual/unofficial/offical contests.",
            me
        ),
        (
            "What if?",
            main_whatif,
            """
            What If Codeforces virtual contests / unofficial participations were official? Calculates new ratings using deltas and simulates the past n contests.
            """,
            me
        ),
]

def main():

    print("Welcome to cfscripts - a collection of scripts for CodeForces")
    print("- created and maintained by", me)
    print()

    print("Choose a script")
    for i in range(len(scripts)):
        print("{}: {}".format(i + 1, scripts[i][0]))
    choice = int(input("Script number (1-{}): ".format(len(scripts))))
    assert(1 <= choice <= len(scripts))
    choice -= 1

    def print_script_info(script):
        firstline="============={}=============".format(script[0])
        print(firstline)
        print(*wrap(dedent(script[2]).strip(), 80), sep="\n")
        print("--------------")
        print(*wrap(dedent(script[3]).strip(), 80), sep="\n")
        print("=" * len(firstline))

    print()
    print_script_info(scripts[choice])
    print()

    program = scripts[choice][1]
    if type(program) == str:
        system(program)
    else:
        program()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        exit(1)
    exit(0)
