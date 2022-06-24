#!/bin/bash

BIN=$(realpath -s ./bin)
DIST=$(realpath -s ./_dist_windows)
SPECS=$(realpath -s ./_specs_windows)
BUILD=$(realpath -s ./_build_windows)

mkdir -p $BIN

function setup_wine {
    # install wine
    # install winetricks
    # run "winetricks win10"
    # download at python installation https://www.python.org/downloads/windows/
    # should probably be installed for all users
    # run "wine "<python-installation-file>"
    pipenv requirements > requirements.txt
    wine pip install -r requirements.txt
}

function pyinstall {
    wine pyinstaller --distpath $DIST --workpath $BUILD --specpath $SPECS -F -p ./src $@
}

function python_build {
    pyinstall -n $1 src/scripts/$2
}

# setup wine
setup_wine

# scripts windows 
python_build dailyacs DailyACs/main.py
python_build comuaccount ComuACCount/main.py
python_build rangerank RangeRank/main.py
python_build virtualperformance VirtualPerformance/main.py
python_build unsolvedcontestproblems UnsolvedContestProblems/main.py
python_build whatif WhatIf/main.py

# cfscripts windows
pyinstall -n cfscripts ./src/main.py
cp $DIST/cfscripts.exe $BIN/cfscripts.exe
