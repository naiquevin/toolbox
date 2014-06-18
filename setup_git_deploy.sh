#!/bin/bash

# todo: make configurable via cli args and options

REMOTE_NAME=production
TRACKING_BRANCH='track-production'
REMOTE_URL=$1

git checkout -b $TRACKING_BRANCH
git remote add $REMOTE_NAME $REMOTE_URL
git config branch.$TRACKING_BRANCH.remote $REMOTE_NAME
git config branch.$TRACKING_BRANCH.merge refs/heads/master
git config remote.$REMOTE_NAME.push refs/heads/$TRACKING_BRANCH:master
echo "Configuration for git based deployment done!"
git checkout master
