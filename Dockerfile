# Use the official Python image as the base for the container
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Configure Python environment:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# - PYTHONUNBUFFERED: Ensures logs are output in real-time without buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy all project files from the local system to the container's /app directory
COPY . /app/

# Update pip to the latest version and install project dependencies
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt

# Expose port 8000 to allow access to the Django application from outside the container
EXPOSE 8000

# Specify the entrypoint script to initialize and start the Django application
ENTRYPOINT ["./entrypoint.sh"]
