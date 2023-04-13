FROM python:3.8-slim-buster

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /cloud

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port on which the application will run
EXPOSE 5000

# Set the default command to run the application
CMD [ "venv/bin/python", "cloud.py" ]
