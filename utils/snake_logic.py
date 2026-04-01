import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

Point = Tuple[int, int]
Direction = Tuple[int, int]


@dataclass(frozen=True)
class SnakeState:
    grid_size: int
    snake: List[Point]
    direction: Direction
    food: Optional[Point]
    score: int
    game_over: bool
    paused: bool
    rng: random.Random


def _is_opposite(a: Direction, b: Direction) -> bool:
    return a[0] == -b[0] and a[1] == -b[1]


def _next_direction(current: Direction, requested: Optional[Direction], length: int) -> Direction:
    if requested is None:
        return current
    if length > 1 and _is_opposite(current, requested):
        return current
    return requested


def place_food(snake: List[Point], grid_size: int, rng: random.Random) -> Optional[Point]:
    occupied = set(snake)
    if len(occupied) >= grid_size * grid_size:
        return None
    while True:
        candidate = (rng.randrange(grid_size), rng.randrange(grid_size))
        if candidate not in occupied:
            return candidate


def init_state(grid_size: int = 20, seed: Optional[int] = None) -> SnakeState:
    rng = random.Random(seed)
    mid = grid_size // 2
    snake = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
    direction = (1, 0)
    food = place_food(snake, grid_size, rng)
    return SnakeState(
        grid_size=grid_size,
        snake=snake,
        direction=direction,
        food=food,
        score=0,
        game_over=False,
        paused=False,
        rng=rng,
    )


def step(state: SnakeState, requested_direction: Optional[Direction] = None) -> SnakeState:
    direction = _next_direction(state.direction, requested_direction, len(state.snake))

    if state.game_over or state.paused:
        return SnakeState(
            grid_size=state.grid_size,
            snake=list(state.snake),
            direction=direction,
            food=state.food,
            score=state.score,
            game_over=state.game_over,
            paused=state.paused,
            rng=state.rng,
        )

    head_x, head_y = state.snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    out_of_bounds = (
        new_head[0] < 0
        or new_head[1] < 0
        or new_head[0] >= state.grid_size
        or new_head[1] >= state.grid_size
    )
    if out_of_bounds:
        return SnakeState(
            grid_size=state.grid_size,
            snake=list(state.snake),
            direction=direction,
            food=state.food,
            score=state.score,
            game_over=True,
            paused=state.paused,
            rng=state.rng,
        )

    grow = state.food is not None and new_head == state.food
    body_to_check = state.snake if grow else state.snake[:-1]
    if new_head in body_to_check:
        return SnakeState(
            grid_size=state.grid_size,
            snake=list(state.snake),
            direction=direction,
            food=state.food,
            score=state.score,
            game_over=True,
            paused=state.paused,
            rng=state.rng,
        )

    if grow:
        new_snake = [new_head] + list(state.snake)
        new_food = place_food(new_snake, state.grid_size, state.rng)
        game_over = new_food is None
        return SnakeState(
            grid_size=state.grid_size,
            snake=new_snake,
            direction=direction,
            food=new_food,
            score=state.score + 1,
            game_over=game_over,
            paused=state.paused,
            rng=state.rng,
        )

    new_snake = [new_head] + list(state.snake[:-1])
    return SnakeState(
        grid_size=state.grid_size,
        snake=new_snake,
        direction=direction,
        food=state.food,
        score=state.score,
        game_over=False,
        paused=state.paused,
        rng=state.rng,
    )
