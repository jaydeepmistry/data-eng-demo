#!/usr/bin/env bash

# Initialize the database
airflow db init

# Start the web server
airflow webserver --port 8080 &

# Start the scheduler
airflow scheduler
