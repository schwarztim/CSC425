FROM python:3.8-slim

# Working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y curl \
    && pip install --upgrade pip

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Fetch wait-for-it.sh
RUN curl -o /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# Copy the application code
COPY . /app

# Expose port 8000
EXPOSE 8000

# Run the Flask application with wait-for-it
CMD ["wait-for-it.sh", "backend:5000", "--timeout=15", "--", "python", "app.py"]
