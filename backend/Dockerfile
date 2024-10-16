# Base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install system dependencies and upgrade pip
RUN apt-get update && apt-get install -y curl \
    && pip install --upgrade pip

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Fetch the wait-for-it.sh script and make it executable
RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# Copy the application code
COPY . /app

# Expose port 5000 for the backend
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV DATABASE_URL=postgresql://user:password@postgres:5432/hair_salon

# Run the Flask application with wait-for-it to ensure the PostgreSQL service is available
CMD ["wait-for-it.sh", "postgres:5432", "--timeout=15", "--", "flask", "run", "--host=0.0.0.0"]
