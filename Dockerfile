# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code to the working directory
COPY . .

# Define environment variable for user profile (to access the Chrome data)
ENV USERPROFILE /root

# Run the script when the container launches
CMD ["python", "pwd.py", "output_file.txt"]


