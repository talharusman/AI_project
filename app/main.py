from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import asyncio
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
        await asyncio.sleep(1.5)  # 1.5 second pause before AI's turn
        game_state = game.ai_move()
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
                
                # If it's AI's turn and game is not over, make AI move after a delay
                if not game.game_over and game.current_player == 'O':
                    await asyncio.sleep(1.5)  # 1.5 second pause before AI's turn
                    game_state = game.ai_move()
                    await websocket.send_json(game_state)
            
            elif message["action"] == "reset":
                game_state = game.reset_game()
                await websocket.send_json(game_state)
                
                # If AI starts first after reset, make a move
                if game.current_player == 'O':
                    await asyncio.sleep(1.5)  # 1.5 second pause before AI's turn
                    game_state = game.ai_move()
                    await websocket.send_json(game_state)
    
    except WebSocketDisconnect:
        # Clean up the game when the client disconnects
        if game_id in games:
            del games[game_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
