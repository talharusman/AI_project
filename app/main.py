from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
import concurrent.futures
from .game import SuperTicTacToe

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="app/templates")

# Store active games
games = {}

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/game", response_class=HTMLResponse)
async def game(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})

@app.get("/pvp", response_class=HTMLResponse)
async def pvp(request: Request):
    return templates.TemplateResponse("pvp.html", {"request": request})

@app.get("/instructions", response_class=HTMLResponse)
async def instructions(request: Request):
    return templates.TemplateResponse("instructions.html", {"request": request})

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()

    
    # Create a new game if it doesn't exist
    if game_id not in games:
        games[game_id] = SuperTicTacToe()
    
    game = games[game_id]
    
    # Send initial game state
    await websocket.send_json(game.get_game_state())
    
    # If AI starts first, make a move
    if game.current_player == 'O':
        # Send AI thinking status
        thinking_state = game.get_game_state()
        thinking_state['ai_thinking'] = True
        await websocket.send_json(thinking_state)
        
        await asyncio.sleep(0.1)  # Brief pause to let client render thinking status

        # Run AI calculation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            game_state = await loop.run_in_executor(executor, game.ai_move)

        await websocket.send_json(game_state)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["action"] == "move":
                row, col = message["row"], message["col"]
                game_state = game.make_move(row, col)

                # Send updated state after player move
                await websocket.send_json(game_state)

                # If it's AI's turn and game is not over, make AI move
                if not game.game_over and game.current_player == 'O':
                    # Send AI thinking status
                    thinking_state = game.get_game_state()
                    thinking_state['ai_thinking'] = True
                    await websocket.send_json(thinking_state)

                    # Run AI calculation in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        game_state = await loop.run_in_executor(executor, game.ai_move)

                    await websocket.send_json(game_state)

            elif message["action"] == "reset":
                game_state = game.reset_game()
                await websocket.send_json(game_state)

                # If AI starts first after reset, make a move
                if game.current_player == 'O':
                    # Send AI thinking status
                    thinking_state = game.get_game_state()
                    thinking_state['ai_thinking'] = True
                    await websocket.send_json(thinking_state)

                    await asyncio.sleep(0.1)  # Brief pause to let client render thinking status
                    
                    # Run AI calculation in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        game_state = await loop.run_in_executor(executor, game.ai_move)
                    
                    await websocket.send_json(game_state)
    
    except WebSocketDisconnect:
        # Clean up the game when the client disconnects
        if game_id in games:
            del games[game_id]

@app.websocket("/ws/pvp/{game_id}")
async def websocket_pvp_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()

    # Create a new game if it doesn't exist
    if game_id not in games:
        games[game_id] = SuperTicTacToe()

    game = games[game_id]

    # Send initial game state
    state = game.get_game_state()
    state['mode'] = 'pvp'
    await websocket.send_json(state)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["action"] == "move":
                row, col = message["row"], message["col"]
                game_state = game.make_pvp_move(row, col)
                game_state['mode'] = 'pvp'
                await websocket.send_json(game_state)

            elif message["action"] == "reset":
                game_state = game.reset_game()
                game_state['mode'] = 'pvp'
                await websocket.send_json(game_state)

    except WebSocketDisconnect:
        if game_id in games:
            del games[game_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
