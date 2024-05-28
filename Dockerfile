# Use an official Python runtime as a parent image
FROM python:3.9-slim as backend

# Set the working directory in the container
WORKDIR /app/Backend

# Copy the current directory contents into the container at /app
COPY Backend /app/Backend

# Create a virtual environment and install dependencies
RUN python -m venv ve && \
    . ve/bin/activate && \
    pip install --no-cache-dir -r install.txt

# Use an official Node.js runtime as a parent image
FROM node:14 as frontend

# Set the working directory in the container
WORKDIR /app/dashboard

# Copy the current directory contents into the container at /app
COPY dashboard /app/dashboard

# Install frontend dependencies
RUN npm install

# Create a new stage to run both backend and frontend
FROM python:3.9-slim

# Install Node.js and npm in the final stage
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

# Copy the backend from the previous backend stage
COPY --from=backend /app /app

# Copy the frontend from the previous frontend stage
COPY --from=frontend /app/dashboard /app/dashboard

# Set the working directory to the backend
WORKDIR /app/Backend

# Copy and set up the entrypoint script
COPY entrypoint.sh /app/Backend/entrypoint.sh
RUN chmod +x /app/Backend/entrypoint.sh

# Expose the ports the app runs on
EXPOSE 8000 3000

# Run the entrypoint script
ENTRYPOINT ["/app/Backend/entrypoint.sh"]
