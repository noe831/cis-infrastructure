#! /bin/sh 

if [ -z "$DNS_ROLE" ]; then
    echo "ERROR!"
    echo "You must specify a value fro \$DNS_ROLE, either internal or external"
    exit -1 
fi 

/usr/sbin/named -g -c /etc/bind/named-$DNS_ROLE.conf -u bind 
