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


def test_set_threshold_parties(nation2021):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_threshold_parties()
    assert len(nation2021.over_threshold_district) == 7  # rip krf and mdg ++
    # krf (3), mdg(3) and pf(1):
    assert nation2021.under_threshold_district.distributed_representatives == 7


def test_calc_leveling_seat_per_party(nation2021, results2021_leveling_seats):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_threshold_parties()
    leveling_seat_per_party = nation2021.calc_leveling_seat_per_party()
    pd.testing.assert_series_equal(
        leveling_seat_per_party,
        results2021_leveling_seats.sum(),
        check_names=False,
        check_dtype=False,
    )
