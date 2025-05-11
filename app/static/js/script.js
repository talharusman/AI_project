document.addEventListener("DOMContentLoaded", () => {
  // Generate a random game ID
  const gameId = Math.random().toString(36).substring(2, 15)

  // Connect to WebSocket
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${gameId}`)

  // DOM elements
  const grid = document.querySelector(".grid")
  const metaGrid = document.querySelector(".meta-grid")
  const statusElement = document.getElementById("status")
  const playerScoreElement = document.getElementById("player-score")
  const aiScoreElement = document.getElementById("ai-score")
  const resetButton = document.getElementById("reset-button")

  // Game state
  let gameState = null
  let loading = false

  // Create loading overlay
  const loadingOverlay = document.createElement("div")
  loadingOverlay.className = "loading"
  loadingOverlay.innerHTML = '<div class="loading-spinner"></div>'
  document.body.appendChild(loadingOverlay)

  // Initialize the board
  function initializeBoard() {
    // Clear existing grid
    grid.innerHTML = ""
    metaGrid.innerHTML = ""

    // Create meta grid
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const metaCell = document.createElement("div")
        metaCell.className = "meta-cell"
        metaCell.dataset.row = i
        metaCell.dataset.col = j
        metaGrid.appendChild(metaCell)
      }
    }

    // Create main grid
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        const cell = document.createElement("div")
        cell.className = "cell"
        cell.dataset.row = i
        cell.dataset.col = j

        // Add subgrid borders
        if (i % 3 === 0) cell.style.borderTop = "2px solid #34495e"
        if (i % 3 === 2) cell.style.borderBottom = "2px solid #34495e"
        if (j % 3 === 0) cell.style.borderLeft = "2px solid #34495e"
        if (j % 3 === 2) cell.style.borderRight = "2px solid #34495e"

        cell.addEventListener("click", () => handleCellClick(i, j))
        grid.appendChild(cell)
      }
    }
  }

  // Update the board based on game state
  function updateBoard() {
    if (!gameState) return

    // Update main board
    const cells = document.querySelectorAll(".cell")
    cells.forEach((cell) => {
      const row = Number.parseInt(cell.dataset.row)
      const col = Number.parseInt(cell.dataset.col)

      // Clear previous classes
      cell.classList.remove("X", "O", "valid", "subgrid-active", "last-move")

      // Set cell content
      const value = gameState.board[row][col]
      if (value !== ".") {
        cell.classList.add(value)
        cell.textContent = value
      } else {
        cell.textContent = ""
      }

      // Highlight valid moves
      const isValidMove = gameState.valid_moves.some((move) => move[0] === row && move[1] === col)
      if (isValidMove && gameState.current_player === "X" && !gameState.game_over) {
        cell.classList.add("valid")
      }

      // Highlight active subboard
      if (gameState.active_subboard !== null) {
        const subRow = Math.floor(row / 3)
        const subCol = Math.floor(col / 3)
        const subIndex = subRow * 3 + subCol

        if (gameState.active_subboard === -1 || gameState.active_subboard === subIndex) {
          cell.classList.add("subgrid-active")
        }
      }
    })

    // Highlight last move
    if (gameState.last_move) {
      const lastRow = gameState.last_move[0]
      const lastCol = gameState.last_move[1]

      cells.forEach((cell) => {
        const row = Number.parseInt(cell.dataset.row)
        const col = Number.parseInt(cell.dataset.col)

        if (row === lastRow && col === lastCol) {
          cell.classList.add("last-move")
        } else {
          cell.classList.remove("last-move")
        }
      })
    }

    // Update meta board
    const metaCells = document.querySelectorAll(".meta-cell")
    metaCells.forEach((cell) => {
      const row = Number.parseInt(cell.dataset.row)
      const col = Number.parseInt(cell.dataset.col)

      // Clear previous classes
      cell.classList.remove("X", "O", "D")

      // Set meta cell content
      const value = gameState.meta_board[row][col]
      if (value !== ".") {
        cell.classList.add(value)
        cell.textContent = value
      } else {
        cell.textContent = ""
      }
    })

    // Update scores
    playerScoreElement.textContent = gameState.player_score
    aiScoreElement.textContent = gameState.ai_score

    // Update status
    if (gameState.game_over) {
      if (gameState.winner) {
        statusElement.textContent = `Game Over! ${gameState.winner === "X" ? "Player" : "AI"} wins!`
        statusElement.className = `status winner-${gameState.winner}`
      } else {
        statusElement.textContent = "Game Over! It's a draw!"
        statusElement.className = "status"
      }
    } else {
      statusElement.textContent = `Current Player: ${gameState.current_player === "X" ? "Player (X)" : "AI (O)"}`
      statusElement.className = "status"

      if (gameState.current_player === "O") {
        showLoading()
      } else {
        hideLoading()
      }
    }
  }

  // Handle cell click
  function handleCellClick(row, col) {
    console.log(`Cell clicked: row=${row}, col=${col}`)

    if (!gameState) {
      console.log("Game state is null, cannot make a move")
      return
    }

    if (gameState.game_over) {
      console.log("Game is over, cannot make a move")
      return
    }

    if (gameState.current_player !== "X") {
      console.log("Not player's turn, cannot make a move")
      return
    }

    // Check if the move is valid
    const isValidMove = gameState.valid_moves.some((move) => move[0] === row && move[1] === col)

    if (!isValidMove) {
      console.log("Invalid move")
      return
    }

    console.log("Sending move to server")

    // Send move to server
    ws.send(
      JSON.stringify({
        action: "move",
        row: row,
        col: col,
      }),
    )

    // Show loading while waiting for AI
    showLoading()
  }

  // Reset the game
  function resetGame() {
    ws.send(
      JSON.stringify({
        action: "reset",
      }),
    )
  }

  // Show loading overlay
  function showLoading() {
    loading = true
    loadingOverlay.style.display = "flex"
  }

  // Hide loading overlay
  function hideLoading() {
    loading = false
    loadingOverlay.style.display = "none"
  }

  // WebSocket event handlers
  ws.onopen = () => {
    console.log("WebSocket connection opened")
    statusElement.textContent = "Connected! Waiting for game to start..."
    initializeBoard()
  }

  ws.onmessage = (event) => {
    console.log("Received message:", event.data)
    gameState = JSON.parse(event.data)
    updateBoard()

    // Make sure loading is hidden after receiving a message
    hideLoading()
  }

  ws.onclose = () => {
    console.log("WebSocket connection closed")
    statusElement.textContent = "Connection closed. Please refresh the page."
    statusElement.className = "status game-over"
    hideLoading() // Make sure loading is hidden if connection closes
  }

  ws.onerror = (error) => {
    console.error("WebSocket error:", error)
    statusElement.textContent = "Connection error. Please refresh the page."
    statusElement.className = "status game-over"
    hideLoading() // Make sure loading is hidden if there's an error
  }

  // Event listeners
  resetButton.addEventListener("click", resetGame)

  // Initial loading state
  showLoading()
})
