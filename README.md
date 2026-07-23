# Hungry Dragon

A terminal-based Python game where you play as a dragon 🐉 searching for food 🍖 while avoiding cunning knights 🤺.

## Story

You are a dragon who has awakened from its 1000-year slumber and is craving its favourite food. Find enough food to continue your slumber — but be careful of the knights looking for you!

## Features

- **5x5 grid** with smooth terminal rendering
- **WASD movement** with boundary checks to keep the dragon on the board
- **Collectible food** that spawns at random positions and increases your score
- **Hazardous knights** that end the game on contact
- **Win condition** — collect 10 pieces of food to resume your slumber
- **Lose condition** — get caught by a knight and the game is over
- **Play again** — after each round, choose to start fresh or exit
- **Score tracking** displayed at the top of the grid every turn

## How to Run

### Start the game

```bash
python game.py
```

### Run the test suite

```bash
pytest test_game.py -v
```

The test suite covers grid rendering, spawning logic, movement, scoring, win/lose conditions, and the play-again loop. All 32 tests should pass.

## Project Structure

```
ai-terminal-game/
├── game.py          # Main game logic and entry point
├── test_game.py     # Pytest test suite
└── README.md        # This file
```

## What I Learned

- **Iterative development** — The game started as a bare 5x5 grid with no features. Each layer (movement, collectibles, hazards, theming, play-again) was added one at a time, tested, and verified before moving on. Building in small increments made it easy to isolate and fix issues.

- **Engineering prompts to prevent regression** — Every time a new feature was added, the existing tests were re-run to catch unintended side effects. For example, adding the hazard tile broke two existing tests because the hazard randomly landed on the player's expected path. Mocking and careful test isolation prevented these regressions from slipping through.

- **Automated testing with pytest** — Writing tests alongside the code caught bugs early and gave confidence to refactor. Mocking random spawning and user input meant every scenario could be tested deterministically, including win/loss paths and the play-again loop.
