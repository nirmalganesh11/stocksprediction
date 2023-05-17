# Base image
FROM python:3.11.3 AS base

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

# Stage 2: Build the static files
FROM base AS build
RUN python manage.py collectstatic --noinput

# Stage 3: Final image with Nginx
FROM nginx:latest
COPY --from=build /code/static /static
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port
EXPOSE 80
