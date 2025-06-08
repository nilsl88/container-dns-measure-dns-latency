#!/bin/bash

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
CSV_FILE="dns_latency_log.csv"

# Hvis der gives et argument, brug det som sti til filen
if [ -n "$1" ]; then
    CSV_FILE="$1"
fi

# Static servers
STATIC_SERVERS="8.8.8.8 1.1.1.1"
# Add nameservers from /etc/resolv.conf
RESOLV_CONF_SERVERS=$(grep ^nameserver /etc/resolv.conf | awk '{print $2}')

# Combine both
SERVERS="$STATIC_SERVERS $RESOLV_CONF_SERVERS"

# Domains to query
DOMAINS="dr.dk tv2.dk eb.dk"

# Write header if file doesn't exist
if [ ! -f "$CSV_FILE" ]; then
    echo "timestamp,protocol,dns_server,domain,query_time_ms" | tee -a "$CSV_FILE"
fi

for PROTO in "" "+tcp"; do
    for SERVER in $SERVERS; do
        for DOMAIN in $DOMAINS; do
            OUTPUT=$(dig $PROTO @$SERVER $DOMAIN | grep "Query time:")
            TIME=$(echo $OUTPUT | grep -o '[0-9]\+')
            PROTO_LABEL="udp"
            [ "$PROTO" = "+tcp" ] && PROTO_LABEL="tcp"
            echo "$TIMESTAMP,$PROTO_LABEL,$SERVER,$DOMAIN,$TIME" | tee -a "$CSV_FILE"
        done
    done
done

