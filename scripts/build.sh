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
    pyinstall -n $1 src/apps/$2
}

python_build dailyacs DailyACs/main.py
python_build comuaccount ComuACCount/main.py
python_build rangerank RangeRank/main.py
python_build virtualperformance VirtualPerformance/main.py
python_build unsolvedcontestproblems UnsolvedContestProblems/main.py
python_build whatif WhatIf/main.py

pyinstall \
    --add-binary $DIST/dailyacs:. \
    --add-binary $DIST/comuaccount:. \
    --add-binary $DIST/rangerank:. \
    --add-binary $DIST/virtualperformance:. \
    --add-binary $DIST/unsolvedcontestproblems:. \
    --add-binary $DIST/whatif:. \
    -n cftools ./src/main.py

mkdir -p $BIN

cp $DIST/cftools $BIN/cftools
