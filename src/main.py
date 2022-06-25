from os import system
from textwrap import wrap, dedent
from sys import exit

me="by William Bille Meyling (cf: WillTheBill, github: willthbill)"

def comuaccount():
    import scripts.ComuACCount.main
    scripts.ComuACCount.main.main()

def dailyacs():
    import scripts.DailyACs.main
    scripts.DailyACs.main.main()

def rangerank():
    import scripts.RangeRank.main
    scripts.RangeRank.main.main()

def unsolvedcontestproblems():
    import scripts.UnsolvedContestProblems.main
    scripts.UnsolvedContestProblems.main.main()

def virtualperformance():
    import scripts.VirtualPerformance.main
    scripts.VirtualPerformance.main.main()

def whatif():
    import scripts.WhatIf.main
    scripts.WhatIf.main.main()

# name
# function/command
# description
# credit
script_configs = [
        (
            "Comulative AC count",
            comuaccount,
            """
            Count how many problems were solved since a specific date.
            """,
            me,
        ),
        (
            "Daily ACs",
            dailyacs,
            """
            Finds problems solved on each day along with their rating.
            """,
            me,
        ),
        (
            "Range rank",
            rangerank,
            """
            In an official contest, where did you rank among the contestants within a given rating range around your rating (the rating at the time of participating).
            """,
            me,
        ),
        (
            "Unsolved Contest Problems",
            unsolvedcontestproblems,
            """
            Find unsolved problems from contests, where you have made at least one submission in the contest. Why? Because you don't want to spoil nice unsolved virtuals, when you just solve problems from the problemset. It handles div1/div2 contests where a problem occurs in both.
            """,
            me
        ),
        (
            "Virtual Performance",
            virtualperformance,
            "Calculate rank/delta/performance of virtual/unofficial/official contests.",
            me
        ),
        (
            "What if?",
            whatif,
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
    for i in range(len(script_configs)):
        print("{}: {}".format(i + 1, script_configs[i][0]))
    choice = int(input("Script number (1-{}): ".format(len(script_configs))))
    assert(1 <= choice <= len(script_configs))
    choice -= 1

    def print_script_info(script):
        firstline="============={}=============".format(script[0])
        print(firstline)
        print(*wrap(dedent(script[2]).strip(), 80), sep="\n")
        print("--------------")
        print(*wrap(dedent(script[3]).strip(), 80), sep="\n")
        print("=" * len(firstline))

    print()
    print_script_info(script_configs[choice])
    print()

    program = script_configs[choice][1]
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
