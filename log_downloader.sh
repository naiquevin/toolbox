#!/bin/bash

## A utility script to download log files from the remote server. All
## log files will be downloaded to the logdir directory defined below
## so make sure it's configured as per your preferences. No need to
## create the dir, the script will take care of that
##
## Author: Vineet Naik <naikvin@gmail.com>
##
## Usage:
##
## $ ./log_downloader.sh -a myapp
##                       -r myuser@myserver
##                       -p /home/myuser/myapp/log
##
## All files matching wildcard pattern *.log* will be downloaded at:
##
## $logdir
##  |- myuser@myserver
##      |- myapp
##          |- logs_<date>-<hour>
##

## Todo: Add command to display help/usage

logdir='/home/vineet/errorlogs2'

while [ "$1" != "" ]; do
    case $1 in
        -a | --app )       shift
                           app=$1
                           ;;
        -r | --remote )    shift
                           remote=$1
                           ;;
        -p | --path )      shift
                           path=$1
    esac
    shift
done

remotepath=$remote:$path

targetpath=$logdir/$remote/$app/logs_`date +'%m-%d-%Y-%H'`

mkdir -p $targetpath

scp $remotepath/"*.log*" $targetpath

echo "Log files downloaded to, " $targetpath
