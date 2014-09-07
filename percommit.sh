#!/usr/bin/env bash


function usage () {
    echo "Usage: $0 <command to run>"
    echo "Info: The provided command will be run against all git branches"
    echo "      by which the local branch is ahead of the remote branch"
    echo "Example: $ $0 \"lein do clean, compile\""
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit
fi


if [ "$1" = "" ]; then
    usage
    exit 1
fi

function safe_run_cmd () {
    typeset cmnd="$1"
    typeset ret_code

    echo cmnd=$cmnd
    op=$(($cmnd) 2>&1)
    ret_code=$?

    if [ $ret_code != 0 ]; then
        printf "Error: [%d] when executing command: '$cmnd'" $ret_code
        echo
        echo "stdout+stderr for failed command"
        echo "$op"
        git checkout -q $branch
        exit $ret_code
    fi
}

branch=$(git rev-parse --abbrev-ref HEAD)
remote_branch=origin/$branch
commits=($(git log  $remote_branch..HEAD --oneline | cut -d " " -f 1))
num_commits=${#commits[@]}
command=$1

printf "=> Local branch ahead of remote branch by %d commits" $num_commits

for ((i=$num_commits-1; i>=0; i--)); do
    if [ "$i" -eq "0" ]; then
        refname=HEAD
        commit=$branch
    else
        refname=(HEAD~$i)
        commit=${commits[$i]}
    fi
  echo
  echo "=> checking out the commit: ${commits[$i]} ($refname)"
  git checkout -q $commit
  safe_run_cmd "$command"
  echo "--------------------------------------------------------------"
done

git checkout -q $branch
