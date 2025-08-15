# GEMINI TODO: A Step-by-Step TDD Plan for Gomoku

This document provides a comprehensive, fine-grained set of steps to build the Gomoku application following a strict Test-Driven Development (TDD) methodology.

## Phase 1: Project Setup & Core Foundation

### Task 1.1: Initialize Project Structure
- [x] Create the main project directory `gomoku`.
- [x] Inside `gomoku`, create the `backend` directory.
- [x] Run `django-admin startproject app backend` to create the project skeleton.
- [x] Create `users`, `games`, `core`, and `web` Django apps.
- [x] Set up the directory structure as outlined in `GEMINI.plan`.

### Task 1.2: Configure Docker Environment
- [x] Create `docker-compose.yml` with `backend`, `postgres`, and `redis` services.
- [x] Create `Dockerfile` for the `backend` service.
- [x] Create `.dockerignore` and `.gitignore` files.
- [x] Verify that `docker compose up --build` successfully starts the services.

### Task 1.3: Set up `pyproject.toml` and Dependencies
- [x] Initialize `uv`: `uv init`.
- [x] Add core dependencies to `pyproject.toml`: `django`, `djangorestframework`, `psycopg2-binary`, `uv`.
- [x] Add development dependencies: `pytest`, `pytest-django`, `factory-boy`, `ruff`.
- [x] Run `uv sync` to create `uv.lock`.

### Task 1.4: Create Custom User Model (TDD)
- [ ] **RED**: In `users/tests/test_models.py`, write a test `test_create_user` that asserts a new user can be created with a `display_name`. The test should fail as the field doesn't exist.
- [ ] **GREEN**: Create a custom `User` model in `users/models.py` inheriting from `AbstractUser`. Add the `display_name` field. Configure `AUTH_USER_MODEL` in `settings.py`.
- [ ] **RED**: Write a test to ensure a user cannot be created without a username.
- [ ] **GREEN**: Make the necessary model field adjustments.
- [ ] **REFACTOR**: Add a `__str__` method to the `User` model and run `ruff` to format the code.

### Task 1.5: Create Core Game Models (TDD)
- [ ] **RED**: In `games/tests/test_models.py`, write a test `test_create_ruleset` that fails because the `RuleSet` model doesn't exist.
- [ ] **GREEN**: Implement the `RuleSet` model in `games/models.py` with fields like `name`, `board_size`, etc.
- [ ] **RED**: Write a test `test_create_game` that fails. It should test the relationship between `Game`, `User` (as players), and `RuleSet`.
- [ ] **GREEN**: Implement the `Game` model with foreign keys to `User` and `RuleSet`.
- [ ] **RED**: Write a test to ensure a game cannot be created with the same user as both black and white players.
- [ ] **GREEN**: Add a `clean` method or a database constraint to the `Game` model to enforce this rule.
- [ ] **REFACTOR**: Review model fields, add `Meta` options for indexes, and add `__str__` methods.

## Phase 2: API Development (DRF)

### Task 2.1: Configure DRF and Authentication
- [ ] Add `rest_framework`, `rest_framework.authtoken`, and `dj_rest_auth` to `INSTALLED_APPS`.
- [ ] Configure DRF to use `TokenAuthentication` as the default.
- [ ] Add DRF and `dj_rest_auth` URLs to the main `urls.py`.

### Task 2.2: Implement User Auth API (TDD)
- [ ] **RED**: In `users/tests/test_api.py`, write a test `test_user_registration` that makes a `POST` request to `/api/v1/auth/register/` and asserts a 201 response and user creation. It will fail with a 404.
- [ ] **GREEN**: Include the `dj_rest_auth.registration.urls` in your API's `urls.py`.
- [ ] **RED**: Write a test `test_user_login` that posts credentials to `/api/v1/auth/login/` and expects a token in the response.
- [ ] **GREEN**: Include the `dj_rest_auth.urls`.
- [ ] **REFACTOR**: Create a custom serializer for registration to include the `display_name` field.

### Task 2.3: Implement Game & RuleSet API (TDD)
- [ ] **RED**: In `games/tests/test_api.py`, write a test `test_list_rulesets` that requires authentication and expects a 200 response.
- [ ] **GREEN**: Create a `RuleSetSerializer` and a `RuleSetViewSet` and register it with the API router.
- [ ] **RED**: Write a test `test_create_game` that posts the required player and ruleset data to `/api/v1/games/` and expects a 201 response.
- [ ] **GREEN**: Create a `GameSerializer` and `GameViewSet`.
- [ ] **REFACTOR**: Implement permissions to ensure only authenticated users can create games and that a user can't create a game they are not a part of.

## Phase 3: Service Layer & Game Logic

### Task 3.1: Implement `GameService` (TDD)
- [ ] **RED**: In `games/tests/test_services.py`, write a unit test `test_service_make_move_valid` that calls a non-existent `GameService.make_move` and asserts a `Move` object is created.
- [ ] **GREEN**: Create `games/services.py` and implement the `GameService` with a `make_move` method that creates and saves a `Move`.
- [ ] **RED**: Write tests for invalid moves: out of bounds, on an occupied square, not the player's turn. Expect custom exceptions like `InvalidMoveError`.
- [ ] **GREEN**: Add the validation logic to `make_move` and define the custom exceptions in `core/exceptions.py`.
- [ ] **RED**: Write a test for `check_for_win` that passes a board state with a winning line.
- [ ] **GREEN**: Implement the win-checking logic in the `GameService`.
- [ ] **REFACTOR**: Clean up the service methods, add type hints, and ensure all edge cases are handled.

### Task 3.2: Integrate `GameService` into API (TDD)
- [ ] **RED**: In `games/tests/test_api.py`, write an integration test `test_api_make_move` that `POST`s to the `/api/v1/games/{id}/move/` action. It should fail with 404.
- [ ] **GREEN**: Add a `move` action to the `GameViewSet`. In the action, call the `GameService.make_move` method.
- [ ] **RED**: Write a test to ensure that if the service raises `InvalidMoveError`, the API returns a 400 Bad Request response.
- [ ] **GREEN**: Add a `try...except` block in the view action to catch the service exception and return the appropriate `Response`.
- [ ] **REFACTOR**: Ensure the `GameViewSet` is now a "thin" layer, with all business logic delegated to the `GameService`.

## Phase 4: Real-time with WebSockets

### Task 4.1: Configure Django Channels
- [ ] Add `channels` to `pyproject.toml` and `uv sync`.
- [ ] Add `daphne` to `INSTALLED_APPS`.
- [ ] Create `app/asgi.py` and configure the `ProtocolTypeRouter`.
- [ ] Set `ASGI_APPLICATION` in `settings.py`.

### Task 4.2: Implement `NotificationService` and `UserConsumer` (TDD)
- [ ] **RED**: In `web/tests/test_consumers.py`, write an async test `test_websocket_connect_authenticated` that attempts to connect an authenticated user.
- [ ] **GREEN**: Create `web/consumers.py` with a `UserConsumer`. Implement the `connect` method to accept authenticated users.
- [ ] **RED**: Write a test `test_send_message_to_user` that calls a non-existent `NotificationService` and uses `channels.testing.Communicator` to assert the message is received by the consumer.
- [ ] **GREEN**: Create `web/services.py` and implement `NotificationService` with a method to send messages to a user's channel group.
- [ ] **REFACTOR**: Define a clear JSON structure for WebSocket messages (e.g., `{"type": "game_update", "payload": {...}}`).

### Task 4.3: Integrate Notifications into `GameService` (TDD)
- [ ] **RED**: In `games/tests/test_services.py`, mock the `NotificationService` and write a test to assert that `GameService.make_move` calls `notification_service.send_game_update`.
- [ ] **GREEN**: In `GameService.make_move`, after a move is successfully made, call the `NotificationService` to notify both players.
- [ ] **REFACTOR**: Ensure the payload sent in the notification contains all the necessary data for the client to update the UI.

## Phase 5: Web Frontend (HTMX)

### Task 5.1: Create Base Templates and Static Files
- [ ] Create `web/templates/base.html` with Bootstrap 5 and HTMX scripts included.
- [ ] Create a basic `web/static/css/style.css`.
- [ ] Configure static file handling.

### Task 5.2: Implement Web Authentication (TDD)
- [ ] **RED**: In `web/tests/test_views.py`, write a test `test_login_page_renders` that gets the `/login/` URL and asserts a 200 response.
- [ ] **GREEN**: Create a `LoginView` and a `login.html` template.
- [ ] **RED**: Write a test that posts valid credentials to the login view and asserts a successful redirect.
- [ ] **GREEN**: Implement the form handling logic in the `LoginView`.
- [ ] **REFACTOR**: Use `django-crispy-forms` and `crispy-bootstrap5` to make the forms look better with less code.

### Task 5.3: Implement Dashboard and Game Board (TDD)
- [ ] **RED**: Write a test `test_dashboard_renders_for_logged_in_user` that asserts a 200 response and that the user's active games are in the context.
- [ ] **GREEN**: Create the `DashboardView` and `dashboard.html` template. The view should fetch the user's games.
- [ ] **RED**: Write a test for the game board partial view. It should check that a `POST` request to make a move (triggered by HTMX) returns an HTML fragment of the updated board.
- [ ] **GREEN**: Create a `game_board_partial.html` and a view that calls the `GameService` and renders this partial.
- [ ] **REFACTOR**: Ensure the HTMX attributes (`hx-post`, `hx-target`, `hx-swap`) are correctly set up in the templates.

### Task 5.4: Integrate WebSockets with HTMX (TDD)
- [ ] **RED**: This is harder to test with pure backend tests. We'll rely on integration testing. First, ensure the dashboard template includes the `hx-ws="connect /ws/user/"` attribute.
- [ ] **GREEN**: Add the attribute to the template.
- [ ] **Manual Test**:
    1. Open two browsers, log in as two different users playing a game.
    2. Make a move in one browser.
    3. **Write JavaScript**: Add a small JavaScript snippet to `base.html` that listens for the `htmx:wsAfterMessage` event. When a `game_update` message is received, it should find the relevant game board on the page and trigger an HTMX `GET` request to refresh the board partial.
    4. Verify the other browser updates automatically.
- [ ] **REFACTOR**: Clean up the JavaScript listener to be robust and handle different message types.

## Phase 6: CI/CD & Deployment

### Task 6.1: Create GitHub Actions Workflow
- [ ] Create `.github/workflows/ci.yml`.
- [ ] Add a `lint` job that runs `ruff check .` and `ruff format --check .`.
- [ ] Add a `test` job that uses `docker compose` to run the `pytest` suite.
- [ ] Ensure the workflow is triggered on push and pull_request.

### Task 6.2: Finalize Docker for Production
- [ ] Implement a multi-stage `Dockerfile` to create a smaller production image.
- [ ] Use `gunicorn` or `daphne` as the entrypoint in the production `Dockerfile`.
- [ ] Ensure `collectstatic` is run during the build.

### Task 6.3: Write Deployment Documentation
- [ ] Update `README.md` with clear instructions on how to deploy the application using Docker Compose.
- [ ] Include details on setting up environment variables for production.
