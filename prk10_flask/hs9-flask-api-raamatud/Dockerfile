# Use an official Python runtime as a parent image
FROM python:3.8-slim

RUN mkdir -p /usr/src/app

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /app
COPY requirements.txt requirements.txt

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY hs9-flask-api-raamatud.py app.py

EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]

