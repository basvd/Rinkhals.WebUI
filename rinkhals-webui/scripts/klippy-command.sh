#!/bin/bash
printf "$1\x03" | socat -t0 -,ignoreeof UNIX-CONNECT:/tmp/unix_uds1,escape=0x03
