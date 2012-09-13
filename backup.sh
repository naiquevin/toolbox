#!/bin/bash

# Script for taking backup of files and directories scattered in
# various places.
# 
# usage:
# 
# create a txt file named tobackup.txt with list of paths to be backed up
# run $ backup.sh
# a directory "backup_<todays_date>" will be created in pwd
# 
# Example backup.sh file for backing up files and dirs created when
# ejabberd is installed
# 
# /etc/ejabberd
# /usr/lib/ejabberd
# /usr/sbin/ejabberd
# /usr/share/doc/ejabberd
# /var/lib/ejabberd
# /var/log/ejabberd

pre="backup_"
dt=`date +'%m-%d-%Y'`
bdir=`echo $pre$dt`
`mkdir $bdir`
for f in `cat tobackup.txt`
do
    tdir=`echo "$f" | sed -e "s/^\/*//"`
    tdirname=`dirname $tdir`
    `mkdir -p $bdir/$tdirname`
    `cp -r $f ./$bdir/$tdirname/`
done
