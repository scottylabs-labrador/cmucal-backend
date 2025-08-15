# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Handle psycopg2 dependencies for PostgreSQL
RUN apt-get update

RUN apt-get install -y libpq-dev gcc

# Copy the requirements file into the container at /app (moved here to ensure build deps are present first)
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get clean

RUN rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "run.py"]