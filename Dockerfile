# Use the official Apache Airflow image
FROM --platform=linux/amd64 apache/airflow:2.2.3

# Fix permissions issue
USER root
RUN mkdir -p /var/lib/apt/lists/partial && chmod -R 755 /var/lib/apt/lists

# Install PostgreSQL and psycopg2
RUN apt-get update -y && apt-get install -y postgresql postgresql-contrib libpq-dev

# Switch back to airflow user
USER airflow

# Copy the requirements file
COPY requirements.txt /requirements.txt

# Install additional dependencies
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy DAGs and scripts
COPY airflow/dags/ /opt/airflow/dags/
COPY airflow/scripts/ /opt/airflow/scripts/

# Set the entry point
ENTRYPOINT ["/opt/airflow/scripts/init.sh"]
