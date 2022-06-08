#!/bin/sh
# Changed file endings to LF from CRLF -- the container did NOT like CRLF line endings, tanked right on line 3
echo "downloding localstack dependency"
pip install localstack-client

echo  "starting python script"
python /tmp/scripts/create_and_write_to_queue.py

echo "winding down"
