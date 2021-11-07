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
    assert len(nation2021.leveling_seat_parties) == 7  # rip krf and mdg ++
