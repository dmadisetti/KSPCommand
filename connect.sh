#!/bin/bash
ssh -oStrictHostKeyChecking=no -i~/.ssh/cs -p$@ \
  -R 50000:localhost:50000 -R 50001:localhost:50001 \
  root@0.tcp.ngrok.io -fN
