#!/usr/bin/env bash

# Initialize the database
airflow db init

# Upgrade the database
airflow db upgrade

# Create Admin user, if it already exists it will not re-create it
airflow users create --username admin --password admin --firstname admin --lastname admin --role Admin --email admin@example.com

# Verify that Admin user exists
airflow users list

# Start the web server
airflow webserver --port 8080 &

# Start the scheduler
airflow scheduler
