# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc libpq-dev python3-dev build-essential \
    && apt-get clean

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && apt-get clean

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libcairo2 \
    libpango1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y postgresql-client
# Copy the requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app/

RUN python manage.py collectstatic --noinput


# Expose port 8000
EXPOSE 8000

# Run migrations and collect static files (for production)
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn fapo.wsgi:application --bind 0.0.0.0:8000 --worker-class gevent --timeout 120"]
