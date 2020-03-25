#!/bin/bash
pass=false
while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do case $1 in
  -h | --help )
    echo "KSPCommand Connect Util
    Usage ./connect.sh [--flags] [port]
    Flags:
      -i | --identity ) List the ssh key to use for connection.
      -p | --pass )     Provide a password to use for connection.
      -h | --help )     Print out this message."
    exit
    ;;
  -i | --identity )
  shift; identity=$1
  ;;
  -p | --pass)
    pass=true
    shift; colab_pass=$1
  ;;
esac; shift; done

command="ssh -oStrictHostKeyChecking=no \
  -R 50000:localhost:50000 -R 50001:localhost:50001 \
  root@0.tcp.ngrok.io -fN"

if [ "x" != "x$colab_pass" ]; then
  command="env SSH_ASKPASS=\"echo $colab_pass\" $command"
fi

if [ "x" != "x$identity" ]; then
  command="$command -i $identity"
fi

port=$@
if [ "x" = "x$port" ]; then
  read -p "Provide the port number: " port
fi

set -x
$command -p $port
