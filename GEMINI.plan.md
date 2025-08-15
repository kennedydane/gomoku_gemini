# GEMINI Plan: Gomoku Full-Stack Application

This document outlines a detailed plan for building a modern, full-stack Gomoku game from a clean start, incorporating best practices and lessons learned from the existing project.

## 1. Core Principles

*   **API-First Design:** The backend will be a standalone RESTful API, capable of supporting multiple clients (web, desktop, mobile).
*   **Test-Driven Development (TDD):** Every feature will be built with a test-first approach.
*   **Service-Oriented Architecture:** Business logic will be encapsulated in service layers, decoupled from the web framework.
*   **Clean Code:** The codebase will be well-documented, typed, and follow PEP 8 standards.
*   **Scalability:** The architecture will be designed to be scalable from the start.

## 2. Technology Stack

*   **Backend:**
    *   **Framework:** Django 5+ with Django REST Framework (DRF)
    *   **Real-time:** Django Channels for WebSockets
    *   **Database:** PostgreSQL 16+
    *   **Async Tasks:** Celery with Redis
    *   **Package Management:** `uv`
*   **Frontend (Web):**
    *   **Framework:** HTMX on top of Django templates
    *   **Styling:** Bootstrap 5
*   **Testing:**
    *   **Framework:** `pytest` with `pytest-django`
    *   **Factories:** `factory-boy`
    *   **Coverage:** `coverage.py`
*   **DevOps:**
    *   **Containerization:** Docker and Docker Compose
    *   **CI/CD:** GitHub Actions

## 3. Project Scaffolding

A clear and logical directory structure is crucial for maintainability.

```
/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/
│   │   └── ...
│   ├── games/
│   │   └── ...
│   ├── users/
│   │   └── ...
│   ├── web/
│   │   ├── consumers.py
│   │   ├── templates/
│   │   ├── static/
│   │   └── ...
│   ├── manage.py
│   ├── pyproject.toml
│   └── pytest.ini
├── docker/
│   ├── backend/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── postgres/
│   │   └── init-db.sh
│   └── ...
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── README.md
└── uv.lock
```

## 4. Backend Architecture

### 4.1. API Design (DRF)

*   **Versioning:** The API will be versioned from the start (e.g., `/api/v1/`).
*   **Authentication:**
    *   Use `dj-rest-auth` or `djoser` for handling registration, login, logout, and token management. This will reduce boilerplate code.
    *   Tokens will be based on DRF's `TokenAuthentication`, but with an expiration policy and a refresh mechanism.
*   **Serializers:**
    *   Serializers will be used for data validation and representation.
    *   Use `ModelSerializer` where possible, but with explicit field definitions for security.
*   **Views:**
    *   Use `ModelViewSet` for standard CRUD operations.
    *   Custom actions will be added for non-CRUD operations (e.g., `start_game`, `make_move`).
*   **Documentation:**
    *   Use `drf-spectacular` to automatically generate an OpenAPI 3 schema and Swagger UI.

### 4.2. Service Layer

*   Business logic will be completely decoupled from Django views.
*   **Example: `GameService`**
    *   `create_game(player1: User, player2: User, ruleset: RuleSet) -> Game`
    *   `make_move(game: Game, player: User, row: int, col: int) -> Move`
    *   `check_for_win(game: Game) -> Optional[User]`
*   Services will raise custom, domain-specific exceptions (e.g., `InvalidMoveError`, `NotYourTurnError`).

### 4.3. Real-time with Django Channels

*   A single WebSocket connection per user will be used for all real-time communication.
*   **Consumer:** A `UserConsumer` will handle the WebSocket lifecycle.
    *   Authentication will be performed on connection.
    *   The consumer will add the user to their own channel group (e.g., `user_{user.id}`).
*   **Notification Service:** A centralized `NotificationService` will be responsible for sending messages to users via WebSockets.
    *   This service will be used by other services (e.g., `GameService`) to send real-time updates.
    *   `send_game_update(game: Game)`
    *   `send_challenge(challenge: Challenge)`

### 4.4. Database Schema

*   **Models:**
    *   `User`: Custom user model inheriting from `AbstractUser`.
    *   `RuleSet`: Defines the rules for a game (board size, win conditions).
    *   `Game`: Represents a single game session.
    *   `Move`: Records a single move in a game.
    *   `Friendship`: Manages friend relationships.
    *   `Challenge`: Represents a game challenge between users.
*   **Indexes:** Strategic indexes will be used on frequently queried fields.

## 5. Frontend Architecture (Web)

*   **HTMX:** All dynamic interactions will be handled with HTMX.
*   **Templates:**
    *   A base template will define the main layout.
    *   Partials will be used for components that are updated via HTMX (e.g., the game board, friends list).
*   **Static Files:**
    *   CSS and JS will be organized by component.
    *   `whitenoise` will be used for serving static files in production.
*   **Client-side state:** Kept to a minimum. The server will be the single source of truth.

## 6. Testing Strategy

*   **`pytest`:** The primary test runner.
*   **Fixtures:** `pytest` fixtures will be used for setting up test data.
*   **Factories:** `factory-boy` will be used to create model instances.
*   **Test Types:**
    *   **Unit Tests:** Test individual functions and classes in isolation (e.g., service layer logic).
    *   **Integration Tests:** Test the interaction between different components (e.g., view -> service -> database).
    *   **End-to-End (E2E) Tests:** Test the full application flow from the user's perspective. For a web application, this would involve a tool like `pytest-playwright`.
*   **Coverage:** Aim for >90% test coverage.

## 7. DevOps and Deployment

### 7.1. Docker

*   A `docker-compose.yml` file will define the services for development and production.
*   **Services:** `backend`, `postgres`, `redis`.
*   The `backend` service will use a multi-stage `Dockerfile` to create a lean production image.

### 7.2. CI/CD with GitHub Actions

*   A `ci.yml` workflow will be triggered on every push and pull request.
*   **Jobs:**
    1.  **Lint & Format:** Run `ruff` to check code quality.
    2.  **Test:** Run the `pytest` suite against the production-like Docker environment.
    3.  **Build & Push:** On merge to `main`, build the Docker image and push it to a container registry (e.g., Docker Hub, GitHub Container Registry).

## 8. Project Management

*   **Task Tracking:** All tasks, bugs, and features will be tracked as GitHub Issues.
*   **Branching Strategy:**
    *   `main`: Production-ready code.
    *   `develop`: Integration branch for features.
    *   `feat/...`: Feature branches.
*   **Pull Requests:** All code changes must be reviewed and pass CI before being merged into `develop`.

## 9. Implementation Plan (High-Level)

1.  **Phase 1: Project Setup**
    *   Initialize project structure.
    *   Set up Docker environment.
    *   Configure `uv` and `pyproject.toml`.
2.  **Phase 2: Core Models and Services**
    *   Implement User, Game, and RuleSet models (TDD).
    *   Implement core `GameService` logic (TDD).
3.  **Phase 3: API and Authentication**
    *   Set up DRF and `dj-rest-auth`.
    *   Implement API endpoints for users and games (TDD).
    *   Set up OpenAPI documentation.
4.  **Phase 4: Real-time Backend**
    *   Configure Django Channels.
    *   Implement `UserConsumer` and `NotificationService` (TDD).
    *   Integrate notifications into `GameService`.
5.  **Phase 5: Web Frontend**
    *   Create base templates and static file structure.
    *   Implement user authentication views (login, register).
    *   Build the game board and dashboard using HTMX and WebSockets (TDD).
6.  **Phase 6: CI/CD and Deployment**
    *   Set up GitHub Actions workflow.
    *   Write deployment scripts.
    *   Deploy to a staging environment.

This plan provides a solid foundation for building a high-quality, maintainable, and scalable Gomoku application.
