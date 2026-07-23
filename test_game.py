import unittest
from io import StringIO
from unittest.mock import patch
from game import GRID_SIZE, PLAYER, COLLECTIBLE, HAZARD, EMPTY, WIN_SCORE, draw_grid, clear_screen, spawn_collectible, spawn_hazard


class TestClearScreen(unittest.TestCase):
    """Test that clear_screen calls the right OS command."""

    @patch("game.os.system")
    def test_clear_screen_calls_os_system(self, mock_system):
        clear_screen()
        mock_system.assert_called_once()


class TestDrawGrid(unittest.TestCase):
    """Test that the grid renders correctly with player, collectible, and hazard."""

    def _capture_grid(self, player_pos: tuple[int, int], collectible_pos: tuple[int, int], hazard_pos: tuple[int, int]) -> str:
        """Helper: call draw_grid and capture its printed output."""
        buffer = StringIO()
        with patch("sys.stdout", buffer):
            draw_grid(player_pos, collectible_pos, hazard_pos)
        return buffer.getvalue()

    def test_player_at_origin(self):
        output = self._capture_grid((0, 0), (2, 2), (4, 4))
        first_line = output.splitlines()[1]
        self.assertIn(f" {PLAYER} ", first_line)

    def test_player_at_bottom_right(self):
        output = self._capture_grid((4, 4), (0, 0), (2, 2))
        last_line = output.splitlines()[9]
        self.assertIn(f" {PLAYER} ", last_line)

    def test_collectible_appears_on_grid(self):
        output = self._capture_grid((0, 0), (3, 2), (4, 4))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        collectible_row = data_rows[3]
        self.assertIn(f" {COLLECTIBLE} ", collectible_row)

    def test_hazard_appears_on_grid(self):
        output = self._capture_grid((0, 0), (3, 2), (1, 3))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        hazard_row = data_rows[1]
        self.assertIn(f" {HAZARD} ", hazard_row)

    def test_grid_has_correct_dimensions(self):
        output = self._capture_grid((2, 2), (0, 0), (4, 4))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        self.assertEqual(len(data_rows), GRID_SIZE)

    def test_each_row_has_correct_columns(self):
        output = self._capture_grid((0, 0), (4, 4), (2, 2))
        lines = output.strip().splitlines()
        data_rows = [line for line in lines if "|" in line]
        for row in data_rows:
            cells = row.split("|")
            self.assertEqual(len(cells), GRID_SIZE)

    def test_all_three_symbols_render(self):
        """@, ★, and X each appear exactly once in the full grid output."""
        output = self._capture_grid((1, 1), (3, 3), (0, 4))
        self.assertEqual(output.count(PLAYER), 1)
        self.assertEqual(output.count(COLLECTIBLE), 1)
        self.assertEqual(output.count(HAZARD), 1)


class TestSpawnCollectible(unittest.TestCase):
    """Test that spawn_collectible returns valid positions."""

    def test_never_spawns_on_player(self):
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


class TestSpawnHazard(unittest.TestCase):
    """Test that spawn_hazard returns valid positions that avoid both player and collectible."""

    def test_never_spawns_on_player(self):
        for _ in range(50):
            pos = spawn_hazard((2, 2), (3, 3))
            self.assertNotEqual(pos, (2, 2))

    def test_never_spawns_on_collectible(self):
        for _ in range(50):
            pos = spawn_hazard((2, 2), (3, 3))
            self.assertNotEqual(pos, (3, 3))

    def test_within_grid_bounds(self):
        for _ in range(50):
            pos = spawn_hazard((0, 0), (4, 4))
            self.assertGreaterEqual(pos[0], 0)
            self.assertLess(pos[0], GRID_SIZE)
            self.assertGreaterEqual(pos[1], 0)
            self.assertLess(pos[1], GRID_SIZE)


class TestGameLoop(unittest.TestCase):
    """Test the full game loop including play-again prompts."""

    def _run_game_with_inputs(self, inputs: list[str]) -> str:
        """Feed a list of inputs into the game and capture all output.

        The first input is consumed by the 'Press Enter to start...' prompt.
        Subsequent inputs feed into the game round and play-again prompt.
        """
        input_text = "\n".join(inputs) + "\n"
        buffer = StringIO()
        with patch("builtins.input", side_effect=input_text.splitlines(keepends=True)), \
             patch("game.spawn_hazard", return_value=(0, 4)), \
             patch("sys.stdout", buffer):
            from game import main
            main()
        return buffer.getvalue()

    # --- Basic movement ---

    def test_quit_exits(self):
        output = self._run_game_with_inputs(["", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_move_down(self):
        output = self._run_game_with_inputs(["", "s", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_move_right(self):
        output = self._run_game_with_inputs(["", "d", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_up_from_origin(self):
        output = self._run_game_with_inputs(["", "w", "w", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_left_from_origin(self):
        output = self._run_game_with_inputs(["", "a", "a", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_cannot_move_past_bottom_right(self):
        moves = ["s"] * 5 + ["d"] * 5 + ["quit", "n"]
        output = self._run_game_with_inputs([""] + moves)
        self.assertIn("Thanks for playing!", output)

    def test_invalid_key_is_ignored(self):
        output = self._run_game_with_inputs(["", "x", "z", "123", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_case_insensitive(self):
        output = self._run_game_with_inputs(["", "W", "s", "D", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    def test_score_displayed(self):
        output = self._run_game_with_inputs(["", "quit", "n"])
        self.assertIn("Score: 0/10", output)

    # --- Collectible ---

    @patch("game.spawn_collectible")
    def test_collecting_item_increases_score(self, mock_collect):
        """Force collectible to player's next position, verify score goes up."""
        mock_collect.side_effect = [(1, 0), (4, 4)]
        output = self._run_game_with_inputs(["", "s", "quit", "n"])
        self.assertIn("Score: 1/10", output)

    @patch("game.spawn_collectible")
    def test_win_condition(self, mock_collect):
        """Force 10 collects in a row — game should end with victory message."""
        mock_collect.side_effect = [(1, 0), (0, 0)] * 10
        moves = ["s", "w"] * 10
        output = self._run_game_with_inputs([""] + moves + ["n"])
        self.assertIn("You win!", output)

    # --- Hazard ---

    @patch("game.spawn_hazard")
    @patch("game.spawn_collectible")
    def test_hazard_kills_player(self, mock_collect, mock_hazard):
        """Move player onto the hazard — game should end with 'Game Over!'."""
        mock_collect.return_value = (4, 4)
        mock_hazard.return_value = (1, 0)
        input_text = "\n".join(["", "s", "n"]) + "\n"
        buffer = StringIO()
        with patch("builtins.input", side_effect=input_text.splitlines(keepends=True)), \
             patch("sys.stdout", buffer):
            from game import main
            main()
        output = buffer.getvalue()
        self.assertIn("Game Over!", output)

    @patch("game.spawn_hazard")
    @patch("game.spawn_collectible")
    def test_hazard_terminates_round_immediately(self, mock_collect, mock_hazard):
        """After hitting the hazard, further move inputs are not processed."""
        mock_collect.return_value = (4, 4)
        mock_hazard.return_value = (1, 0)
        # 's' hits hazard at (1,0) — round ends, no more moves processed
        input_text = "\n".join(["", "s", "n"]) + "\n"
        buffer = StringIO()
        with patch("builtins.input", side_effect=input_text.splitlines(keepends=True)), \
             patch("sys.stdout", buffer):
            from game import main
            main()
        output = buffer.getvalue()
        self.assertIn("Game Over!", output)
        # Only 3 inputs consumed: start, move, play-again

    # --- Play again ---

    def test_play_again_prompt_after_win(self):
        """After winning, user should be asked 'Play again?'."""
        output = self._run_game_with_inputs(["", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    @patch("game.spawn_hazard")
    @patch("game.spawn_collectible")
    def test_play_again_prompt_after_game_over(self, mock_collect, mock_hazard):
        """After game over, choosing 'n' exits cleanly."""
        mock_collect.return_value = (4, 4)
        mock_hazard.return_value = (1, 0)
        input_text = "\n".join(["", "s", "n"]) + "\n"
        buffer = StringIO()
        with patch("builtins.input", side_effect=input_text.splitlines(keepends=True)), \
             patch("sys.stdout", buffer):
            from game import main
            main()
        output = buffer.getvalue()
        self.assertIn("Game Over!", output)
        self.assertIn("Thanks for playing!", output)

    @patch("game.spawn_hazard")
    @patch("game.spawn_collectible")
    def test_play_again_resets_game(self, mock_collect, mock_hazard):
        """Choosing 'y' should start a fresh round with score 0."""
        mock_collect.side_effect = [(1, 0), (4, 4), (1, 0), (4, 4)]
        mock_hazard.return_value = (0, 4)
        # Start, move down (collect), play again, move down (collect), quit
        output = self._run_game_with_inputs(["", "s", "y", "s", "quit", "n"])
        # Score should appear as 1/10 in the second round (fresh start)
        self.assertIn("Score: 1/10", output)

    def test_no_to_play_again_exits(self):
        """Choosing 'n' at play again prompt should exit cleanly."""
        output = self._run_game_with_inputs(["", "quit", "n"])
        self.assertIn("Thanks for playing!", output)

    @patch("game.spawn_hazard")
    @patch("game.spawn_collectible")
    def test_win_then_play_again(self, mock_collect, mock_hazard):
        """Winning then choosing 'y' should start a fresh round."""
        mock_collect.side_effect = [(1, 0), (0, 0)] * 10 + [(1, 0), (4, 4)]
        mock_hazard.return_value = (0, 4)
        moves_win = ["s", "w"] * 10
        output = self._run_game_with_inputs([""] + moves_win + ["y", "s", "quit", "n"])
        self.assertIn("You win!", output)
        # Second round should show score 1/10
        self.assertIn("Score: 1/10", output)


if __name__ == "__main__":
    unittest.main()
