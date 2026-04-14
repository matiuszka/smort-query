from collections.abc import Iterable, Iterator
from random import shuffle

import pytest

from smort_query import OQ, ObjectQuery

from .conftest import Asset


class TestInit:
    def test_initialized_by_iterable(self):
        oq = ObjectQuery(list(range(10)))

        assert isinstance(oq.objects_source, Iterator)

    def test_initialized_by_iterator(self):
        oq = ObjectQuery(iter(list(range(10))))

        assert isinstance(oq.objects_source, Iterator)

    def test_type_error(self):
        with pytest.raises(TypeError):
            ObjectQuery(object())


class TestRepr:
    def test_repr_contains_class_name(self):
        query = ObjectQuery(range(10))

        assert "ObjectQuery" in repr(query)

    def test_repr_format(self):
        query = ObjectQuery(range(10))

        result = repr(query)

        assert result.startswith("<ObjectQuery")
        assert result.endswith(">")


class TestOQAlias:
    def test_oq_is_object_query(self):
        assert OQ is ObjectQuery

    def test_oq_works(self):
        result = list(OQ(range(5)))

        assert result == [0, 1, 2, 3, 4]


class TestIteration:
    def test_iterable(self):
        oq = ObjectQuery([])

        assert isinstance(oq, Iterable)

    def test_iterator(self):
        oq = ObjectQuery([])

        assert isinstance(oq, Iterator)

    def test_iteration(self):
        oq = ObjectQuery(range(10))

        for x, y in zip(oq, range(10), strict=False):
            assert x == y

    def test_stop_iteration_on_exhausted(self):
        query = ObjectQuery(range(1))

        next(query)

        with pytest.raises(StopIteration):
            next(query)


class TestLen:
    def test_len(self):
        listt = [1]
        list_iter = iter(listt)
        query = ObjectQuery(list_iter)

        assert len(query) == len(listt)

        with pytest.raises(StopIteration):
            next(list_iter)

    def test_len_uses_cache(self):
        query = ObjectQuery(range(10))

        assert len(query) == 10
        # Second call should use cache and return the same result
        assert len(query) == 10
        # Iterator should still work after cached len
        assert list(query) == list(range(10))


class TestGetItem:
    def test_get_item(self):
        query = ObjectQuery(range(10))

        assert query[5] == 5

    def test_slice(self):
        query = ObjectQuery(range(10))

        assert list(query[5:0:-1]) == list(range(10))[5:0:-1]

    def test_get_item_uses_cache(self):
        query = ObjectQuery(range(10))

        assert query[5] == 5
        # Second call should use cache
        assert query[3] == 3
        assert query[9] == 9

    def test_len_then_getitem(self):
        query = ObjectQuery(range(10))

        assert len(query) == 10
        # After len, getitem should use the same cache
        assert query[5] == 5
        assert query[0] == 0


class TestAll:
    def test_all(self):
        query1 = ObjectQuery(range(10))
        query2 = query1.all()

        assert list(query1) == list(query2)


# ---- Filter & Exclude: parametrized over comparator --------------------


class TestFilter:
    def test_no_lookup(self, id_items):
        assert list(ObjectQuery(id_items).filter()) == id_items

    def test_not_suppported_attribute(self, id_items):
        with pytest.raises(AttributeError):
            list(ObjectQuery(id_items).filter(not_suppported_attribute=0))

    @pytest.mark.parametrize(
        "lookup, expected_ids",
        [
            ({"id": 0}, [0, 0]),
            ({"id__eq": 0}, [0, 0]),
            ({"id__exact": 0}, [0, 0]),
        ],
        ids=["implicit_eq", "explicit_eq", "exact"],
    )
    def test_equality_lookups(self, id_items, lookup, expected_ids):
        result = list(ObjectQuery(id_items).filter(**lookup))

        assert [r.id for r in result] == expected_ids

    @pytest.mark.parametrize(
        "lookup, expected_ids",
        [
            ({"id__lt": 1}, [0]),
            ({"id__le": 1}, [0, 1]),
            ({"id__lte": 1}, [0, 1]),
            ({"id__gt": 1}, [2]),
            ({"id__ge": 1}, [1, 2]),
            ({"id__gte": 1}, [1, 2]),
        ],
        ids=["lt", "le", "lte", "gt", "ge", "gte"],
    )
    def test_comparison_lookups(self, ordered_items, lookup, expected_ids):
        result = list(ObjectQuery(ordered_items).filter(**lookup))

        assert [r.id for r in result] == expected_ids

    def test_in(self, ordered_items):
        result = list(ObjectQuery(ordered_items).filter(id__in=[1, 2]))

        assert [r.id for r in result] == [1, 2]

    def test_contains(self, seq_items):
        assert list(ObjectQuery(seq_items).filter(seq__contains=3)) == [
            seq_items[1],
        ]

    def test_combining_lookups(self):
        items = [
            Asset(id=0, seq=[0]),
            Asset(id=1, seq=(0, 0, 0xFF, 0, 0, 0, 0, 0)),
            Asset(id=1, seq=[0]),
        ]

        assert list(ObjectQuery(items).filter(id=1, seq__contains=0xFF)) == [
            items[1],
        ]

    def test_empty_source(self):
        assert list(ObjectQuery([]).filter(id=0)) == []


class TestExclude:
    def test_no_lookup(self, id_items):
        assert list(ObjectQuery(id_items).exclude()) == id_items

    def test_not_suppported_attribute(self, id_items):
        with pytest.raises(AttributeError):
            list(ObjectQuery(id_items).exclude(not_suppported_attribute=0))

    @pytest.mark.parametrize(
        "lookup, expected_ids",
        [
            ({"id": 0}, [1]),
            ({"id__eq": 0}, [1]),
            ({"id__exact": 0}, [1]),
        ],
        ids=["implicit_eq", "explicit_eq", "exact"],
    )
    def test_equality_lookups(self, id_items, lookup, expected_ids):
        result = list(ObjectQuery(id_items).exclude(**lookup))

        assert [r.id for r in result] == expected_ids

    @pytest.mark.parametrize(
        "lookup, expected_ids",
        [
            ({"id__lt": 1}, [1, 2]),
            ({"id__le": 1}, [2]),
            ({"id__lte": 1}, [2]),
            ({"id__gt": 1}, [0, 1]),
            ({"id__ge": 1}, [0]),
            ({"id__gte": 1}, [0]),
        ],
        ids=["lt", "le", "lte", "gt", "ge", "gte"],
    )
    def test_comparison_lookups(self, ordered_items, lookup, expected_ids):
        result = list(ObjectQuery(ordered_items).exclude(**lookup))

        assert [r.id for r in result] == expected_ids

    def test_in(self, ordered_items):
        result = list(ObjectQuery(ordered_items).exclude(id__in=[1, 2]))

        assert [r.id for r in result] == [0]

    def test_contains(self):
        items = [
            Asset(id=0, seq=[0]),
            Asset(id=1, seq=tuple(range(8))),
            Asset(id=1, seq=[0]),
        ]

        assert list(ObjectQuery(items).exclude(seq__contains=3)) == [
            items[0],
            items[2],
        ]

    def test_combining_lookups(self):
        items = [
            Asset(id=0, seq=[0]),
            Asset(id=1, seq=(0, 0, 0xFF, 0, 0, 0, 0, 0)),
            Asset(id=1, seq=[0]),
        ]

        assert list(ObjectQuery(items).exclude(id=1, seq__contains=0xFF)) == [
            items[0],
        ]

    def test_empty_source(self):
        assert list(ObjectQuery([]).exclude(id=0)) == []


# ---- Ordering ----------------------------------------------------------


class TestObjectQueryOrdering:
    def test_ascending(self):
        input_items = [Asset(id=i) for i in range(10)]
        output_items = [Asset(id=i) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).order_by("id")) == output_items

    def test_descending(self):
        input_items = [Asset(id=i) for i in range(10)]
        output_items = [Asset(id=i) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).order_by("-id")) == list(
            reversed(output_items)
        )

    def test_multiple_fields(self):
        input_items = [Asset(id=0, sid=i) for i in range(10)]
        output_items = [Asset(id=0, sid=i) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).order_by("id", "sid")) == output_items

    def test_nested(self):
        input_items = [Asset(nested=Asset(id=i)) for i in range(10)]
        output_items = [Asset(nested=Asset(id=i)) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).order_by("nested__id")) == output_items

    def test_mixed_ascending_descending(self):
        """order_by with mixed asc/desc directions per attribute."""
        items = [
            Asset(group="a", value=2),
            Asset(group="b", value=1),
            Asset(group="a", value=1),
            Asset(group="b", value=2),
        ]

        result = list(ObjectQuery(items).order_by("group", "-value"))

        assert [(r.group, r.value) for r in result] == [
            ("a", 2),
            ("a", 1),
            ("b", 2),
            ("b", 1),
        ]

    def test_mixed_descending_ascending(self):
        """order_by with desc primary, asc secondary."""
        items = [
            Asset(group="a", value=2),
            Asset(group="b", value=1),
            Asset(group="a", value=1),
            Asset(group="b", value=2),
        ]

        result = list(ObjectQuery(items).order_by("-group", "value"))

        assert [(r.group, r.value) for r in result] == [
            ("b", 1),
            ("b", 2),
            ("a", 1),
            ("a", 2),
        ]

    def test_empty_source(self):
        assert list(ObjectQuery([]).order_by("id")) == []


class TestReversed:
    def test_reversed(self):
        query = ObjectQuery(range(10))

        assert list(query.reverse()) == list(reversed(range(10)))

    def test_reversed_empty(self):
        assert list(ObjectQuery([]).reverse()) == []


class TestAsc:
    def test_ascending_single(self):
        input_items = [Asset(id=i) for i in range(10)]
        output_items = [Asset(id=i) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).asc("id")) == output_items

    def test_ascending_multiple(self):
        input_items = [Asset(id=0, sid=i) for i in range(10)]
        output_items = [Asset(id=0, sid=i) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).asc("id", "sid")) == output_items

    def test_ascending_nested(self):
        input_items = [Asset(nested=Asset(id=i)) for i in range(10)]
        output_items = [Asset(nested=Asset(id=i)) for i in range(10)]

        shuffle(input_items)

        assert list(ObjectQuery(input_items).asc("nested__id")) == output_items


class TestDesc:
    def test_descending_single(self):
        input_items = [Asset(id=i) for i in range(10)]
        output_items = list(reversed([Asset(id=i) for i in range(10)]))

        shuffle(input_items)

        assert list(ObjectQuery(input_items).desc("id")) == output_items

    def test_descending_multiple(self):
        input_items = [Asset(id=0, sid=i) for i in range(10)]
        output_items = list(reversed([Asset(id=0, sid=i) for i in range(10)]))

        shuffle(input_items)

        assert list(ObjectQuery(input_items).desc("id", "sid")) == output_items

    def test_descending_nested(self):
        input_items = [Asset(nested=Asset(id=i)) for i in range(10)]
        output_items = list(reversed([Asset(nested=Asset(id=i)) for i in range(10)]))

        shuffle(input_items)

        assert list(ObjectQuery(input_items).desc("nested__id")) == output_items


# ---- Annotate ----------------------------------------------------------


class TestAnnotate:
    def test_flat_attribute(self):
        input_items = [Asset(id=i, sid=i) for i in range(10)]
        output_items = [Asset(id=i, sid=i, tid=i + i) for i in range(10)]

        assert (
            list(ObjectQuery(input_items).annotate(tid=lambda obj: obj.id + obj.sid))
            == output_items
        )

    def test_flat_multiple_attribute(self):
        input_items = [Asset(id=i, sid=i) for i in range(10)]
        output_items = [
            Asset(id=i, sid=i, tid=i + i, fid=(i + i) * 2) for i in range(10)
        ]

        assert (
            list(
                ObjectQuery(input_items).annotate(
                    tid=lambda obj: obj.id + obj.sid, fid=lambda obj: obj.tid * 2
                )
            )
            == output_items
        )

    def test_nested_attribute(self):
        input_items = [Asset(id=i, sid=i, nested=Asset(tid=0)) for i in range(10)]
        output_items = [Asset(id=i, sid=i, nested=Asset(tid=i + i)) for i in range(10)]

        assert (
            list(
                ObjectQuery(input_items).annotate(
                    nested__tid=lambda obj: obj.id + obj.sid
                )
            )
            == output_items
        )


# ---- Union & OR --------------------------------------------------------


class TestUnion:
    def test_union(self):
        q1 = ObjectQuery(range(10))
        q2 = ObjectQuery(range(10))

        assert list(q1.union(q2)) == list(range(10)) + list(range(10))

    def test_union_empty(self):
        q1 = ObjectQuery(range(5))
        q2 = ObjectQuery([])

        assert list(q1.union(q2)) == list(range(5))


class TestOR:
    def test_or(self):
        q1 = ObjectQuery(range(10))
        q2 = ObjectQuery(range(10))

        assert list(q1 | q2) == list(range(10)) + list(range(10))


# ---- Unique ------------------------------------------------------------


class TestUniqueJustseen:
    def test_no_attributes(self):
        assert list(ObjectQuery([1, 1, 2, 2, 3, 1]).unique_justseen()) == [1, 2, 3, 1]

    def test_with_attribute(self):
        items = [
            Asset(id=0, name="a"),
            Asset(id=0, name="b"),
            Asset(id=1, name="c"),
            Asset(id=1, name="d"),
            Asset(id=0, name="e"),
        ]

        result = list(ObjectQuery(items).unique_justseen("id"))

        assert result == [items[0], items[2], items[4]]

    def test_with_nested_attribute(self):
        items = [
            Asset(nested=Asset(id=0)),
            Asset(nested=Asset(id=0)),
            Asset(nested=Asset(id=1)),
        ]

        result = list(ObjectQuery(items).unique_justseen("nested__id"))

        assert result == [items[0], items[2]]

    def test_empty(self):
        assert list(ObjectQuery([]).unique_justseen()) == []


class TestUniqueEverseen:
    def test_no_attributes(self):
        assert list(ObjectQuery([1, 1, 2, 2, 3, 1]).unique_everseen()) == [1, 2, 3]

    def test_with_attribute(self):
        items = [
            Asset(id=0, name="a"),
            Asset(id=0, name="b"),
            Asset(id=1, name="c"),
            Asset(id=1, name="d"),
            Asset(id=0, name="e"),
        ]

        result = list(ObjectQuery(items).unique_everseen("id"))

        assert result == [items[0], items[2]]

    def test_with_nested_attribute(self):
        items = [
            Asset(nested=Asset(id=0)),
            Asset(nested=Asset(id=1)),
            Asset(nested=Asset(id=0)),
        ]

        result = list(ObjectQuery(items).unique_everseen("nested__id"))

        assert result == [items[0], items[1]]

    def test_empty(self):
        assert list(ObjectQuery([]).unique_everseen()) == []


# ---- Intersection ------------------------------------------------------


class TestIntersection:
    def test_no_attributes(self):
        q1 = ObjectQuery([1, 2, 3, 4, 5])
        q2 = ObjectQuery([3, 4, 5, 6, 7])

        assert list(q1.intersection(q2)) == [3, 4, 5]

    def test_with_attribute(self):
        items1 = [Asset(id=0), Asset(id=1), Asset(id=2)]
        items2 = [Asset(id=1), Asset(id=2), Asset(id=3)]

        result = list(ObjectQuery(items1).intersection(ObjectQuery(items2), "id"))

        assert result == [items1[1], items1[2]]

    def test_no_overlap(self):
        q1 = ObjectQuery([1, 2, 3])
        q2 = ObjectQuery([4, 5, 6])

        assert list(q1.intersection(q2)) == []

    def test_empty(self):
        q1 = ObjectQuery([1, 2, 3])
        q2 = ObjectQuery([])

        assert list(q1.intersection(q2)) == []

    def test_with_nested_attribute(self):
        items1 = [Asset(nested=Asset(id=0)), Asset(nested=Asset(id=1))]
        items2 = [Asset(nested=Asset(id=1)), Asset(nested=Asset(id=2))]

        result = list(
            ObjectQuery(items1).intersection(ObjectQuery(items2), "nested__id")
        )

        assert result == [items1[1]]


# ---- Chained operations ------------------------------------------------


class TestChainedOperations:
    def test_filter_then_order_by(self):
        items = [Asset(id=i) for i in range(10)]
        shuffle(items)

        result = list(ObjectQuery(items).filter(id__gte=5).order_by("id"))

        assert [r.id for r in result] == [5, 6, 7, 8, 9]

    def test_filter_then_exclude(self):
        items = [Asset(id=i) for i in range(10)]

        result = list(ObjectQuery(items).filter(id__gte=3).exclude(id__gte=7))

        assert [r.id for r in result] == [3, 4, 5, 6]

    def test_filter_exclude_order_annotate(self):
        items = [Asset(id=i, value=i * 10) for i in range(10)]
        shuffle(items)

        result = list(
            ObjectQuery(items)
            .filter(id__gte=2)
            .exclude(id__gte=8)
            .order_by("-id")
            .annotate(doubled=lambda obj: obj.value * 2)
        )

        assert [r.id for r in result] == [7, 6, 5, 4, 3, 2]
        assert [r.doubled for r in result] == [140, 120, 100, 80, 60, 40]

    def test_order_by_then_unique_justseen(self):
        items = [
            Asset(id=1, group="a"),
            Asset(id=2, group="b"),
            Asset(id=3, group="a"),
            Asset(id=4, group="b"),
        ]

        result = list(ObjectQuery(items).order_by("group").unique_justseen("group"))

        assert [r.group for r in result] == ["a", "b"]

    def test_union_then_filter(self):
        q1 = ObjectQuery([Asset(id=1), Asset(id=2)])
        q2 = ObjectQuery([Asset(id=3), Asset(id=4)])

        result = list((q1 | q2).filter(id__gte=3))

        assert [r.id for r in result] == [3, 4]


# ---- Nested lookup in filter/exclude ----------------------------------


class TestNestedLookups:
    def test_filter_nested_attribute(self):
        items = [
            Asset(nested=Asset(id=0)),
            Asset(nested=Asset(id=5)),
            Asset(nested=Asset(id=10)),
        ]

        result = list(ObjectQuery(items).filter(nested__id__gt=3))

        assert result == [items[1], items[2]]

    def test_exclude_nested_attribute(self):
        items = [
            Asset(nested=Asset(id=0)),
            Asset(nested=Asset(id=5)),
            Asset(nested=Asset(id=10)),
        ]

        result = list(ObjectQuery(items).exclude(nested__id__gt=3))

        assert result == [items[0]]
