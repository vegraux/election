import pandas as pd


def test_results2021_ordinary_representatives(results2021_ordinary_representatives, nation2021):
    nation2021.calc_ordinary_representatives()
    pd.testing.assert_frame_equal(
        nation2021.party_representatives, results2021_ordinary_representatives, check_names=False
    )


def test_results2021_district_representatives_count(results2021_all_representatives, nation2021):
    district_representatives = results2021_all_representatives.sum(axis=1)
    nation2021.calc_district_representatives()
    pd.testing.assert_series_equal(
        nation2021.district_representatives["representatives"],
        district_representatives,
        check_names=False,
    )


def test_set_national_district(nation2021):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    pass


def test_set_parties_over_cutoff(nation2021):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_parties_over_cutoff()
    assert len(nation2021.over_cutoff_district) == 7  # rip krf and mdg ++


def test_calc_leveling_seat_per_party(nation2021, results2021_leveling_seats):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_parties_over_cutoff()
    leveling_seat_per_party = nation2021.calc_leveling_seat_per_party()
    pd.testing.assert_series_equal(
        leveling_seat_per_party,
        results2021_leveling_seats.sum(),
        check_names=False,
        check_dtype=False,
    )