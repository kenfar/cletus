#!/usr/bin/env bash
#------------------------------------------------------------------------------
# The purpose of this script is to run the test_cletus_job.py
# program enough times to hopefully detect race conditions.
#
# It isn't intended to be automatically run by tox, or a ci tool.  Just run this
# from within the testing directory.
#
# See the file "LICENSE" for the full license governing use of this file.
#    Copyright 2013, 2014 Ken Farmer
#------------------------------------------------------------------------------


control_c()
{
    echo '****************************************'
    echo '           USER EXIT                    '
    echo '****************************************'
    exit
}


trap control_c SIGINT


COUNTER=0
while [ $COUNTER -lt 100 ]; do
    echo ========= COUNTER: $COUNTER ===============

    py.test -svx ./test_cletus_job.py
    if [ "$?" -ne "0" ]; then
        echo '****************************************'
        echo '           ERROR!!!!                    '
        echo '****************************************'
        exit
    fi

    let COUNTER=COUNTER+1
done
