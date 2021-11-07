# -*- coding: utf-8 -*-

"""

"""

import pytest

from election.district import District
from election.party import Party


class TestDistrict:
    def test_county_add_representative(self, district1):
        """
        The division number should change when the number of representatives increase
        """
        div_num0 = district1.quotient
        district1.representatives += 1
        div_num1 = district1.quotient
        assert div_num0 > div_num1

    def test_correct_div_num_modified(self, district1):
        district1.method = "modified"
        assert (
            district1.quotient == (1000 + 1000 * 1.8) / 1.4
        )  # divide with 1.4 with modified version
        district1.representatives = 3
        assert district1.quotient == (1000 + 1000 * 1.8) / 7

    def test_correct_div_num_normal(self, district1):
        district1.method = "normal"
        assert district1.quotient == 1000 + 1000 * 1.8
        district1.representatives = 5
        assert district1.quotient == (1000 + 1000 * 1.8) / 11

    def test_county_name_area(self):
        with pytest.raises(ValueError):
            District(name="Oslo", area=-234, population=12345)

        with pytest.raises(ValueError):
            District(name="Oslo", area=234, population=-12345)

    def test_set_parameters(self):
        c1 = District(name="Finnmark", area=123, population=3421)
        c2 = District(name="Trondheim", area=123, population=5432)
        assert c1.parameters["area_importance"] == 1.8

        District.set_parameters({"area_importance": 2})
        assert c1.parameters["area_importance"] == 2
        assert c2.parameters["area_importance"] == 2
        District.set_parameters({"area_importance": 1.8})

    def test_append_parties(self):
        c1 = District(name="Finnmark", area=123, population=3421)
        p1 = Party(name="SV", votes=2354)
        p2 = Party(name="FRP", votes=654)

        assert c1.parties is None
        c1.append_parties([p1, p2])

        assert len(c1.parties) == 2

    def test_county_votes(self):
        c1 = District(name="Finnmark", area=123, population=3421)
        p1 = Party(name="Sosialistisk venstreparti", votes=200)
        p2 = Party(name="FRP", votes=300)

        c1.append_parties([p1, p2])

        assert c1.district_votes == 500

    def test_add_district_area(self, district1, district2):
        """Checks that + operator works. Area and population should be added together"""
        added_district = district1 + district2
        assert added_district._area == 1100
        assert district1._area == 1000
        assert district2._area == 100

    def test_add_district_population(self, district1, district2):
        """Checks that + operator works. Area and population should be added together"""
        added_district = district1 + district2
        assert added_district._population == 1100
        assert district1._population == 1000
        assert district2._population == 100
