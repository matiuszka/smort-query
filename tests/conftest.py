import pytest


class Asset:
    def __init__(self, **attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    def __repr__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, Asset):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


@pytest.fixture
def id_items():
    """Three Assets with ids 0, 1, 0."""
    return [Asset(id=0), Asset(id=1), Asset(id=0)]


@pytest.fixture
def ordered_items():
    """Three Assets with ids 0, 1, 2."""
    return [Asset(id=0), Asset(id=1), Asset(id=2)]


@pytest.fixture
def seq_items():
    """Assets with id and seq attributes for contains/in tests."""
    return [
        Asset(id=0, seq=[0]),
        Asset(id=1, seq=tuple(range(8))),
        Asset(id=2, seq=[0]),
    ]
