# Use the official Python image from the Docker Hub
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file and the application code
COPY requirements.txt .

# Install the necessary packages
RUN pip install --no-cache-dir -r requirements.txt

COPY Agents/ .
COPY Game/ .

# Expose the port the app runs on
EXPOSE 8050

# Keep the container running for interactive use
CMD ["tail", "-f", "/dev/null"]