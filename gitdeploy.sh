#!/bin/bash

usage () {
    echo "Usage: ./gitdeploy.sh <tracking_branch> <remote_name> <remote_url>"
}


if [ "$1" = "-h" ] || [ "$1" = "--help" ]
then
    usage
    exit
fi


if [ "$1" = "" ] || [ "$2" = "" ] || [ "$3" = "" ]
then
    usage
    exit 1
fi


tracking_branch=$1
remote_name=$2
remote_url=$3


git branch $tracking_branch
git checkout $tracking_branch
git remote add $remote_name $remote_url
git config branch.$tracking_branch.remote $remote_name
git config branch.$tracking_branch.merge refs/heads/master
git config remote.$remote_name.push refs/heads/$tracking_branch:master
