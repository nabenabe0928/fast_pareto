import pytest
import unittest

import numpy as np

from fast_pareto.pareto import _change_directions, is_pareto_front, nondominated_rank


def naive_pareto_front(costs: np.ndarray) -> np.ndarray:
    size = len(costs)
    is_front = np.ones(size, dtype=np.bool8)
    for i in range(size):
        for j in range(size):
            if i == j:
                continue
            cond1 = np.all(costs[j] <= costs[i])
            cond2 = np.any(costs[j] < costs[i])
            if cond1 and cond2:
                is_front[i] = False
                break

    return is_front


def test_change_directions() -> None:
    costs = np.random.normal(size=(20, 10))
    new_costs = _change_directions(costs)
    assert np.allclose(costs, new_costs)

    costs = np.random.normal(size=(20, 10))
    larger_is_better_objectives = [1, 3, 4]
    new_costs = _change_directions(
        costs, larger_is_better_objectives=larger_is_better_objectives
    )
    for i in range(len(costs)):
        for idx in larger_is_better_objectives:
            costs[i][idx] *= -1
    assert np.allclose(costs, new_costs)

    with pytest.raises(ValueError):
        costs = np.random.normal(size=(20, 10))
        larger_is_better_objectives = [20]
        _change_directions(
            costs, larger_is_better_objectives=larger_is_better_objectives
        )

    with pytest.raises(ValueError):
        costs = np.random.normal(size=(20, 10))
        larger_is_better_objectives = [-1]
        _change_directions(
            costs, larger_is_better_objectives=larger_is_better_objectives
        )


def test_pareto_front() -> None:
    for _ in range(3):
        costs = np.random.normal(size=(100, 3))
        assert np.allclose(is_pareto_front(costs), naive_pareto_front(costs))

        costs = np.random.normal(size=(100, 3))
        new_costs = costs.copy()
        new_costs[:, 0] *= -1
        assert np.allclose(
            is_pareto_front(costs, larger_is_better_objectives=[0]),
            naive_pareto_front(new_costs),
        )


def test_no_change_in_costs_pareto_front() -> None:
    costs = np.random.normal(size=(100, 3))
    ans = costs.copy()
    is_pareto_front(costs, larger_is_better_objectives=[0])
    assert np.allclose(costs, ans)


def test_nondominated_rank() -> None:
    for _ in range(3):
        costs = np.random.normal(size=(100, 1))
        ranks = np.argsort(np.argsort(costs.flatten()))
        assert np.allclose(nondominated_rank(costs), ranks)

        costs = np.random.normal(size=(100, 1))
        new_costs = costs.copy()
        new_costs[:, 0] *= -1
        ranks = np.argsort(np.argsort(new_costs.flatten()))
        assert np.allclose(
            nondominated_rank(costs, larger_is_better_objectives=[0]), ranks
        )


def test_no_change_in_costs_nondominated_rank() -> None:
    costs = np.random.normal(size=(100, 3))
    ans = costs.copy()
    nondominated_rank(costs, larger_is_better_objectives=[0])
    assert np.allclose(costs, ans)


def test_nondominated_rank_with_tie_break() -> None:
    for _ in range(3):
        costs = np.random.normal(size=(100, 1))
        nd_ranks = nondominated_rank(costs)
        ranks_with_tie_break = nondominated_rank(costs, tie_break=True)
        rank_min = nd_ranks.min()
        rank_max = nd_ranks.max()

        head, tail = 0, 0
        for rank in range(rank_min, rank_max + 1):
            mask = nd_ranks == rank
            targets = nd_ranks[mask]
            tail += targets.size
            assert np.all(head <= ranks_with_tie_break[mask] <= tail - 1)
            head = tail


if __name__ == "__main__":
    unittest.main()
