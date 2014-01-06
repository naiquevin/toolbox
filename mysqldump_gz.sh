#!/bin/bash

## A simple wrapper on top of the `mysqldump` command to quickly dump
## database tables in gzipped format. The target filename will be
## appended with the current date
##
## Usage: ./mysqldump_gz.sh -u <username>
##                          -p <password>
##                          -d <backupdir>
##                          -t <tablename>
##
## Typical usage: Add list of tablenames to be backed up in a file
## eg. `tables.txt` and then run the command using xargs,
##
##   $ cat tables.txt | xargs -n 1 ./mysqldump_gz.sh -u <..> -p <..> -d <..> -t 
##
## Todo: Add command to display help/usage
## 

while [ "$1" != "" ]; do
    case $1 in
        -u | --username )       shift
                                username=$1
                                ;;
        -p | --password )       shift
                                password=$1
                                ;;
        -t | --table )          shift
                                table=$1
                                ;;
        -d | --dir )            shift
                                backupdir=$1
    esac
    shift
done

backupfile=$backupdir/$table"_$(date +'%m-%d-%Y').sql.gz"

mysqldump -u $username -p$password $table | gzip > $backupfile


