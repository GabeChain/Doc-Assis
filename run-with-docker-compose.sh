#!/bin/bash

source .env

docker-compose build && docker-compose up
