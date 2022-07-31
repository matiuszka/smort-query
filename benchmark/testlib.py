"""
Auxiliary library for benchmark tests.

"""
__all__ = [
    "execute_data_frame",
    "execute_object_query",
    "plot_results",
    "python_ver",
    "setup_test_objects",
    "test_filtering",
    "tested_version",
]

from dataclasses import dataclass
from enum import Enum
from random import choice, randint, seed
from sys import version
from textwrap import dedent
from timeit import repeat
from typing import Callable, List

import matplotlib.pyplot as plt
from pandas import DataFrame
from pandas import __version__ as pd_ver
from smort_query import ObjectQuery
from smort_query import __version__ as smort_ver

from benchmark import project_name

python_ver = version.split()[0]
N_it = 100  # Number of iterations for repeat function.
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


def make_random_human(name):
    """Generate a random human."""
    return Human(
        name=name,
        age=randint(20, 80),
        sex=choice((Sex.FEMALE, Sex.MALE)),
        height=randint(160, 210),
        weight=randint(60, 80),
    )


def generate_humans(number):
    """Generate a set of random humans."""
    seed(0)
    return [make_random_human(i) for i in range(number)]


def setup_test_objects(number: int) -> str:
    """Command to set up test objects."""
    return f"humans = generate_humans({number})"


def execute_object_query() -> str:
    """Command to execute ObjectQuery."""
    snippet = f"""\
    oq = ObjectQuery(humans)
    df_filter = DataFrame(data=oq.filter(age__ge={age_min}, age__le={age_max}))
    """
    return dedent(snippet)


def execute_data_frame() -> str:
    """Command to execute DataFrame object."""
    snippet = f"""\
    df = DataFrame(data=humans)
    df_filter = df[(df['age'] >= {age_min}) & (df['age'] <= {age_max})]
    """
    return dedent(snippet)


def test_filtering(number: int, setup: Callable, execute_code: Callable) -> float:
    """Test efficiency of filtering by different objects for a given number of items to filter."""
    setup_code = setup(number)
    test_code = execute_code()
    time_execution = repeat(
        setup=setup_code, stmt=test_code, repeat=3, number=N_it, globals=globals()
    )

    return min(time_execution) / N_it


def tested_version() -> str:
    """Return a string with versions of used packages for testing."""
    versions = dedent(
        f"""\
    - python {python_ver}
    - {project_name.replace(' ', '_')} {smort_ver}
    - pandas {pd_ver}
    """
    )
    return versions


def plot_results(
    size: list, title: str, version: str, **kwargs: List[float]
) -> plt.Figure:
    """Plot comparison of time execution for two different objects with variable size of input data."""
    colors = ("blue", "orange")

    fig, ax = plt.subplots()
    fig.set_size_inches(12, 5)
    ax.set_title(title, {"fontsize": 20})
    ax.set_xlabel("Number of rows", fontsize=15)
    ax.set_ylabel("Execution time [s]", fontsize=15)
    ax.tick_params(axis="both", labelsize=12)
    for performance, color in zip(kwargs, colors):
        ax.plot(size, kwargs[performance], "o--", color=color, label=performance)
    ax.legend(title=version, title_fontsize="small")

    return fig
