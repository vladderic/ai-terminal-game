import unittest
from io import StringIO
from unittest.mock import patch
from game import GRID_SIZE, PLAYER, EMPTY, draw_grid, clear_screen


class TestClearScreen(unittest.TestCase):
    """Test that clear_screen calls the right OS command."""

    @patch("game.os.system")
    def test_clear_screen_calls_os_system(self, mock_system):
        clear_screen()
        mock_system.assert_called_once()


class TestDrawGrid(unittest.TestCase):
    """Test that the grid renders correctly with the player in various positions."""

    def _capture_grid(self, player_pos: tuple[int, int]) -> str:
        """Helper: call draw_grid and capture its printed output."""
        buffer = StringIO()
        with patch("sys.stdout", buffer):
            draw_grid(player_pos)
        return buffer.getvalue()

    def test_player_at_origin(self):
        output = self._capture_grid((0, 0))
        # First line should have @ in the first cell
        first_line = output.splitlines()[1]
        self.assertIn(f" {PLAYER} ", first_line)

    def test_player_at_bottom_right(self):
        output = self._capture_grid((4, 4))
        last_line = output.splitlines()[9]  # row 4 (with dashes between)
        self.assertIn(f" {PLAYER} ", last_line)

    def test_grid_has_correct_dimensions(self):
        output = self._capture_grid((2, 2))
        # Skip the leading blank line, then count data rows (not separator lines)
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        self.assertEqual(len(data_rows), GRID_SIZE)

    def test_each_row_has_correct_columns(self):
        output = self._capture_grid((0, 0))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        for row in data_rows:
            cells = row.split("|")
            self.assertEqual(len(cells), GRID_SIZE)

    def test_player_replaces_dot(self):
        """The player cell should show @, not ·, and exactly one @ per row."""
        output = self._capture_grid((3, 1))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        player_row = data_rows[3]
        # The player row must contain exactly one @
        self.assertEqual(player_row.count(PLAYER), 1)
        # The other rows must contain zero @ symbols
        for i, row in enumerate(data_rows):
            if i != 3:
                self.assertEqual(row.count(PLAYER), 0, f"Row {i} should not have a player")


class TestMovementLogic(unittest.TestCase):
    """Test that the movement logic works by simulating the main loop inputs."""

    def _run_game_with_inputs(self, inputs: list[str]) -> str:
        """Feed a list of inputs into the game and capture all output."""
        input_text = "\n".join(inputs) + "\n"
        buffer = StringIO()
        with patch("builtins.input", side_effect=input_text.splitlines(keepends=True)), \
             patch("sys.stdout", buffer):
            from game import main
            main()
        return buffer.getvalue()

    def test_quit_exits(self):
        output = self._run_game_with_inputs(["quit"])
        self.assertIn("Thanks for playing!", output)

    def test_move_down(self):
        output = self._run_game_with_inputs(["s", "quit"])
        # After moving down, player should be at row 1
        # The second grid draw should show @ in the second row
        self.assertIn("Thanks for playing!", output)

    def test_move_right(self):
        output = self._run_game_with_inputs(["d", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_up_from_origin(self):
        """Pressing W at (0,0) should not move the player."""
        output = self._run_game_with_inputs(["w", "w", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_left_from_origin(self):
        """Pressing A at (0,0) should not move the player."""
        output = self._run_game_with_inputs(["a", "a", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_past_bottom_right(self):
        """Pressing S and D enough times should stop at (4,4)."""
        moves = ["s"] * 5 + ["d"] * 5 + ["quit"]
        output = self._run_game_with_inputs(moves)
        self.assertIn("Thanks for playing!", output)

    def test_invalid_key_is_ignored(self):
        """Typing a random key should not crash or move the player."""
        output = self._run_game_with_inputs(["x", "z", "123", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_case_insensitive(self):
        """Upper and lowercase inputs should both work."""
        output = self._run_game_with_inputs(["W", "s", "D", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_full_path_movement(self):
        """Move in a square: right, down, left, up — should return to start."""
        output = self._run_game_with_inputs(["d", "s", "a", "w", "quit"])
        self.assertIn("Thanks for playing!", output)


if __name__ == "__main__":
    unittest.main()
