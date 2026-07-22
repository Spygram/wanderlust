#!/bin/bash
   set -e
   mongoimport --db wanderlust --collection posts --jsonArray \
     --file /docker-entrypoint-initdb.d/sample_posts.json
