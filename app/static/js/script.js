document.addEventListener("DOMContentLoaded", () => {
  const gameId = Math.random().toString(36).substring(2, 15)

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
  const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${gameId}`)

  const grid = document.querySelector(".grid")
  const metaGrid = document.querySelector(".meta-grid")
  const statusElement = document.getElementById("status")
  const playerScoreElement = document.getElementById("player-score")
  const aiScoreElement = document.getElementById("ai-score")
  const resetButton = document.getElementById("reset-button")
  const modal = document.getElementById("game-over-modal")
  const modalIcon = document.getElementById("modal-icon")
  const modalTitle = document.getElementById("modal-title")
  const modalSubtitle = document.getElementById("modal-subtitle")

  let gameState = null
  let waitingForAI = false

  function initializeBoard() {
    grid.innerHTML = ""
    metaGrid.innerHTML = ""

    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        const metaCell = document.createElement("div")
        metaCell.className = "meta-cell"
        metaCell.dataset.row = i
        metaCell.dataset.col = j
        metaGrid.appendChild(metaCell)
      }
    }

    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        const cell = document.createElement("div")
        cell.className = "cell"
        cell.dataset.row = i
        cell.dataset.col = j

        if (i % 3 === 0) cell.classList.add("subgrid-border-top")
        if (i % 3 === 2) cell.classList.add("subgrid-border-bottom")
        if (j % 3 === 0) cell.classList.add("subgrid-border-left")
        if (j % 3 === 2) cell.classList.add("subgrid-border-right")

        cell.addEventListener("click", () => handleCellClick(i, j))
        grid.appendChild(cell)
      }
    }
  }

  function showGameOverModal() {
    if (gameState.winner === "X") {
      modalIcon.textContent = "\uD83C\uDFC6"
      modalTitle.textContent = "You Win!"
      modalTitle.className = "modal-title winner-x-title"
      modalSubtitle.textContent = "Nicely played! You outsmarted the AI."
    } else if (gameState.winner === "O") {
      modalIcon.textContent = "\uD83E\uDD16"
      modalTitle.textContent = "AI Wins!"
      modalTitle.className = "modal-title winner-o-title"
      modalSubtitle.textContent = "The AI got you this time. Try again?"
    } else {
      modalIcon.textContent = "\uD83E\uDD1D"
      modalTitle.textContent = "It's a Draw!"
      modalTitle.className = "modal-title"
      modalSubtitle.textContent = "So close! Neither side could claim victory."
    }
    modal.style.display = "flex"
  }

  function updateBoard() {
    if (!gameState) return

    const cells = document.querySelectorAll(".cell")
    cells.forEach((cell) => {
      const row = Number.parseInt(cell.dataset.row)
      const col = Number.parseInt(cell.dataset.col)

      cell.classList.remove("X", "O", "valid", "ai-valid", "subgrid-active", "last-move")

      const value = gameState.board[row][col]
      if (value !== ".") {
        cell.classList.add(value)
        cell.textContent = value
        cell.style.cursor = "default"
        cell.classList.remove("subgrid-active")
      } else {
        cell.textContent = ""
        cell.style.cursor = "pointer"

        if (gameState.active_subboard !== null && gameState.active_subboard !== -1) {
          const subRow = Math.floor(row / 3)
          const subCol = Math.floor(col / 3)
          const subIndex = subRow * 3 + subCol

          if (gameState.active_subboard === subIndex) {
            cell.classList.add("subgrid-active")
          }
        }
      }

      const isValidMove = gameState.valid_moves.some((move) => move[0] === row && move[1] === col)
      if (isValidMove && !gameState.game_over && value === ".") {
        if (gameState.current_player === "X") {
          cell.classList.add("valid")
        } else if (gameState.current_player === "O") {
          cell.classList.add("ai-valid")
        }
      }
    })

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

    const metaCells = document.querySelectorAll(".meta-cell")
    metaCells.forEach((cell) => {
      const row = Number.parseInt(cell.dataset.row)
      const col = Number.parseInt(cell.dataset.col)

      cell.classList.remove("X", "O", "D")

      const value = gameState.meta_board[row][col]
      if (value !== ".") {
        cell.classList.add(value)
        cell.textContent = value
      } else {
        cell.textContent = ""
      }
    })

    playerScoreElement.textContent = gameState.player_score
    aiScoreElement.textContent = gameState.ai_score

    if (gameState.game_over) {
      waitingForAI = false
      if (gameState.winner) {
        statusElement.textContent = `Game Over! ${gameState.winner === "X" ? "Player" : "AI"} wins!`
        statusElement.className = `status winner-${gameState.winner}`
      } else {
        statusElement.textContent = "Game Over! It's a draw!"
        statusElement.className = "status"
      }
      setTimeout(showGameOverModal, 3000)
    } else {
      if (gameState.ai_thinking || gameState.current_player === "O") {
        waitingForAI = true
        statusElement.textContent = "AI is thinking..."
        statusElement.className = "status ai-thinking"
      } else {
        waitingForAI = false
        const validCount = gameState.valid_moves.length
        const subboardInfo =
          gameState.active_subboard === -1
            ? "any sub-board"
            : `sub-board ${gameState.active_subboard + 1}`
        statusElement.textContent = `Your turn (X) \u2014 ${validCount} cell${validCount !== 1 ? "s" : ""} available in ${subboardInfo}`
        statusElement.className = "status player-turn"
      }
    }
  }

  function handleCellClick(row, col) {
    if (!gameState) return
    if (gameState.game_over) return
    if (waitingForAI) return
    if (gameState.current_player !== "X") return

    const isValidMove = gameState.valid_moves.some((move) => move[0] === row && move[1] === col)
    if (!isValidMove) return

    ws.send(
      JSON.stringify({
        action: "move",
        row: row,
        col: col,
      }),
    )

    waitingForAI = true
    statusElement.textContent = "AI is thinking..."
    statusElement.className = "status ai-thinking"
  }

  function resetGame() {
    modal.style.display = "none"
    ws.send(
      JSON.stringify({
        action: "reset",
      }),
    )
  }

  ws.onopen = () => {
    statusElement.textContent = "Connected! Starting game..."
    initializeBoard()
  }

  ws.onmessage = (event) => {
    gameState = JSON.parse(event.data)
    updateBoard()
  }

  ws.onclose = () => {
    statusElement.textContent = "Connection closed. Please refresh the page."
    statusElement.className = "status game-over"
  }

  ws.onerror = () => {
    statusElement.textContent = "Connection error. Please refresh the page."
    statusElement.className = "status game-over"
  }

  resetButton.addEventListener("click", resetGame)
})
