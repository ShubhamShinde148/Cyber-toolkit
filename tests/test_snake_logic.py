import unittest
from utils.snake_logic import init_state, place_food, step, SnakeState


class SnakeLogicTestCase(unittest.TestCase):
    def test_move_forward(self):
        state = init_state(grid_size=10, seed=1)
        next_state = step(state)
        self.assertEqual(next_state.snake[0], (state.snake[0][0] + 1, state.snake[0][1]))
        self.assertEqual(len(next_state.snake), len(state.snake))

    def test_growth_on_food(self):
        state = init_state(grid_size=10, seed=2)
        head_x, head_y = state.snake[0]
        food = (head_x + 1, head_y)
        state = SnakeState(
            grid_size=state.grid_size,
            snake=list(state.snake),
            direction=state.direction,
            food=food,
            score=state.score,
            game_over=False,
            paused=False,
            rng=state.rng,
        )
        next_state = step(state)
        self.assertEqual(len(next_state.snake), len(state.snake) + 1)
        self.assertEqual(next_state.score, state.score + 1)

    def test_wall_collision(self):
        state = SnakeState(
            grid_size=5,
            snake=[(0, 0), (1, 0), (2, 0)],
            direction=(-1, 0),
            food=(4, 4),
            score=0,
            game_over=False,
            paused=False,
            rng=init_state(seed=3).rng,
        )
        next_state = step(state)
        self.assertTrue(next_state.game_over)

    def test_self_collision(self):
        state = SnakeState(
            grid_size=6,
            snake=[(2, 2), (2, 3), (1, 3), (1, 2), (1, 1), (2, 1)],
            direction=(0, 1),
            food=(5, 5),
            score=0,
            game_over=False,
            paused=False,
            rng=init_state(seed=4).rng,
        )
        next_state = step(state)
        self.assertTrue(next_state.game_over)

    def test_place_food_last_cell(self):
        grid_size = 3
        snake = [
            (0, 0), (1, 0), (2, 0),
            (0, 1), (1, 1), (2, 1),
            (0, 2), (1, 2),
        ]
        rng = init_state(seed=5).rng
        food = place_food(snake, grid_size, rng)
        self.assertEqual(food, (2, 2))

    def test_place_food_full_grid(self):
        grid_size = 2
        snake = [(0, 0), (1, 0), (0, 1), (1, 1)]
        rng = init_state(seed=6).rng
        food = place_food(snake, grid_size, rng)
        self.assertIsNone(food)


if __name__ == '__main__':
    unittest.main()
