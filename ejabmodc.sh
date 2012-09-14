#!/bin/sh

## A script for compiling an ejabberd module in the current dir and
## moving beam file to ebin dir of ejabberd installation

## A few points:
## 
## - This is for personal use hence the hard coded paths.## 
## - Before using this script with an existing ejabberd module, first
##   check if the directory has it's own build.sh file and use it
##   instead if it exists.

INCLUDEDIR=/lib/ejabberd/include
SRCDIR=/home/vineet/erlang/ejabberd-2.1.11/src
EBINDIR=/lib/ejabberd/ebin

filename=`basename $1`
module="${filename%.*}"

erlc -I $INCLUDEDIR -pa $SRCDIR $1
sudo mv $module.beam $EBINDIR

