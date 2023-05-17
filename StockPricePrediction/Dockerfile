# Base image
FROM python:3.11.3

# Install Nginx
RUN apt-get update && apt-get install -y nginx

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file to the container
COPY requirements.txt /code/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code to the container
COPY . /code/

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for Nginx
EXPOSE 80

# Run Nginx and the Django development server
CMD service nginx start && python manage.py runserver 0.0.0.0:8000
