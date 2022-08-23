from random import shuffle
from typing import Iterable, Iterator

import pytest
from smort_query import ObjectQuery


class Asset:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        for (dk1, dk1v), (dk2, dk2v) in zip(
            self.__dict__.items(), other.__dict__.items()
        ):
            if dk1 != dk2 or dk1v != dk2v:
                break
        else:
            return True

        return False


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


class TestIteration:
    def test_iterable(self):
        oq = ObjectQuery([])

        assert isinstance(oq, Iterable)

    def test_iterator(self):
        oq = ObjectQuery([])

        assert isinstance(oq, Iterator)

    def test_iteration(self):
        oq = ObjectQuery(range(10))

        for x, y in zip(oq, range(10)):
            assert x == y


class TestLen:
    def test_len(self):
        listt = [1]
        list_iter = iter(listt)
        query = ObjectQuery(list_iter)

        assert len(query) == len(listt)

        with pytest.raises(StopIteration):
            next(list_iter)


class TestGetItem:
    def test_get_item(self):
        query = ObjectQuery(range(10))

        assert query[5] == 5

    def test_slice(self):
        query = ObjectQuery(range(10))

        assert list(query[5:0:-1]) == list(range(10))[5:0:-1]


class TestAll:
    def test_all(self):
        query1 = ObjectQuery(range(10))
        query2 = query1.all()

        assert list(query1) == list(query2)


class TestFilter:
    def test_no_lookup(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).filter()) == items

    def test_not_suppported_attribute(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        with pytest.raises(AttributeError):
            list(ObjectQuery(items).filter(not_suppported_attribute=0))

    def test_implicit_eq(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).filter(id=0)) == [
            items[0],
            items[2],
        ]

    def test_explicit_eq(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).filter(id__eq=0)) == [
            items[0],
            items[2],
        ]

    def test_exact(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).filter(id__exact=0)) == [
            items[0],
            items[2],
        ]

    def test_lt(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__lt=1)) == [
            items[0],
        ]

    def test_le(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__le=1)) == [
            items[0],
            items[1],
        ]

    def test_lte(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__lte=1)) == [
            items[0],
            items[1],
        ]

    def test_gt(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__gt=1)) == [
            items[2],
        ]

    def test_ge(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__ge=1)) == [
            items[1],
            items[2],
        ]

    def test_gte(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__gte=1)) == [
            items[1],
            items[2],
        ]

    def test_in(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).filter(id__in=[1, 2])) == [
            items[1],
            items[2],
        ]

    def test_contains(self):
        items = [
            Asset(id=0, seq=[0]),
            Asset(id=1, seq=tuple(range(8))),
            Asset(id=2, seq=[0]),
        ]

        assert list(ObjectQuery(items).filter(seq__contains=3)) == [
            items[1],
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


class TestObjectQueryExclude:
    def test_no_lookup(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).exclude()) == items

    def test_not_suppported_attribute(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        with pytest.raises(AttributeError):
            list(ObjectQuery(items).exclude(not_suppported_attribute=0))

    def test_implicit_eq(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).exclude(id=0)) == [
            items[1],
        ]

    def test_explicit_eq(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).exclude(id__eq=0)) == [
            items[1],
        ]

    def test_exact(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=0),
        ]

        assert list(ObjectQuery(items).exclude(id__exact=0)) == [
            items[1],
        ]

    def test_lt(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__lt=1)) == [
            items[1],
            items[2],
        ]

    def test_le(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__le=1)) == [
            items[2],
        ]

    def test_lte(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__lte=1)) == [
            items[2],
        ]

    def test_gt(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__gt=1)) == [
            items[0],
            items[1],
        ]

    def test_ge(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__ge=1)) == [
            items[0],
        ]

    def test_gte(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__gte=1)) == [
            items[0],
        ]

    def test_in(self):
        items = [
            Asset(id=0),
            Asset(id=1),
            Asset(id=2),
        ]

        assert list(ObjectQuery(items).exclude(id__in=[1, 2])) == [
            items[0],
        ]

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


class TestReversed:
    def test_reversed(self):
        query = ObjectQuery(range(10))

        assert list(query.reverse()) == list(reversed(range(10)))


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


class TestUnion:
    def test_union(self):
        q1 = ObjectQuery(range(10))
        q2 = ObjectQuery(range(10))

        assert list(q1.union(q2)) == list(range(10)) + list(range(10))


class TestOR:
    def test_or(self):
        q1 = ObjectQuery(range(10))
        q2 = ObjectQuery(range(10))

        assert list(q1 | q2) == list(range(10)) + list(range(10))
