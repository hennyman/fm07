# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Add app to the PYTHONPATH
ENV PYTHONPATH /app

# Run test_service.py in gunicorn using 5 workers when the container launches
ENTRYPOINT gunicorn test_service:app -b 0.0.0.0:80 --workers 5