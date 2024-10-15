# Base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl \
    && pip install --upgrade pip

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Fetch the wait-for-it.sh script and make it executable
RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# Copy the application code
COPY . /app

# Expose port 5000 for the backend
EXPOSE 5000

# Set environment variables
ENV DATABASE_URL=postgresql://user:password@postgres:5432/hair_salon

# Run the Flask application with wait-for-it to ensure the PostgreSQL service is available
CMD ["wait-for-it.sh", "postgres:5432", "--", "python", "app.py"]
