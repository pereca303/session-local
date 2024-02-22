#!/bin/bash 

docker-compose up --detach stream-registry \
	registry-database \
	users-db \
	tokens-core \
	tokens-db \
	tokens-api 

# auth-service \
# users-database \

echo "Auth and stream registry service deployed ... "

./utils/cdn/remove_cdn.py
./utils/cdn/deploy_cdn.py

echo "Cdn instances deployed" 

docker-compose up --detach cdn-proxy

echo "Cdn proxy deployed."

./utils/ingest/stop_ingests.py y
./utils/ingest/deploy_ingest.py 2 0

echo "Ingest deployed ... "

docker-compose up --detach ingest-proxy 

echo "Ingest proxy deoployed ... "