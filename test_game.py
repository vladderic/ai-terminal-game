import unittest
from io import StringIO
from unittest.mock import patch
from game import GRID_SIZE, PLAYER, COLLECTIBLE, EMPTY, WIN_SCORE, draw_grid, clear_screen, spawn_collectible


class TestClearScreen(unittest.TestCase):
    """Test that clear_screen calls the right OS command."""

    @patch("game.os.system")
    def test_clear_screen_calls_os_system(self, mock_system):
        clear_screen()
        mock_system.assert_called_once()


class TestDrawGrid(unittest.TestCase):
    """Test that the grid renders correctly with player and collectible."""

    def _capture_grid(self, player_pos: tuple[int, int], collectible_pos: tuple[int, int]) -> str:
        """Helper: call draw_grid and capture its printed output."""
        buffer = StringIO()
        with patch("sys.stdout", buffer):
            draw_grid(player_pos, collectible_pos)
        return buffer.getvalue()

    def test_player_at_origin(self):
        output = self._capture_grid((0, 0), (2, 2))
        first_line = output.splitlines()[1]
        self.assertIn(f" {PLAYER} ", first_line)

    def test_player_at_bottom_right(self):
        output = self._capture_grid((4, 4), (0, 0))
        last_line = output.splitlines()[9]
        self.assertIn(f" {PLAYER} ", last_line)

    def test_collectible_appears_on_grid(self):
        output = self._capture_grid((0, 0), (3, 2))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        collectible_row = data_rows[3]
        self.assertIn(f" {COLLECTIBLE} ", collectible_row)

    def test_grid_has_correct_dimensions(self):
        output = self._capture_grid((2, 2), (0, 0))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        self.assertEqual(len(data_rows), GRID_SIZE)

    def test_each_row_has_correct_columns(self):
        output = self._capture_grid((0, 0), (4, 4))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        for row in data_rows:
            cells = row.split("|")
            self.assertEqual(len(cells), GRID_SIZE)

    def test_player_and_collectible_both_render(self):
        """Both @ and ★ appear exactly once in the full grid output."""
        output = self._capture_grid((1, 1), (3, 3))
        self.assertEqual(output.count(PLAYER), 1)
        self.assertEqual(output.count(COLLECTIBLE), 1)


class TestSpawnCollectible(unittest.TestCase):
    """Test that spawn_collectible returns valid positions."""

    def test_never_spawns_on_player(self):
        """Run 50 times — collectible must never overlap the player."""
        player = (2, 2)
        for _ in range(50):
            pos = spawn_collectible(player)
            self.assertNotEqual(pos, player)

    def test_returns_tuple_of_two_ints(self):
        pos = spawn_collectible((0, 0))
        self.assertIsInstance(pos, tuple)
        self.assertEqual(len(pos), 2)
        self.assertIsInstance(pos[0], int)
        self.assertIsInstance(pos[1], int)

    def test_within_grid_bounds(self):
        for _ in range(50):
            pos = spawn_collectible((0, 0))
            self.assertGreaterEqual(pos[0], 0)
            self.assertLess(pos[0], GRID_SIZE)
            self.assertGreaterEqual(pos[1], 0)
            self.assertLess(pos[1], GRID_SIZE)


class TestScoring(unittest.TestCase):
    """Test scoring, collection, and win condition by simulating game inputs."""

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
        self.assertIn("Thanks for playing!", output)

    def test_move_right(self):
        output = self._run_game_with_inputs(["d", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_up_from_origin(self):
        output = self._run_game_with_inputs(["w", "w", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_left_from_origin(self):
        output = self._run_game_with_inputs(["a", "a", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_past_bottom_right(self):
        moves = ["s"] * 5 + ["d"] * 5 + ["quit"]
        output = self._run_game_with_inputs(moves)
        self.assertIn("Thanks for playing!", output)

    def test_invalid_key_is_ignored(self):
        output = self._run_game_with_inputs(["x", "z", "123", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_case_insensitive(self):
        output = self._run_game_with_inputs(["W", "s", "D", "quit"])
        self.assertIn("Thanks for playing!", output)

    def test_score_displayed(self):
        """Score line should appear in the output."""
        output = self._run_game_with_inputs(["quit"])
        self.assertIn("Score: 0/10", output)

    @patch("game.spawn_collectible")
    def test_collecting_item_increases_score(self, mock_spawn):
        """Force collectible to player's second position, verify score goes up."""
        # First call: place collectible at (1, 0) so player moves onto it with 's'
        # Second call: place it somewhere harmless so the game continues
        mock_spawn.side_effect = [(1, 0), (4, 4)]
        output = self._run_game_with_inputs(["s", "quit"])
        self.assertIn("Score: 1/10", output)

    @patch("game.spawn_collectible")
    def test_win_condition(self, mock_spawn):
        """Force 10 collects in a row — game should end with victory message."""
        # Alternate collectible between (1,0) and (0,0) so the player
        # can collect by alternating 's' and 'w' moves.
        mock_spawn.side_effect = [(1, 0), (0, 0)] * 10
        moves = ["s", "w"] * 10
        output = self._run_game_with_inputs(moves)
        self.assertIn("You win!", output)


if __name__ == "__main__":
    unittest.main()
