FROM python:3.11-slim

# Set non-interactive mode
RUN export DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    # ssl
    libssl-dev \
    # lxml
    libxml2-dev \
    libxslt1-dev \
    # certifi
    libffi-dev \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8090 available
EXPOSE 8090

# Run app.py when the container launches
CMD ["python", "main.py"]
