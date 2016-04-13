#!/usr/bin/env bash

# Script to run the chatbot and auto-restart it if it crashes.case

# Note: this requires all startup information to be passed in arguments
# or Config.py.
# If the above criteria are not fulfilled, the chatbot will have to request
# startup information when it starts, and then it will also do so when
# restarting when it crashes, which defeats the purpose of this file.

stoprunning=0
firststart=1
ec=0
while [ "$stoprunning" -eq "0" ]
do
    if [ "$firststart" -eq "1" ]
    then
        python3 main.py "$@"
    elif [ "$firststart" -eq "0" ] && [ "$ec" -eq "1" ]
    then
        python3 main.py "$@" -m "Bot restarted after crash."
    elif [ "$firststart" -eq "0" ] && [ "$ec" -eq "2" ]
    then
        rev=git rev-parse HEAD
        python3 main.py "$@" -m "Bot restarted after pulling from the GitHub repository. Running on revision `$rev`."
    else
        python3 main.py "$@" -m "Bot restarted after terminating with an unrecognized status code."
    fi

    ec=$?

    if [ "$ec" -eq "0" ]
    then
        stoprunning=1
    elif [ "$ec" -eq "2" ]
    then
        git fetch origin master
        git merge origin/master --no-edit
        git submodule update --init --recursive
        firststart = 0
    else
        firststart=0
    fi
done