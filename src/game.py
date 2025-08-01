import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import models

game_router = APIRouter(prefix="/game", tags=["game"])


@game_router.get("/{game_id}", response_model=models.GameState)
def read_gamestate(game_id: int):
    return models.GameState(
        community_cards=[models.Card(rank=1, suit=1)],
        num_players=8,
        current_round=0,
        players=[],
        action_on=0,
    )


@game_router.post("/{game_id}/next", response_model=str)
def next_move(game_id: int, moves: int):
    # Define the name of the directory
    directory_name = os.path.join("test_data")

    # Define the number of files you want to create
    number_of_files = moves

    # i dont actually want to be able to create a billion files on my instance
    """
    # Create the target directory if it doesn't already exist
    # The exist_ok=True argument prevents an error if the directory is already there
    os.makedirs(directory_name, exist_ok=True)
    

    # Loop to create the files
    for i in range(1, number_of_files + 1):
        # Create the full file path by joining the directory and filename
        file_path = os.path.join(directory_name, f"file_{i}.txt")

        # Open the file in write mode ('w') to create it, then immediately close it.
        # The 'with' statement handles closing the file automatically.
        with open(file_path, "w") as fp:
            fp.write("making money moves")
    """

    return f"✅ Successfully created {number_of_files} files in the '{directory_name}' directory."

    # should return the gamestate after the move was made.


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(
        self,
        message: str,
        websocket: WebSocket,
        not_to_self=False,
    ):
        for connection in self.active_connections:
            if not_to_self and connection == websocket:
                pass
            else:
                await connection.send_text(message)


manager = ConnectionManager()


@game_router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            await manager.send_personal_message(f"you: {data}", websocket)
            await manager.broadcast(f"???: {data}", websocket, not_to_self=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("someone left the chat.", websocket)
