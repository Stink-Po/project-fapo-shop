# Persian E-Commerce Django App

A fully featured, production-ready **Persian E-Commerce** application built with **Django**, **Celery**, **RabbitMQ**, and **Redis**, designed to offer a seamless shopping experience. This project is Dockerized for easy deployment and scalability.

---

## Features

- **Fully Dockerized**: Simplified deployment with Docker for development and production environments.
- **Celery for Asynchronous Task Management**: Offload long-running tasks (e.g., sending emails, processing payments) using Celery with RabbitMQ and Redis as the message broker.
- **Responsive Persian UI**: A sleek and user-friendly interface designed for Persian-speaking users.
- **E-commerce Functionality**:  
  - Product categories with multiple images.  
  - Dynamic color options for products with stock quantities.  
  - Discount system based on accumulated user points.  
  - User-generated product comments and ratings.
- **Social Authentication**: Users can sign up and log in using **Google OAuth** and **mobile phone OTP**.
- **SEO Optimized**: Enhanced with URL patterns and dynamic metadata for better search engine rankings.
- **Secure and Scalable**: Ready for production with robust configurations, using **Gunicorn** and **Nginx** for performance.

---




---

## Requirements

- **Docker**: Make sure Docker is installed and running on your machine.
- **Python 3.8+**
- **RabbitMQ** and **Redis** (configured with Celery)

---

## Setup & Installation

### 1. Clone the Repository

Clone the project repository to your local machine:

```bash
git clone https://github.com/Stink-Po/project-fapo-shop.git
cd ecommerce-django-app
```
### 3 create your .env File

create a .env file in root of project and put your sensitive data with needed keys there
### 2. Build and Run with Docker

To start the app in Docker, run the following command:

```bash
docker-compose up --build
```

This will build the necessary Docker containers (including Django, Celery, RabbitMQ, Redis, and Nginx) and start the application.

### 3. Run Migrations

Once the containers are up and running, you can apply migrations by executing:

```bash
docker-compose exec web python manage.py migrate
```

### 4. Create a Superuser (Optional)

To create a superuser for the Django admin panel, run:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Usage

- The app will be available at `http://localhost:8000` (or the respective port mapped in Docker Compose).
- You can access the Django Admin Panel at `http://localhost:8000/admin` using the superuser credentials.
- To interact with the backend, users can either sign up/login using mobile OTP or Google OAuth.

---

## Celery Configuration

Celery is set up to handle asynchronous tasks such as sending emails, processing payments, etc. RabbitMQ is used as the message broker and Redis for caching.

To start the Celery worker, run:

```bash
docker-compose exec celery celery -A config worker --loglevel=info
```

---

## Production Readiness

- **Gunicorn** is used as the WSGI server.
- **Nginx** is configured for serving static files and acting as a reverse proxy.
- Use Docker Compose to run and manage the app across multiple containers in production.
- Redis and RabbitMQ are configured to ensure high availability of the app's asynchronous tasks.

---

## Deployment

This project is ready to be deployed on platforms like Heroku, AWS, or DigitalOcean. Make sure to configure environment variables such as `DATABASE_URL`, `SECRET_KEY`, and Celery settings in your production environment.

---

## Contributing

We welcome contributions! If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Contact

For any issues or suggestions, feel free to contact me at:

- **Email**: mr.poorya.mohamadi@gmail.com
- **GitHub**: https://github.com/Stink-Po/project-fapo-shop.git

---

## Acknowledgements

- **Django**: The powerful web framework behind this app.
- **Celery**: The asynchronous task queue that powers background jobs.
- **RabbitMQ & Redis**: Our choice for message brokering and caching.
- **Docker**: Making it easy to run this app in isolated environments.
