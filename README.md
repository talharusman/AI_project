# Super Tic-Tac-Toe Game with AI

## 📌 Overview

Super Tic-Tac-Toe is an enhanced version of the classic Tic-Tac-Toe game. It introduces a 9x9 grid of mini boards, AI-powered gameplay, and a unique scoring system to reward strategic moves. Players can enjoy single-player mode against an intelligent AI or compete in two-player mode.

## 🎯 Objectives

- Develop an AI-powered single-player mode using Minimax with Alpha-Beta Pruning.
- Integrate a performance-based scoring system.
- Design a user-friendly and visually appealing interface.

## 🕹️ Game Design

- **Multi-board Gameplay:** 9x9 grid consisting of 9 smaller 3x3 Tic-Tac-Toe boards.
- **Move Rules:** A move in a mini-board directs the opponent's next move.
- **Winning Condition:** Control 3 mini-boards in a row (horizontal, vertical, or diagonal) to win.

## 🤖 AI Decision-Making

- **Algorithm:** Minimax with Alpha-Beta Pruning.
- **Approach:** Recursively evaluate future game states and select the optimal move.
- **Goal:** Mimic human strategic thinking and ensure optimal performance.

## 🧮 Scoring System

| Move Type              | Points      |
|------------------------|-------------|
| Optimal Move           | +20         |
| Less Optimal Move      | +10          |

## 💻 User Interface Features

- Interactive 9x9 grid with intuitive cell selection.
- Meta board which show the current meta tic tac toe results
- Scoreboard showing real-time points.
- Biuttons for reset board an back to home

## 🧠 Search Algorithm: Minimax + Alpha-Beta Pruning

- **Recursion:** Simulates all possible future plays.
- **Evaluation Function:** Assigns scores to game states (win, draw, loss).
- **Pruning:** Skips branches of the game tree that cannot affect the final decision, improving efficiency.

## ✅ Requirements

- Programming Language: Python / JavaScript (based on chosen platform)
- GUI Framework: FAST API / HTML-CSS-JS
- Minimax and Alpha-Beta Pruning implementation
- Data structures for managing boards and score

## 📌 Conclusion

This project delivers a strategic, engaging twist on classic Tic-Tac-Toe with added AI depth and a rewarding scoring model. Ideal for both casual and strategic gameplay, Super Tic-Tac-Toe provides a challenging AI opponent and innovative gameplay mechanics.

---
