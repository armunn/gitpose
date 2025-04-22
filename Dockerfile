# Use the official Python image as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install Docker and Docker Compose
RUN apt-get update && apt-get install -y \
    docker.io \
    docker-compose \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application code into the container
COPY main.py /app/main.py

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install required Python packages using the requirements file
RUN pip install -r requirements.txt

# Expose the port for webhook mode
ENV WEBHOOK_PORT=5000
EXPOSE $WEBHOOK_PORT

# Set the entrypoint for the container
ENTRYPOINT ["python", "main.py"]