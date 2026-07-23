import os

GRID_SIZE = 5
PLAYER = "@"
EMPTY = "·"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_grid(player_pos: tuple[int, int]) -> None:
    """Draw the grid with the player position marked."""
    print()
    for row in range(GRID_SIZE):
        line = ""
        for col in range(GRID_SIZE):
            if (row, col) == player_pos:
                line += f" {PLAYER} "
            else:
                line += f" {EMPTY} "
            if col < GRID_SIZE - 1:
                line += "|"
        print(line)
        if row < GRID_SIZE - 1:
            print("-" * (GRID_SIZE * 4 - 1))
    print()

def main():
    player_pos = [0, 0]  # Start at top-left corner (row, col)

    print("Welcome! You are the '@' symbol on a 5x5 grid.")
    print("Use WASD to move, or type 'quit' to exit.\n")

    while True:
        clear_screen()
        draw_grid(tuple(player_pos))

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

if __name__ == "__main__":
    main()
