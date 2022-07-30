"""
Auxiliary library for benchmark tests.

"""
__all__ = [
    "execute_data_frame",
    "execute_object_query",
    "setup_test_objects",
    "test_filtering",
]

from dataclasses import dataclass
from enum import Enum
from random import choice, randint, seed
from textwrap import dedent
from timeit import repeat
from typing import Callable

from pandas import DataFrame

from smort_query import ObjectQuery

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
