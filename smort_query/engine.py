from __future__ import annotations

from itertools import tee
from typing import Any, Callable, Generic, Iterable, Iterator, TypeVar

__all__ = ["Query"]

ObjectType = TypeVar("ObjectType")
ObjectsSource = Iterable[ObjectType] | Iterator[ObjectType]


class Query(Generic[ObjectType]):
    """
    Lazy evaluated query implementation for searching through Python objects
    inspired by Django QuerySets:
    - https://docs.djangoproject.com/en/4.0/ref/models/querysets/#queryset-api

    The engine requires only `getattr` and `setattr` methods to know how to access
    attributes. This way it can work with `object.__getattribute__` or
    `dict.__getitem__`/`dict.__setitem__`.
    """

    def __init__(
        self,
        objects_source: ObjectsSource[ObjectType],
        getattr: Callable[[str, Any], Any] = object.__getattribute__,
        setattr: Callable[[str, Any, Any], None] = object.__setattr__,
    ) -> None:
        self.object_source: Iterator[ObjectType] = iter(objects_source)
        self.getattr = getattr
        self.setattr = setattr

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.object_source}>"

    def __iter__(self) -> Query[ObjectType]:
        """
        Turns Query into iterable.
        """
        return self

    def __next__(self) -> ObjectType:
        """
        Returns next object from object_source.

        Examples
        --------
        >>> query = Query(range(2))
        >>> next(query)
        0
        >>> next(query)
        1
        >>> next(query)
        >>> next(query)
        StopIteration
        """
        return next(self.object_source)

    def __len__(self) -> int:
        """
        Return number of items in query.

        .. warning::
            It evaluates the query.

        Examples
        --------
        >>> query = Query(range(10))
        >>> len(query)
        10

        """
        return len(self._evaluate_query())

    def _evaluate_query(self) -> list[ObjectType]:
        """
        Evaluates the query and saves new iterator.

        """
        evaluated_query = list(self.object_source)
        self.object_source = iter(evaluated_query)

        return evaluated_query

    def _copy(self) -> Query[ObjectType]:
        """
        Makes a copy of current object source. Used for creation new queries.

        It is important that we are not evaluating the iterators.

        """
        original_objects_source, copied_objects_source = tee(self.object_source)

        # We need to replace original iterator with new one.
        self.object_source = original_objects_source

        # Create an instance of new Query based on newly created iterator.
        return self.__class__(
            copied_objects_source,
            getattr=self.getattr,
            setattr=self.setattr,
        )
