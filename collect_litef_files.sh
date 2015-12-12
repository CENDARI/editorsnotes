#!/bin/sh

echo ',
' > /tmp/pad.json

echo '['
find /var/lib/litef/default/resources -name 'application:x-elasticindexer-json-output' | xargs -i cat {} /tmp/pad.json; echo 'null]
'
rm /tmp/pad.json
