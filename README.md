# Gomoku

A full-stack, real-time Gomoku (Five in a Row) game built with Django and HTMX.

This project is an implementation of the classic Gomoku board game, featuring a modern, scalable architecture. The backend is a robust Django API, while the frontend is a dynamic, server-rendered experience powered by HTMX and WebSockets for real-time updates.

## Features

*   **Real-time Gameplay:** Play against other users in real-time with WebSocket-powered updates.
*   **User Authentication:** Secure user registration and login.
*   **Game Management:** Create, join, and view your active and past games.
*   **Multiple Rulesets:** Support for different game variations (e.g., standard, Renju).
*   **API-First Design:** A versioned RESTful API for potential future clients.
*   **Containerized:** Fully containerized with Docker for easy setup and deployment.

## Technology Stack

### Backend
*   **Framework:** Django / Django REST Framework
*   **Real-time:** Django Channels
*   **Database:** PostgreSQL
*   **Async Tasks:** Celery / Redis
*   **Package Management:** uv

### Frontend
*   **Framework:** HTMX (via Django Templates)
*   **Styling:** Bootstrap 5

### DevOps
*   **Containerization:** Docker / Docker Compose
*   **CI/CD:** GitHub Actions
*   **Testing:** Pytest

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose (V2)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/gomoku-gemini.git
    cd gomoku-gemini
    ```

2.  **Build and run the containers:**
    This command will build the Docker images, start the backend, database, and Redis services.
    ```bash
    docker compose up --build -d
    ```

3.  **Apply database migrations:**
    ```bash
    docker compose exec backend python manage.py migrate
    ```

4.  **Create a superuser (optional):**
    ```bash
    docker compose exec backend python manage.py createsuperuser
    ```

The application should now be running and accessible at `http://localhost:8000`.

## Running Tests

To run the full test suite, use the following command:

```bash
docker compose exec backend pytest
```
