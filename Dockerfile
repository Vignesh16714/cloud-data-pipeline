# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install boto3

# Run the pipeline
CMD ["python", "lambda/handler.py"]