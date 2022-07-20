#!/usr/bin/bash

command=$1
ip_list_filepath=$2

if [ "$#" -ne 2 ]; then
    echo "not enough arguments"
elif [ "$command" != "block" ] && [ "$command" != "unblock" ]; then
    echo "invalid command"
elif [ ! -f "$ip_list_filepath" ]; then
    echo "ip list file not found"
elif [ "$command" == "block" ]; then
    for ip in $(cat $ip_list_filepath); do
        if [ $(iptables -L | grep -c $ip) -eq 1 ]; then
            iptables -F INPUT
        else
            iptables -I INPUT -s $ip -j DROP # block ip
        fi
    done

elif [ "$command" == "unblock" ]; then
    for ip in $(cat $ip_list_filepath); do
        if [ $(iptables -L | grep -c $ip) -eq 1 ]; then
            iptables -F INPUT # unblock ip
        else
            iptables -I INPUT -s $ip -j ACCEPT # unblock ip
        fi
    done
fi

# TODO: Implement