# Base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install curl to fetch wait-for-it.sh
RUN apt-get update && apt-get install -y curl

# Copy requirements.txt to the working directory
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Fetch the wait-for-it.sh script and make it executable
RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# Copy the rest of the application code
COPY . /app

# Expose port 5000 for the backend
EXPOSE 5000

# Run the Flask application with wait-for-it to ensure the PostgreSQL service is available
CMD ["wait-for-it.sh", "postgres:5432", "--", "python", "app.py"]