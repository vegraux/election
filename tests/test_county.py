# -*- coding: utf-8 -*-

"""

"""

from country import County, Party
import pytest

__author__ = "Vegard Solberg"
__email__ = "vegard.ulriksen.solberg@nmbu.no"


class TestCounty:
    def test_county_name_area(self):

        with pytest.raises(ValueError):
            County(name="Oslo", area=-234, population=12345)

        with pytest.raises(ValueError):
            County(name="Oslo", area=234, population=-12345)

    def test_set_parameters(self):
        c1 = County(name="Finnmark", area=123, population=3421)
        c2 = County(name="Trondheim", area=123, population=5432)
        assert c1.parameters["area_importance"] == 1.8

        County.set_parameters({"area_importance": 2})
        assert c1.parameters["area_importance"] == 2
        assert c2.parameters["area_importance"] == 2

    def test_add_parties(self):
        c1 = County(name="Finnmark", area=123, population=3421)
        p1 = Party(name="SV", votes=2354)
        p2 = Party(name="FRP", votes=654)

        assert c1.parties is None
        c1.add_parties([p1, p2])

        assert len(c1.parties) == 2

    def test_county_votes(self):
        c1 = County(name="Finnmark", area=123, population=3421)
        p1 = Party(name="SV", votes=200)
        p2 = Party(name="FRP", votes=300)

        c1.add_parties([p1, p2])

        assert c1.count_county_votes() == 500


class TestParty:
    pass
