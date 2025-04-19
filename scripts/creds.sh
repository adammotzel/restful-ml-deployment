#!/bin/bash

# random username
AUTH_UN=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 8)

# random password
AUTH_PW=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 24)

echo "AUTH_UN=$AUTH_UN" > .env
echo "AUTH_PW=$AUTH_PW" >> .env

echo "Environment variables have been set and saved in .env file."
