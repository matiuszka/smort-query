# Smort Query

[![PyPI version](https://badge.fury.io/py/smort-query.svg)](https://badge.fury.io/py/smort-query)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/smort-query.svg)](https://pypi.org/project/smort-query)
![Build Status](https://github.com/matiuszka/smort-query/actions/workflows/checks.yml/badge.svg)
[![codecov](https://codecov.io/gh/matiuszka/smort-query/branch/master/graph/badge.svg)](https://codecov.io/gh/matiuszka/smort-query)
[![PyPI download total](https://img.shields.io/pypi/dw/smort-query.svg)](https://pypi.python.org/pypi/smort-query/)

![alt text](https://media3.giphy.com/media/hFROvOhBPQVRm/giphy.gif "Smort")

Lazy evaluated query implementation for searching through Python objects
inspired by [Django QuerySets](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#queryset-api-reference).

- GitHub: https://github.com/matiuszka/smort-query
- PyPi: https://pypi.org/project/smort-query

## Rationale

In many moments of our programming tasks we have to filter iterables in
search of the right objects in right order.
I realized that most of the time code looks almost the same, but what kind of interface will be easiest to use? In that moment I figured out that [Django QuerySets](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#queryset-api-reference) implementation is kinda handy and well known.

So I decided to write small query engine that interface will be similar to Django one.
But it will work for Python objects. Additional assumption was that it will be lazy evaluated to
avoid memory consumption.

## Lookup format

Whole idea relies on keywords arguments naming format.
Let's consider following qualname `attr1.attr2` which can we used to get or set value for attribute.
This engine does things similarly but instead of separating by dot(`.`) we are separating by `__` signs.
So above example can be converted to keyword argument name like that `attr1__attr2`. Due to fact that we can't use `.` in argument names.

For some methods like `filter` and `exclude`, we can also specify comparator.
By default those methods are comparing against equality `==`. But we can easily change it.
If we want to compare by using `<=` we can use `__le` or `__lte` postfix.
So we will end up with argument name like `attr1__attr2__lt`.

All supported comparators are described here in [supported comparators](#supported-comparators) section.

## Installation

```console
pip install smort-query
```

## Importing

```python
from smort_query import ObjectQuery
# or by alias
from smort_query import OQ
```

## How it works?

### Basics

Each method in `ObjectQuery` produces new query. Which makes chaining very easy.
The most important thing is that `ObjectQuery` instances are unevaluated - it means that
they are not loading an objects to the memory even when we are chaining them.

Query sets can be evaluated in several ways:

- Iteration:

  ```python
  query = ObjectQuery(range(5))

  for obj in query:
      print(obj)

  """out:
  1
  2
  3
  4
  5
  """
  ```

- Checking length:

  ```python
  query = ObjectQuery(range(10))

  len(query)
  """out:
  10
  """
  ```

- Reversing query:

  ```python
  query = ObjectQuery(range(10))

  query.reverse()
  """out:
  <ObjectQuery for <reversed object at 0x04E8B460>>
  """

  list(list(query.reverse()))
  """out
  [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
  """
  ```

- Getting items:
  - Getting by index evaluates query:
    ```python
    query = ObjectQuery(range(10))
    query[5]
    """out:
    5
    """
    ```
  - But slices not! They creates another query.
    ```python
    query = ObjectQuery(range(10))
    query[5:0:-1]
    """out:
    <ObjectQuery for <generator object islice_extended at 0x0608B338>>
    """
    list(query[5:0:-1])
    """out:
    [5, 4, 3, 2, 1]
    """
    ```
- Initializing other objects that used iterators/iterables (it is still almost same mechanism like normal iteration):

  ```python
  query1 = ObjectQuery(range(10))
  query2 = ObjectQuery(range(10))

  list(query1)
  """out:
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  """
  tuple(query2)
  """out:
  (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
  """
  ```

### Use cases

Let's consider following code for populating faked humans:

```python
from random import randint, choice


class Human:
    def __init__(self, name, age, sex, height, weight):
        self.name = name
        self.age = age
        self.sex = sex
        self.height = height
        self.weight = weight

    def __repr__(self):
        return str(self.__dict__)


def make_random_human(name):
    return Human(
        name=name,
        age=randint(20, 80),
        sex=choice(('female', 'male')),
        height=randint(160, 210),
        weight=randint(60, 80),
    )
```

Creating 10 random humans:

```python
humans = [make_random_human(i) for i in range(10)]
"""out:
[{'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""
```

### Filtering and excluding

Finding people from age between [30; 75). To do that we will use specialized comparators:

```python
list(ObjectQuery(humans).filter(age__ge=30, age__lt=75))
"""out:
[{'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""
```

We can also exclude males in a similar way:

```python
list(ObjectQuery(humans).exclude(sex="male"))
"""out:
[{'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
 """
```

### Ordering

Ordering by `sex` attributes in ascending order:

```python
list(ObjectQuery(humans).order_by("sex"))
"""out
[{'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72}]
"""
```

Ordering by `sex` attributes in descending order:

```python
list(ObjectQuery(humans).order_by("-sex"))
"""out
[{'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""
```

Ordering by multiple attributes:

```python
list(ObjectQuery(humans).order_by("-sex", "height"))
"""out:
[{'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71}]
"""
```

### Annotate

If some attributes worth of filtering and ordering are not available by hand
we can calculate them on the fly:

```python
# Sorry for example if someone feels offended
root_query = ObjectQuery(humans)

only_females = root_query.filter(sex="female")  # reduce objects for annotation calculation
bmi_annotated_females = only_females.annotate(bmi=lambda obj: obj.weight / (obj.height / 100) ** 2)
overweight_females = bmi_annotated_females.filter(bmi__gt=25)
overweight_females_ordered_by_age = overweight_females.order_by("age")
list(overweight_females_ordered_by_age)
"""out:
[{'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71, 'bmi': 27.390918560240728},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75, 'bmi': 25.95155709342561},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78, 'bmi': 26.061679307694877}]
"""
```

### Copying

Each method query is returning copy.
Where iteration over newly created ones does not affect object sources.

```python
root_query = ObjectQuery(humans).filter(age__ge=30, age__lt=75)
query1 = root_query.filter(weight__gt=75)
query2 = root_query.filter(weight__in=[78, 62])

list(query1)
"""out:
[{'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""

list(query2)
"""out:
[{'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""

list(root_query)
"""out:
[{'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""
```

But sometimes evaluating some query in middle of chain may break it, so when you explicitly
want to save somewhere copy of query and be sure that further actions on `root` will not
affect on query, you can do:

```python
root_query = ObjectQuery(humans)
copy = root_query.all()
```

### Reversing

You can also reverse query, but remember that it will evaluate query:

```python
root_query = ObjectQuery(humans).reverse()
list(root_query)
"""out:
[{'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71}]
"""
```

### OR

Bitwise OR combines two queries together. Same as `union` method.
Note that after ORing two queries or even more, ordering might be needed:

```python
root_query = ObjectQuery(humans)
males = root_query.filter(sex="male")
females = root_query.filter(sex="female")
both1 = (males | females)
both2 = males.union(females)

list(both1)
"""out:
[{'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""
list(both2)
"""out:
[{'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78}]
"""
```

### Ascending and descending ordering

The `asc()` and `desc()` methods are shorthands for `order_by()` with a predefined direction:

```python
list(ObjectQuery(humans).asc("age"))
"""out:
[{'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77}]
"""

list(ObjectQuery(humans).desc("age"))
"""out:
[{'name': 5, 'age': 75, 'sex': 'male', 'height': 189, 'weight': 77},
 {'name': 4, 'age': 73, 'sex': 'male', 'height': 174, 'weight': 62},
 {'name': 6, 'age': 64, 'sex': 'male', 'height': 179, 'weight': 63},
 {'name': 8, 'age': 64, 'sex': 'male', 'height': 188, 'weight': 72},
 {'name': 3, 'age': 48, 'sex': 'female', 'height': 173, 'weight': 78},
 {'name': 2, 'age': 45, 'sex': 'female', 'height': 186, 'weight': 74},
 {'name': 9, 'age': 43, 'sex': 'female', 'height': 198, 'weight': 78},
 {'name': 7, 'age': 35, 'sex': 'female', 'height': 170, 'weight': 75},
 {'name': 1, 'age': 33, 'sex': 'female', 'height': 205, 'weight': 67},
 {'name': 0, 'age': 24, 'sex': 'female', 'height': 161, 'weight': 71}]
"""
```

### Removing duplicates

`unique_justseen()` removes consecutive duplicates, while `unique_everseen()` removes all duplicates keeping the first occurrence. Both accept optional attribute names for comparison:

```python
list(ObjectQuery([1, 1, 2, 2, 3, 1]).unique_justseen())
"""out:
[1, 2, 3, 1]
"""

list(ObjectQuery([1, 1, 2, 2, 3, 1]).unique_everseen())
"""out:
[1, 2, 3]
"""
```

With attribute-based comparison:

```python
root_query = ObjectQuery(humans)
# Remove consecutive duplicates by sex
list(root_query.unique_justseen("sex"))
# Remove all duplicates by sex (keeps first female and first male)
list(root_query.unique_everseen("sex"))
```

### Intersection

The `intersection()` method returns objects present in both queries.
Comparison can be done by equality or by specific attributes:

```python
young = ObjectQuery(humans).filter(age__lt=50)
tall = ObjectQuery(humans).filter(height__gt=180)

# Find young AND tall humans
list(young.intersection(tall))

# Or compare by specific attribute
q1 = ObjectQuery(humans)[:5]
q2 = ObjectQuery(humans)[3:]
list(q1.intersection(q2, "name"))
```

## Supported Comparators

Project supports many comparators that can be chosen as postfix for lookup:

- Default comparator is `eq`
- `eq` makes `a == b`
- `exact` makes `a == b`
- `in` makes `a in b`
- `contains` makes `b in a`
- `gt` makes `a > b`
- `gte` makes `a >= b`
- `ge` makes `a >= b`
- `lt` makes `a < b`
- `lte` makes `a <= b`
- `le` makes `a <= b`

## Performance & When to Use

ObjectQuery is designed for **developer ergonomics**, not raw speed. It trades
performance for a clean, Django-like API that works on arbitrary Python objects
without any data conversion step.

### Benchmark results (100 000 objects, Python 3.13)

| Operation | ObjectQuery | list comprehension | filter+lambda | pandas | polars | SQLite | DuckDB |
|---|---|---|---|---|---|---|---|
| **filter** | 74.8 ms | 4.3 ms | 5.2 ms | 0.6 ms | **0.2 ms** | 32.5 ms | 12.0 ms |
| **sort** | 26.5 ms | 37.5 ms | 37.6 ms | **2.3 ms** | 2.1 ms | 155.4 ms | 36.1 ms |
| **filter+sort** | 84.0 ms | 15.2 ms | 16.1 ms | 1.5 ms | **1.2 ms** | 55.4 ms | 13.6 ms |
| **unique** | 3.3 ms | 1.8 ms | 1.8 ms | **0.4 ms** | 0.5 ms | 14.4 ms | 1.0 ms |
| **materialize** | 4.1 ms | **0.3 ms** | 0.3 ms | 74.0 ms | 41.4 ms | 76.3 ms | 31.1 ms |

> Numbers are the best of 3 repeats, 50 iterations each. Benchmark source in
> `benchmark/`. Run with:
> `uv run python -m benchmark.benchmark_cli --size 100 1000 10000 100000 --print --img chart.png`

### When ObjectQuery is a good fit

- **Small to medium datasets (up to ~5 000 objects)** -- the overhead is
  negligible and you get a much more readable query pipeline than nested
  list comprehensions.
- **Working with rich domain objects** -- dataclasses, ORM-like models, nested
  attribute trees. No need to flatten your data into rows/columns first.
- **Lazy pipelines over iterators/generators** -- ObjectQuery never materializes
  intermediate results (except for sort/reverse), so it composes well with
  streaming data.
- **Prototyping and glue code** -- when developer time matters more than
  microseconds. The Django-like API is immediately familiar and self-documenting.
- **Zero-dependency contexts** -- the only runtime dependency is `more-itertools`.
  No C extensions, no compilation step, no heavy imports.

### When to reach for something else

- **Large datasets (50 000+ objects) with filtering** -- columnar engines like
  **polars** or **pandas** operate on contiguous memory in C/Rust and will be
  orders of magnitude faster. At 100k objects, polars filters ~370x faster.
- **Repeated analytical queries on the same data** -- if you load data once and
  query it many times, converting to a DataFrame upfront pays off quickly.
- **Sorting large collections** -- Python-level attribute access in a sort key
  does not scale well. pandas/polars sort 100k rows ~12x faster.
- **SQL-shaped problems** -- if your data fits naturally into tables with JOINs
  and GROUP BYs, use an actual database (SQLite, DuckDB). ObjectQuery does not
  support aggregation or joins.

### The tradeoff in one sentence

ObjectQuery gives you the **cleanest API** for querying Python objects at the
cost of being **pure-Python slow** -- choose it when readability and convenience
matter more than throughput.

## TODOs

- Sphinx documentation.

## Contribution

Any form of contribution is appreciated. Finding issues, new ideas, new features.
And of course you are welcome to create PR for this project.
