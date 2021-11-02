import pytest

from election.district import District
from election.voting import Nation


@pytest.fixture
def district1():
    return District(area=100, population=100, name="foo1")


@pytest.fixture
def district2():
    return District(area=1000, population=1000, name="foo2")


@pytest.fixture
def nation(district1, district2):
    return Nation(districts=[district1, district2])
