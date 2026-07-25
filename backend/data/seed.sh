#!/bin/bash
   set -e
   mongoimport --username "$MONGO_INITDB_ROOT_USERNAME" \
              --password "$MONGO_INITDB_ROOT_PASSWORD" \
              --authenticationDatabase admin \
              --db wanderlust --collection posts --jsonArray \
              --file /docker-entrypoint-initdb.d/sample_posts.json