# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY website/backend/requirements.txt ./website/backend/requirements.txt

# Install the Python dependencies
RUN pip3 install --no-cache-dir -r ./website/backend/requirements.txt

# Copy the entire `website` directory (relative to the Dockerfile location)
COPY website/backend ./website/backend
# Copy the `src` directory into `/app`
COPY src ./src

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "website.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
