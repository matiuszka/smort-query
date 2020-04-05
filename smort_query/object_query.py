import operator
from itertools import chain, tee
from typing import Any, Iterable, Iterator, Tuple, Union

from more_itertools import islice_extended


class ObjectQuery:
    """
    Lazy evaluated query implementation for searching through Python objects
    inspired by Django QuerySets.

    Attributes
    ----------
    object_source: Iterator
        Source of objects as iterator used for creation of new queries.

    """

    _COMPARATORS = {
        "exact": operator.eq,
        "eq": operator.eq,
        "in": lambda x, y: x in y,
        "contains": operator.contains,
        "gt": operator.gt,
        "gte": operator.ge,
        "ge": operator.ge,
        "lt": operator.lt,
        "lte": operator.le,
        "le": operator.le,
    }

    def __init__(self, objects: Union[Iterator, Iterable]) -> None:
        """
        Initializes objects by passing either an iterator or an iterable.

        Parameters
        ----------
        objects: Union[Iterator, Iterable]
            Objects that will be used as source of query.

        Raises
        ------
        TypeError
            When passed `objects` parameter is neither iterator not iterable.

        """
        self.objects_source: Iterator

        if isinstance(objects, Iterable):
            self.objects_source = iter(objects)
        elif isinstance(objects, Iterable):
            self.objects_source = objects
        else:
            raise TypeError(
                f"The objects parameter has to be an iterator or an iterable,\
                  but is {type(objects)}."
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.objects_source}>"

    def __iter__(self) -> "ObjectQuery":
        """
        Makes it an iterable.

        Returns
        -------
        ObjectQuery
            Returns itself.

        """
        return self

    def __next__(self) -> Any:
        """
        Produces object from object_source. It evaluates query.

        Returns
        -------
        `Any`
            Anything that was in object_source.

        Examples
        --------
        >>> query = ObjectQuery(range(2))
        >>> next(query)
        0
        >>> next(query)
        1
        >>> next(query)
        >>> next(query)
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "object_query.py", line 95, in __next__
            return next(self.objects_source)
        StopIteration

        """
        return next(self.objects_source)

    def __len__(self) -> int:
        """
        Return number of items in query. It evaluates query.

        Returns
        -------
        int
            Number of items in query.

        Examples
        --------
        >>> query = ObjectQuery(range(10))
        >>> len(query)
        10

        """
        return len(self._evaluate_query())

    def __getitem__(self, key: Union[int, slice]) -> Union[Any, "ObjectQuery"]:
        """
        If key is an integer it evaluates query and returns item.
        If key is a slice it returns another unevaluated ObjectQuery.

        Parameters
        ----------
        key: Union[int, slice]
            Key represents index of item or slice object.

        Examples
        --------
        >>> ObjectQuery(range(10))[5]
        5
        >>> list(ObjectQuery(range(10))[5:0:-1])
        [5, 4, 3, 2, 1]

        """
        if isinstance(key, slice):
            return self.__class__(
                islice_extended(self.objects_source, key.start, key.stop, key.step)
            )

        return self._evaluate_query()[key]

    def __or__(self, other: "ObjectQuery") -> "ObjectQuery":
        """
        Chains two queries by creating new one.

        Parameters
        ----------
        other: ObjectQuery
            Query that will be attached to the end of current query.

        Returns
        -------
        ObjectQuery
            New query combined from current and new query.

        """
        copy = self._copy()
        copy.objects_source = chain(copy.objects_source, other._copy())

        return copy

    @staticmethod
    def _setattr(obj: Any, attr: str, value: Any) -> None:
        """
        Recursively sets attrbiutes for objects.
        Each nested object has to be separated by `__` signs.

        """
        current_attr, _, nested_attr = attr.rpartition("__")
        getter = operator.attrgetter(current_attr)

        return setattr(getter(obj) if current_attr else obj, nested_attr, value)

    @classmethod
    def _parse_lookup_string(cls, lookup_string: str) -> Tuple[callable, callable]:
        """
        Parses lookup string into getter function and comparator function.

        Returns
        -------
        Tuple[callable, callable]
            Getter function and coparator.

        """
        *lookup_parts, comparator_candidate = lookup_string.split("__")
        comparator = operator.eq

        if comparator_candidate in cls._COMPARATORS:
            comparator = cls._COMPARATORS.get(comparator_candidate)
        else:
            lookup_parts.append(comparator_candidate)

        return operator.attrgetter(".".join(lookup_parts)), comparator

    @classmethod
    def _filter_or_exclude(
        cls, objects_source: Iterator, negate: bool, **lookups: dict
    ) -> Iterator:
        """
        Yields objects that match or does not match(depends on `negate`) lookups from
        `objects_source`.

        Parameters
        ----------
        objects_source: Iterator
            Source of objects to be filtered.
            We are passing it explicitly here to save context of generators, otherwise
            we might end up with 'generator already executing' thing.
        negate: bool
            Tells if object have to match `lookups` or not.
        **lookups: dict
            Object lookups passed as key words. Argument name is taken as lookup string
            for attribute and comparator extraction which will be used at the end to
            compare against argument value.

        Raises
        ------
        AttributeError
            When lookup string cannot be properly resolved on objects.

        """
        for obj in objects_source:
            for lookup_string, value in lookups.items():
                getter, comparator = cls._parse_lookup_string(lookup_string)

                try:
                    if comparator(getter(obj), value) is negate:
                        break
                except AttributeError:
                    raise AttributeError(
                        f"The '{lookup_string}' is not valid attribute for {obj}."
                    )
            else:
                yield obj

    def _copy(self) -> "ObjectQuery":
        """
        Makes copy of current object. Used for creation new queries

        Returns
        -------
        ObjectQuery
            Brand new query.

        """
        self.objects_source, copy = tee(self.objects_source)
        return self.__class__(copy)

    def _evaluate_query(self) -> list:
        """
        Evaluates query and saves iterator.

        Return
        ------
        list
            Evaluated query.

        """
        evaluated_query = list(self.objects_source)
        self.objects_source = iter(evaluated_query)

        return evaluated_query

    def all(self) -> "ObjectQuery":
        """
        Returns a copy of current query.

        Returns
        -------
        ObjectQuery
            Copy of query.

        Examples
        --------
        >>> query = ObjectQuery(range(10))
        >>> list(query.all())
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> list(query)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        """
        return self._copy()

    def filter(self, **lookups: dict) -> "ObjectQuery":
        """
        Filters objects by passed `lookups` and creates new query from it.

        Parameters
        ----------
        **lookups: dict
            Argument name is taken as lookup string to properly extract object
            attribute. Attributes might be nested, you have to separate them by `__`
            characters. If you want to specify comparator function you can pass it also
            separeted by `__`.

        Returns
        -------
        ObjectQuery
            New query created from filtered objects.

        """
        copy = self._copy()
        copy.objects_source = copy._filter_or_exclude(
            objects_source=copy.objects_source, negate=False, **lookups
        )

        return copy

    def exclude(self, **lookups: dict) -> "ObjectQuery":
        """
        Excludes objects that match passed `lookups`.

        Parameters
        ----------
        **lookups: dict
            Argument name is taken as lookup string to properly extract object
            attribute. Attributes might be nested, you have to separate them by `__`
            characters. If you want to specify comparator function you can pass it also
            separeted by `__`.

        Returns
        -------
        ObjectQuery
            New query created from excluded objects.

        """
        copy = self._copy()
        copy.objects_source = self._filter_or_exclude(
            objects_source=copy.objects_source, negate=True, **lookups
        )

        return copy

    def order_by(self, *attributes: tuple) -> "ObjectQuery":
        """
        Sorts query in order of chosen attributes passed as `attributes` parameter.

        Parameters
        ----------
        *attributes: tuple
            Attributes that will be used for ordering. Addint `-` sign at prefix makes
            ordering descending, ascending otherwise.

        Returns
        -------
        ObjectQuery
            New query created from ordered objects.

        """
        attrs = []
        reverse = False
        copy = self._copy()

        for attr in attributes:
            if attr.startswith("-"):
                attr = attr.lstrip("-")
                reverse = True

            attrs.append(attr.replace("__", "."))

        getter = operator.attrgetter(*attrs)
        copy.objects_source = sorted(
            copy.objects_source, key=lambda obj: getter(obj), reverse=reverse
        )

        return copy

    def reverse(self) -> "ObjectQuery":
        """
        Creates a new reversed query. Unfortunately we cannot reverse iterator without
        evaluating it whole. So if you need to please do it at last step in chain.

        Returns
        -------
        ObjectQuery
            Query with reversed objects.

        """
        copy = self._copy()
        copy.objects_source = reversed(tuple(copy.objects_source))

        return copy

    def annotate(self, **annotations: dict) -> "ObjectQuery":
        """
        Calculates and sets new attributes by passed callables.
        New attribute name is taken from key attribute name.
        Since annotations are calculated one by one, next annotations have access
        to previously calculated attributes.

        Parameters
        ----------
        **annotations: dict
            Attribute name is taken as new name for object attribute.
            Value is taken as callable for calculating attribute value.
            Nested attributes have to be divided by `__` signs.

        Returns
        -------
        ObjectQuery
            Query with calculated annotations.

        """
        copy = self._copy()
        copy.objects_source = (
            obj
            for obj in copy.objects_source
            if all(
                self._setattr(obj, attr, call(obj)) is None
                for attr, call in annotations.items()
            )
        )

        return copy

    def union(self, other: "ObjectQuery") -> "ObjectQuery":
        """
        Chains two queries by creating new one. Same as OR.

        Parameters
        ----------
        other: ObjectQuery
            Query that will be attached to the end of current query.

        Returns
        -------
        ObjectQuery
            New query combined from current and new query.

        """
        return self | other
