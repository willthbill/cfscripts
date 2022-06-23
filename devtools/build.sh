#!/bin/bash

DIST=$(realpath -s ./_dist)
BIN=$(realpath -s ./bin)
SPECS=$(realpath -s ./_specs)
BUILD=$(realpath -s ./_build)

mkdir -p $DIST

function pyinstall {
    pyinstaller --distpath $DIST --workpath $BUILD --specpath $SPECS -F -p ./src $@
}

function python_build {
    pyinstall -n $1 src/scripts/$2
}

# scripts
python_build dailyacs DailyACs/main.py
python_build comuaccount ComuACCount/main.py
python_build rangerank RangeRank/main.py
python_build virtualperformance VirtualPerformance/main.py
python_build unsolvedcontestproblems UnsolvedContestProblems/main.py
python_build whatif WhatIf/main.py

# cfscripts
pyinstall -n cfscripts ./src/main.py

mkdir -p $BIN

cp $DIST/cfscripts $BIN/cfscripts
