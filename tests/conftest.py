import pytest

from election.district import District
from election.voting import Nation


@pytest.fixture
def county1():
    return District(area=100, population=100, name="foo1")


@pytest.fixture
def county2():
    return District(area=1000, population=1000, name="foo2")


@pytest.fixture
def nation(county1, county2):
    return Nation(counties=[county1, county2])
