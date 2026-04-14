"""
Auxiliary library for benchmark tests.

"""

__all__ = [
    "Human",
    "Sex",
    "age_max",
    "age_min",
    "generate_humans",
    "make_random_human",
    "plot_results",
    "python_ver",
    "run_benchmark",
    "tested_version",
]

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from importlib.metadata import version as pkg_version
from random import choice, randint, seed
from sys import version
from timeit import repeat
from typing import Any

import matplotlib.pyplot as plt  # type: ignore

from benchmark import project_name

smort_ver = pkg_version("smort-query")
python_ver = version.split()[0]

N_REPEAT = 3  # Number of repeats for timeit.
N_ITERATIONS = 50  # Number of iterations per repeat.
age_min, age_max = 30, 50  # Filtering parameters.


class Sex(Enum):
    FEMALE = "female"
    MALE = "male"


@dataclass
class Human:
    """Representation of a human."""

    name: str
    age: int
    sex: Sex
    height: int
    weight: int


def make_random_human(name: Any) -> Human:
    """Generate a random human."""
    return Human(
        name=name,
        age=randint(20, 80),
        sex=choice((Sex.FEMALE, Sex.MALE)),
        height=randint(160, 210),
        weight=randint(60, 80),
    )


def generate_humans(number: int) -> list[Human]:
    """Generate a set of random humans."""
    seed(0)
    return [make_random_human(i) for i in range(number)]


# ---------------------------------------------------------------------------
# Generic benchmark runner
# ---------------------------------------------------------------------------


def run_benchmark(
    operation_fn: Callable[[Any], Any],
    data: Any,
    n_repeat: int = N_REPEAT,
    n_iterations: int = N_ITERATIONS,
) -> float:
    """
    Benchmark a single operation on pre-setup data.

    Returns the minimum average time per iteration (in seconds).
    """
    times = repeat(
        lambda: operation_fn(data),
        repeat=n_repeat,
        number=n_iterations,
    )
    return min(times) / n_iterations


# ---------------------------------------------------------------------------
# Version info
# ---------------------------------------------------------------------------


def tested_version() -> str:
    """Return a string with versions of used packages for testing."""
    return f"python {python_ver}\n{project_name.replace(' ', '_')} {smort_ver}"


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

# Color palette for up to 7 engines
ENGINE_COLORS = [
    "#2196F3",  # blue - ObjectQuery
    "#FF9800",  # orange - pandas
    "#4CAF50",  # green - list comprehension
    "#9C27B0",  # purple - filter+lambda
    "#F44336",  # red - SQLite
    "#00BCD4",  # cyan - DuckDB
    "#795548",  # brown - polars
]

ENGINE_MARKERS = ["o", "s", "^", "D", "v", "P", "X"]


def plot_results(
    sizes: list[int],
    results: dict[str, dict[str, list[float]]],
    version_info: str,
) -> plt.Figure:
    """
    Plot benchmark results.

    Parameters
    ----------
    sizes : list[int]
        Dataset sizes used in the benchmark.
    results : dict[str, dict[str, list[float]]]
        Nested dict: results[operation_name][engine_name] = [times...]
    version_info : str
        Version string for the legend.

    Returns
    -------
    matplotlib Figure with one subplot per operation.
    """
    operations = list(results.keys())
    n_ops = len(operations)

    fig, axes = plt.subplots(1, n_ops, figsize=(6 * n_ops, 5), squeeze=False)
    fig.suptitle(
        f"{project_name.title().replace(' ', '')} -- Benchmark",
        fontsize=16,
        fontweight="bold",
    )

    # Collect all engine names (preserving order from first operation)
    all_engines: list[str] = []
    for op_data in results.values():
        for eng_name in op_data:
            if eng_name not in all_engines:
                all_engines.append(eng_name)

    # Build a color/marker map
    color_map = {
        eng: ENGINE_COLORS[i % len(ENGINE_COLORS)] for i, eng in enumerate(all_engines)
    }
    marker_map = {
        eng: ENGINE_MARKERS[i % len(ENGINE_MARKERS)]
        for i, eng in enumerate(all_engines)
    }

    for col, op_name in enumerate(operations):
        ax = axes[0][col]
        op_data = results[op_name]

        for eng_name, times in op_data.items():
            ax.plot(
                sizes,
                times,
                marker=marker_map[eng_name],
                linestyle="--",
                color=color_map[eng_name],
                label=eng_name,
                markersize=6,
                linewidth=1.5,
            )

        ax.set_title(op_name, fontsize=13)
        ax.set_xlabel("Number of objects", fontsize=11)
        if col == 0:
            ax.set_ylabel("Time [s]", fontsize=11)
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, title=version_info, title_fontsize=6)

    fig.tight_layout()
    return fig
