# Use a base image with Python installed
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the entire root directory (including mls, db, etc.) to the container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Set the default command to run your main Python script
CMD ["python", "main.py"]
