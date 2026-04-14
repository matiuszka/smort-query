"""
Benchmark engine implementations.

Each engine class provides a uniform interface for benchmarking:
- setup(humans): prepare data structures from a list of Human objects
- filter(data): filter where 30 <= age <= 50
- sort(data): sort by age ASC, weight DESC
- chain_ops(data): filter + sort combined
- unique(data): unique by age
- materialize(data): full materialization of the dataset
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from typing import Any

import duckdb
import pandas as pd
import polars as pl

from smort_query import ObjectQuery

from benchmark.testlib import Human, age_max, age_min

# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class Engine(ABC):
    """Base class for benchmark engines."""

    name: str

    @abstractmethod
    def setup(self, humans: list[Human]) -> Any:
        """Prepare engine-specific data structure from list of Human objects."""

    @abstractmethod
    def filter(self, data: Any) -> Any:
        """Filter: age >= age_min AND age <= age_max. Must return materialised result."""

    @abstractmethod
    def sort(self, data: Any) -> Any:
        """Sort by age ASC, weight DESC. Must return materialised result."""

    @abstractmethod
    def chain_ops(self, data: Any) -> Any:
        """Filter + sort combined. Must return materialised result."""

    @abstractmethod
    def unique(self, data: Any) -> Any:
        """Unique by age. Must return materialised result."""

    @abstractmethod
    def materialize(self, data: Any) -> Any:
        """Full iteration / materialisation of all data. Must return materialised result."""


# ---------------------------------------------------------------------------
# 1. ObjectQuery (smort-query)
# ---------------------------------------------------------------------------


class ObjectQueryEngine(Engine):
    name = "ObjectQuery"

    def setup(self, humans: list[Human]) -> list[Human]:
        return humans

    def filter(self, data: list[Human]) -> list[Human]:
        return list(ObjectQuery(data).filter(age__ge=age_min, age__le=age_max))

    def sort(self, data: list[Human]) -> list[Human]:
        return list(ObjectQuery(data).order_by("age", "-weight"))

    def chain_ops(self, data: list[Human]) -> list[Human]:
        return list(
            ObjectQuery(data)
            .filter(age__ge=age_min, age__le=age_max)
            .order_by("age", "-weight")
        )

    def unique(self, data: list[Human]) -> list[Human]:
        return list(ObjectQuery(data).unique_everseen("age"))

    def materialize(self, data: list[Human]) -> list[Human]:
        return list(ObjectQuery(data))


# ---------------------------------------------------------------------------
# 2. pandas DataFrame
# ---------------------------------------------------------------------------


class PandasEngine(Engine):
    name = "pandas"

    def setup(self, humans: list[Human]) -> pd.DataFrame:
        return pd.DataFrame([h.__dict__ for h in humans])

    def filter(self, data: pd.DataFrame) -> pd.DataFrame:
        return data[(data["age"] >= age_min) & (data["age"] <= age_max)]

    def sort(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.sort_values(["age", "weight"], ascending=[True, False])

    def chain_ops(self, data: pd.DataFrame) -> pd.DataFrame:
        filtered = data[(data["age"] >= age_min) & (data["age"] <= age_max)]
        return filtered.sort_values(["age", "weight"], ascending=[True, False])

    def unique(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop_duplicates(subset=["age"])

    def materialize(self, data: pd.DataFrame) -> list:
        return data.to_dict("records")


# ---------------------------------------------------------------------------
# 3. Pure Python (list comprehension)
# ---------------------------------------------------------------------------


class ListCompEngine(Engine):
    name = "list_comprehension"

    def setup(self, humans: list[Human]) -> list[Human]:
        return humans

    def filter(self, data: list[Human]) -> list[Human]:
        return [h for h in data if age_min <= h.age <= age_max]

    def sort(self, data: list[Human]) -> list[Human]:
        return sorted(data, key=lambda h: (h.age, -h.weight))

    def chain_ops(self, data: list[Human]) -> list[Human]:
        filtered = [h for h in data if age_min <= h.age <= age_max]
        return sorted(filtered, key=lambda h: (h.age, -h.weight))

    def unique(self, data: list[Human]) -> list[Human]:
        seen: set[int] = set()
        result: list[Human] = []
        for h in data:
            if h.age not in seen:
                seen.add(h.age)
                result.append(h)
        return result

    def materialize(self, data: list[Human]) -> list[Human]:
        return list(data)


# ---------------------------------------------------------------------------
# 4. filter() + lambda
# ---------------------------------------------------------------------------


class FilterLambdaEngine(Engine):
    name = "filter_lambda"

    def setup(self, humans: list[Human]) -> list[Human]:
        return humans

    def filter(self, data: list[Human]) -> list[Human]:
        return list(filter(lambda h: age_min <= h.age <= age_max, data))

    def sort(self, data: list[Human]) -> list[Human]:
        return sorted(data, key=lambda h: (h.age, -h.weight))

    def chain_ops(self, data: list[Human]) -> list[Human]:
        filtered = list(filter(lambda h: age_min <= h.age <= age_max, data))
        return sorted(filtered, key=lambda h: (h.age, -h.weight))

    def unique(self, data: list[Human]) -> list[Human]:
        seen: set[int] = set()
        result: list[Human] = []
        for h in data:
            if h.age not in seen:
                seen.add(h.age)
                result.append(h)
        return result

    def materialize(self, data: list[Human]) -> list[Human]:
        return list(data)


# ---------------------------------------------------------------------------
# 5. SQLite in-memory
# ---------------------------------------------------------------------------


class SQLiteEngine(Engine):
    name = "SQLite"

    def setup(self, humans: list[Human]) -> sqlite3.Connection:
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE humans "
            "(name TEXT, age INTEGER, sex TEXT, height INTEGER, weight INTEGER)"
        )
        conn.executemany(
            "INSERT INTO humans VALUES (?, ?, ?, ?, ?)",
            [(h.name, h.age, h.sex.value, h.height, h.weight) for h in humans],
        )
        conn.commit()
        return conn

    def filter(self, data: sqlite3.Connection) -> list:
        return data.execute(
            "SELECT * FROM humans WHERE age >= ? AND age <= ?",
            (age_min, age_max),
        ).fetchall()

    def sort(self, data: sqlite3.Connection) -> list:
        return data.execute(
            "SELECT * FROM humans ORDER BY age ASC, weight DESC"
        ).fetchall()

    def chain_ops(self, data: sqlite3.Connection) -> list:
        return data.execute(
            "SELECT * FROM humans WHERE age >= ? AND age <= ? "
            "ORDER BY age ASC, weight DESC",
            (age_min, age_max),
        ).fetchall()

    def unique(self, data: sqlite3.Connection) -> list:
        return data.execute("SELECT DISTINCT age FROM humans").fetchall()

    def materialize(self, data: sqlite3.Connection) -> list:
        return data.execute("SELECT * FROM humans").fetchall()


# ---------------------------------------------------------------------------
# 6. DuckDB in-memory
# ---------------------------------------------------------------------------


class DuckDBEngine(Engine):
    name = "DuckDB"

    def setup(self, humans: list[Human]) -> duckdb.DuckDBPyConnection:
        conn = duckdb.connect(":memory:")
        conn.execute(
            "CREATE TABLE humans "
            "(name VARCHAR, age INTEGER, sex VARCHAR, height INTEGER, weight INTEGER)"
        )
        conn.executemany(
            "INSERT INTO humans VALUES (?, ?, ?, ?, ?)",
            [(str(h.name), h.age, h.sex.value, h.height, h.weight) for h in humans],
        )
        return conn

    def filter(self, data: duckdb.DuckDBPyConnection) -> list:
        return data.execute(
            "SELECT * FROM humans WHERE age >= ? AND age <= ?",
            [age_min, age_max],
        ).fetchall()

    def sort(self, data: duckdb.DuckDBPyConnection) -> list:
        return data.execute(
            "SELECT * FROM humans ORDER BY age ASC, weight DESC"
        ).fetchall()

    def chain_ops(self, data: duckdb.DuckDBPyConnection) -> list:
        return data.execute(
            "SELECT * FROM humans WHERE age >= ? AND age <= ? "
            "ORDER BY age ASC, weight DESC",
            [age_min, age_max],
        ).fetchall()

    def unique(self, data: duckdb.DuckDBPyConnection) -> list:
        return data.execute("SELECT DISTINCT age FROM humans").fetchall()

    def materialize(self, data: duckdb.DuckDBPyConnection) -> list:
        return data.execute("SELECT * FROM humans").fetchall()


# ---------------------------------------------------------------------------
# 7. Polars
# ---------------------------------------------------------------------------


class PolarsEngine(Engine):
    name = "polars"

    def setup(self, humans: list[Human]) -> pl.DataFrame:
        return pl.DataFrame(
            {
                "name": [str(h.name) for h in humans],
                "age": [h.age for h in humans],
                "sex": [h.sex.value for h in humans],
                "height": [h.height for h in humans],
                "weight": [h.weight for h in humans],
            }
        )

    def filter(self, data: pl.DataFrame) -> pl.DataFrame:
        return data.filter((pl.col("age") >= age_min) & (pl.col("age") <= age_max))

    def sort(self, data: pl.DataFrame) -> pl.DataFrame:
        return data.sort(["age", "weight"], descending=[False, True])

    def chain_ops(self, data: pl.DataFrame) -> pl.DataFrame:
        return data.filter(
            (pl.col("age") >= age_min) & (pl.col("age") <= age_max)
        ).sort(["age", "weight"], descending=[False, True])

    def unique(self, data: pl.DataFrame) -> pl.DataFrame:
        return data.unique(subset=["age"])

    def materialize(self, data: pl.DataFrame) -> list:
        return data.to_dicts()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ALL_ENGINES: list[Engine] = [
    ObjectQueryEngine(),
    PandasEngine(),
    ListCompEngine(),
    FilterLambdaEngine(),
    SQLiteEngine(),
    DuckDBEngine(),
    PolarsEngine(),
]

ENGINE_MAP: dict[str, Engine] = {e.name: e for e in ALL_ENGINES}

OPERATION_NAMES = ["filter", "sort", "chain_ops", "unique", "materialize"]
