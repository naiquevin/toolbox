#!/bin/sh

BASEDIR=$(dirname $0)
PWD=`pwd`


while [ "$1" != "" ]; do
    case $1 in
        basehtml ) cp $BASEDIR/base.html $PWD/$2
                   ;;
    esac
    shift
done



