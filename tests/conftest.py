import pytest
from testfixtures import LogCapture

from election.district import District, Party
from election.voting import Nation


@pytest.fixture
def party_a():
    return Party(name="Party A", votes=100)


@pytest.fixture
def party_b():
    return Party(name="Party B", votes=200)


@pytest.fixture
def district1(party_a, party_b):
    district = District(area=1000, population=1000, name="foo2")
    district.append_parties(parties=[party_a, party_b])
    return district


@pytest.fixture
def district2(party_a, party_b):
    district = District(area=100, population=100, name="foo1")
    district.append_parties(parties=[party_a, party_b])
    return district


@pytest.fixture
def parties_with_representatives(district1):
    district1.representatives = 10
    district1.calc_ordinary_representatives()
    return district1.parties


@pytest.fixture
def nation(district1, district2):
    return Nation(districts=[district1, district2])


@pytest.fixture(autouse=True)
def capture():
    with LogCapture() as capture:
        yield capture
