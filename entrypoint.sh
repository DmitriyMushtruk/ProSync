#!/bin/bash

# Create new migration files for any changes in the models
python manage.py makemigrations

# Apply database migrations to ensure the database schema is up-to-date
python manage.py migrate

# Start the Django development server on all available network interfaces at port 8000
python manage.py runserver 0.0.0.0:8000

# Execute any additional commands passed to the script
exec "$@"
