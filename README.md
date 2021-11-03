# Smort Query

[![PyPI version](https://badge.fury.io/py/smort-query.svg)](https://badge.fury.io/py/smort-query)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/smort-query.svg)](https://pypi.org/project/smort-query)
![Build Status](https://github.com/matiuszka/smort-query/actions/workflows/checks.yml/badge.svg)
[![codecov](https://codecov.io/gh/matiuszka/smort-query/branch/master/graph/badge.svg)](https://codecov.io/gh/matiuszka/smort-query)
[![PyPI download total](https://img.shields.io/pypi/dw/smort-query.svg)](https://pypi.python.org/pypi/smort-query/)

![alt text](https://media3.giphy.com/media/hFROvOhBPQVRm/giphy.gif "Smort")

Lazy evaluated query implementation for searching through Python objects
inspired by [Django QuerySets](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#queryset-api-reference).

- GitHub: https://github.com/matiuszka/smort-query
- PyPi: https://pypi.org/project/smort-query

## Rationale

In many moments of our programing tasks we have to filter iterables in
search of the right objects in right order.
I realized that most of the time code looks almost the same, but what kind of interface will be easiest to use ? In that moment I figured out that [Django QuerySets](https://docs.djangoproject.com/en/3.0/ref/models/querysets/#queryset-api-reference) implementation is kinda handy and well known.

So I decided to write small query engine that interface will be similar to Django one.
But it will work for Python objects. Additional assumption was that it will be lazy evaluated to
avoid memory consumption.

## Lookup format

Whole idea relays on keywords arguments naming format.
Let's consider following qualname `attr1.attr2` which can we used to get or set value for attribute.
This engine do things similarly but instead of separating by dot(`.`) we are separating by `__` signs.
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

## How it works ?

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

### User cases

Let's consider fallowing code for populating faked humans:

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

Finding peoples from age between [30; 75). To that we will used specialized comparators:

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

We can also excluding males in similar way:

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

## Supported Comparators

Project supports many comparator that can be chosen as postfix for lookup:

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

## TODOs

- Sphinx documentation.
- The `asc()` and `desc()` methods which works same as `order_by()` but with specified order in advance.
- The `unique_justseen()` and `unique_everseen()` methods to remove duplicates.
  Comparison realized by passed attributes or delegated to objects equality `__eq__`.
- The `intersection()` method for finding common objects in two queries.
  Comparison realized by passed attributes or delegated to objects equality `__eq__`.
- The `__len__` and `__getitem__` improvement for evaluating query only once per life cycle.

## Contribution

Any form of contribution is appreciated. Finding issues, new ideas, new features.
And of course you are welcome to create PR for this project.
