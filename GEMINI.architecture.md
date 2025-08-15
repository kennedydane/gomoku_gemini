# GEMINI Architecture: Technical Blueprint

This document provides a detailed technical specification for the core components of the Gomoku application. It covers the database models, the real-time WebSocket architecture, and the HTMX-driven frontend implementation.

## 1. Database Models (Data Layer)

This section details the Django models that form the application's data layer.

### 1.1. `users.User`
Inherits from `django.contrib.auth.models.AbstractUser`.

| Field Name | Field Type | Description |
| :--- | :--- | :--- |
| `display_name` | `CharField(max_length=50)` | The user's public-facing name. |
| `wins` | `PositiveIntegerField(default=0)` | Total number of games won. |
| `losses` | `PositiveIntegerField(default=0)` | Total number of games lost. |
| `draws` | `PositiveIntegerField(default=0)` | Total number of games drawn. |

**Key Methods:**
- `get_stats()`: Returns a dictionary of the user's win/loss/draw record.

### 1.2. `games.RuleSet`
Stores the configuration for different game variations.

| Field Name | Field Type | Description |
| :--- | :--- | :--- |
| `name` | `CharField(max_length=50, unique=True)` | The unique name of the ruleset (e.g., "Standard", "Renju"). |
| `board_size` | `PositiveSmallIntegerField(default=15)` | The size of the game board (e.g., 15 for a 15x15 board). |
| `win_condition` | `PositiveSmallIntegerField(default=5)` | The number of stones in a row required to win. |
| `allow_overlines` | `BooleanField(default=False)` | If `True`, 6 or more stones in a row also count as a win. |
| `description` | `TextField()` | A brief description of the ruleset. |

### 1.3. `games.Game`
Represents a single game session between two players.

| Field Name | Field Type | Description |
| :--- | :--- | :--- |
| `id` | `UUIDField(primary_key=True, default=uuid.uuid4)` | The primary key for the game. |
| `black_player` | `ForeignKey(User, related_name='black_games')` | The user playing as black. |
| `white_player` | `ForeignKey(User, related_name='white_games')` | The user playing as white. |
| `ruleset` | `ForeignKey(RuleSet)` | The ruleset being used for this game. |
| `status` | `CharField(choices=GameStatus, default='PENDING')` | The current status of the game (e.g., PENDING, ACTIVE, FINISHED, DRAW). |
| `current_turn` | `CharField(choices=PlayerColor, default='BLACK')` | Which player's turn it is. |
| `winner` | `ForeignKey(User, null=True, blank=True)` | The user who won the game. |
| `board_state` | `JSONField()` | A JSON representation of the board, e.g., `{'board': [[null, 'B', 'W'], ...], 'last_move': [x, y]}`. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Timestamp of when the game was created. |
| `finished_at` | `DateTimeField(null=True, blank=True)` | Timestamp of when the game finished. |

**Key Methods:**
- `get_opponent(user)`: Given one player, returns the other player.
- `is_players_turn(user)`: Returns `True` if it is the given user's turn.

### 1.4. `games.Move`
Records a single move within a game.

| Field Name | Field Type | Description |
| :--- | :--- | :--- |
| `game` | `ForeignKey(Game, related_name='moves')` | The game this move belongs to. |
| `player` | `ForeignKey(User)` | The player who made the move. |
| `move_number` | `PositiveIntegerField()` | The sequential number of the move (1, 2, 3, ...). |
| `row` | `PositiveSmallIntegerField()` | The row of the move. |
| `col` | `PositiveSmallIntegerField()` | The column of the move. |
| `timestamp` | `DateTimeField(auto_now_add=True)` | When the move was made. |

## 2. Real-time Architecture (WebSockets)

The real-time layer is powered by Django Channels and a centralized notification service.

### 2.1. `web.consumers.UserConsumer`
This class handles the entire lifecycle of a user's WebSocket connection.

**Responsibilities:**
1.  **`connect()`:**
    -   Authenticates the user from the scope (e.g., from the Django session).
    -   If the user is not authenticated, the connection is rejected.
    -   Adds the user's connection to a user-specific channel group (e.g., `user_{user.id}`). This allows us to easily target messages to all of a user's connected clients (e.g., multiple browser tabs).
2.  **`disconnect()`:**
    -   Removes the connection from the user's channel group.
3.  **`receive()`:**
    -   This method is intentionally kept simple. The client will not send complex messages to the server over the WebSocket. The primary purpose of the WebSocket is for server-to-client communication. Any client actions (like making a move) are sent via standard HTMX `POST` requests.
4.  **Message Handlers (e.g., `game_update(event)`):**
    -   These methods are called when a message is sent to the user's channel group from the backend.
    -   They take the message payload and forward it down to the connected client over the WebSocket.

### 2.2. `web.services.NotificationService`
A centralized, stateless service for sending notifications to users. This service is called by other parts of the application (like the `GameService`) to trigger real-time updates.

**Key Methods:**
- `send_game_update(game: Game)`:
    -   Constructs a payload with the updated game state.
    -   Sends a message to the channel groups of both the black and white players.
    -   The message type will be `game_update`.
- `send_challenge_notification(challenge: Challenge)`:
    -   Constructs a payload with the challenge details.
    -   Sends a message to the challenged user's channel group.
    -   The message type will be `new_challenge`.

### 2.3. WebSocket Message Format
All messages sent from the server to the client will follow a consistent JSON structure:

```json
{
  "type": "event_type_name",
  "payload": {
    // ... data specific to the event
  }
}
```

**Example `game_update` message:**
```json
{
  "type": "game_update",
  "payload": {
    "game_id": "a1b2c3d4-...",
    "updated_by": "username",
    "next_turn": "other_username"
  }
}
```

## 3. Frontend Architecture (HTMX)

The frontend is a "single-page" dashboard built with Django templates and powered by HTMX for dynamic interactions.

### 3.1. The Single-View Dashboard (`dashboard.html`)
The main user interface is a single dashboard with three columns:
1.  **Left Panel:** List of active and recent games.
2.  **Center Panel:** The main content area, which will display the selected game board.
3.  **Right Panel:** Friends list and challenges.

### 3.2. HTMX Interaction Patterns

#### Making a Move (Client -> Server)
1.  **User Action:** The user clicks on an empty intersection on the game board.
2.  **HTMX Trigger:** The clicked element has HTMX attributes:
    ```html
    <div class="intersection"
         hx-post="/games/{game.id}/move/"
         hx-vals='{"row": 7, "col": 7}'
         hx-target="#game-board-wrapper"
         hx-swap="outerHTML">
    </div>
    ```
3.  **Server-Side:**
    -   The `GameMoveView` receives the `POST` request.
    -   It calls `GameService.make_move()`.
    -   If the move is valid, the view renders the `game_board_partial.html` template with the updated game state and returns it as the response.
4.  **HTMX Swap:** HTMX receives the HTML fragment and swaps the `#game-board-wrapper` content with the new board.

#### Receiving an Update (Server -> Client via WebSocket)
This is the crucial part that connects the real-time backend to the HTMX frontend.

1.  **WebSocket Message:** The browser receives a `game_update` message from the server (as described in section 2.3).
2.  **Client-Side JavaScript Listener:** A small, global JavaScript function in `base.html` listens for WebSocket messages from HTMX.
    ```javascript
    document.body.addEventListener('htmx:wsAfterMessage', function(event) {
      const data = JSON.parse(event.detail.message);

      if (data.type === 'game_update') {
        // Find the game board on the page that needs updating
        const gameBoard = document.querySelector(`#game-board-wrapper[data-game-id='${data.payload.game_id}']`);

        if (gameBoard) {
          // Use HTMX's JavaScript API to trigger a request to refresh the board
          htmx.ajax('GET', `/games/${data.payload.game_id}/board/`, {
            target: gameBoard,
            swap: 'outerHTML'
          });
        }

        // Also trigger a refresh of the games list panel
        const gamesPanel = document.querySelector('#games-panel');
        if (gamesPanel) {
            htmx.ajax('GET', '/panels/games/', { target: gamesPanel, swap: 'innerHTML' });
        }
      }
    });
    ```
3.  **HTMX Trigger:** The JavaScript code uses `htmx.ajax()` to programmatically tell HTMX to fetch the latest version of the game board partial from the server.
4.  **Server-Side:** A simple Django view receives this `GET` request, renders the `game_board_partial.html`, and returns it.
5.  **HTMX Swap:** HTMX swaps the old board with the new one, exactly as if the user had initiated the action themselves.

This architecture creates a powerful and efficient feedback loop:
- **User actions** are sent to the server via standard HTTP requests with HTMX.
- **Server-initiated updates** are pushed to the client via WebSockets.
- A **small JavaScript bridge** listens for WebSocket events and uses HTMX's own API to trigger UI updates, keeping all the rendering logic on the server.
