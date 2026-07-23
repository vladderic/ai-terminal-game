import os
import random

GRID_SIZE = 5
PLAYER = "@"
COLLECTIBLE = "★"
HAZARD = "X"
EMPTY = "·"
WIN_SCORE = 10

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_grid(player_pos: tuple[int, int], collectible_pos: tuple[int, int], hazard_pos: tuple[int, int]) -> None:
    """Draw the grid with the player, collectible, and hazard marked."""
    print()
    for row in range(GRID_SIZE):
        line = ""
        for col in range(GRID_SIZE):
            if (row, col) == player_pos:
                line += f" {PLAYER} "
            elif (row, col) == collectible_pos:
                line += f" {COLLECTIBLE} "
            elif (row, col) == hazard_pos:
                line += f" {HAZARD} "
            else:
                line += f" {EMPTY} "
            if col < GRID_SIZE - 1:
                line += "|"
        print(line)
        if row < GRID_SIZE - 1:
            print("-" * (GRID_SIZE * 4 - 1))
    print()

def spawn_collectible(player_pos: tuple[int, int]) -> tuple[int, int]:
    """Return a random position that is not the player's position."""
    while True:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos != player_pos:
            return pos

def spawn_hazard(player_pos: tuple[int, int], collectible_pos: tuple[int, int]) -> tuple[int, int]:
    """Return a random position that is not the player or collectible."""
    while True:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos != player_pos and pos != collectible_pos:
            return pos

def main():
    player_pos = [0, 0]
    score = 0
    collectible_pos = spawn_collectible(tuple(player_pos))
    hazard_pos = spawn_hazard(tuple(player_pos), collectible_pos)

    print("Welcome! You are the '@' symbol on a 5x5 grid.")
    print("Collect the '★' to score points. Avoid the 'X'!")
    print("Use WASD to move, or type 'quit' to exit.\n")

    while True:
        clear_screen()
        print(f"Score: {score}/{WIN_SCORE}")
        draw_grid(tuple(player_pos), collectible_pos, hazard_pos)

        command = input("Move (WASD) or quit: ").strip().lower()

        if command == "quit":
            print("Thanks for playing!")
            break
        elif command == "w" and player_pos[0] > 0:
            player_pos[0] -= 1
        elif command == "s" and player_pos[0] < GRID_SIZE - 1:
            player_pos[0] += 1
        elif command == "a" and player_pos[1] > 0:
            player_pos[1] -= 1
        elif command == "d" and player_pos[1] < GRID_SIZE - 1:
            player_pos[1] += 1

        # Check if player hit the hazard
        if tuple(player_pos) == hazard_pos:
            clear_screen()
            print(f"Score: {score}/{WIN_SCORE}")
            draw_grid(tuple(player_pos), collectible_pos, hazard_pos)
            print("Game Over!")
            break

        # Check if player collected the item
        if tuple(player_pos) == collectible_pos:
            score += 1
            if score >= WIN_SCORE:
                clear_screen()
                print(f"Score: {score}/{WIN_SCORE}")
                draw_grid(tuple(player_pos), collectible_pos, hazard_pos)
                print("You win! Well played!")
                break
            collectible_pos = spawn_collectible(tuple(player_pos))

if __name__ == "__main__":
    main()
