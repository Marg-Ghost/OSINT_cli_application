#!/bin/bash
source ~/desktop/tor.sh

if [ -f "/home/marg_ghost/desktop/assets/osint.txt" ]; then
    cat /home/marg_ghost/desktop/assets/osint.txt
fi
ehco "||=====================||"
ehco "||  Wellcome to OSINT  ||"
ehco "||=====================||"
ehco "|| 1:Email  2:username ||"
ehco "||=====================||"

if [ -z "$1" ]; then
    echo "[-] Missing type: (1 for email / 2 for username)"
    exit 1
fi

if [ "$1" == "1" ]; then
    python "email.py"
elif [ "$1" == "2" ]; then
    python "username.py"
else
    echo "[-] Ungültige Option: $1"
fi

