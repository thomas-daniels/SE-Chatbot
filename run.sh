#!/usr/bin/env bash

# Script to run the chatbot and auto-restart it if it crashes.case

# Note: this requires all startup information to be passed in arguments
# or Config.py.
# If the above criteria are not fulfilled, the chatbot will have to request
# startup information when it starts, and then it will also do so when
# restarting when it crashes, which defeats the purpose of this file.

stoprunning=0
firststart=1
while [ "$stoprunning" -eq "0" ]
do
    if [ "$firststart" -eq "1" ]
    then
        python3 main.py "$@"
    else
        python3 main.py "$@" -m "Bot restarted after crash."
    fi

    ec=$?

    if [ "$ec" -eq "0" ]
    then
        stoprunning=1
    else
        firststart=0
    fi
done