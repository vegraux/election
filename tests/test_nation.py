import pandas as pd

from election.nation import Nation


def test_results2021_ordinary_representatives(results2021_ordinary_representatives: pd.DataFrame, nation2021: Nation):
    nation2021.calc_ordinary_representatives()
    pd.testing.assert_frame_equal(
        nation2021.ordinary_party_representatives,
        results2021_ordinary_representatives,
        check_names=False,
    )


def test_results2021_district_representatives_count(results2021_all_representatives: pd.DataFrame, nation2021: Nation):
    district_representatives = results2021_all_representatives.sum(axis=1)
    nation2021.calc_district_representatives()
    pd.testing.assert_series_equal(
        nation2021.district_representatives["representatives"],
        district_representatives,
        check_names=False,
    )


def test_set_national_district(nation2021: Nation):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()


def test_set_threshold_parties(nation2021: Nation):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_threshold_parties()
    assert len(nation2021.over_threshold_district) == 7  # rip krf and mdg ++
    # krf (3), mdg(3) and pf(1):
    assert nation2021.under_threshold_district.distributed_representatives == 7


def test_set_leveling_seat_per_party(nation2021: Nation, results2021_leveling_seats: pd.DataFrame):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_threshold_parties()
    nation2021.set_leveling_seat_per_party()
    pd.testing.assert_series_equal(
        nation2021.leveling_seat_per_party.sort_index(),
        results2021_leveling_seats.sum().sort_index(),
        check_names=False,
        check_dtype=False,
    )


def test_distribute_leveling_seats_to_parties(nation2021: Nation, results2021_leveling_seats: pd.DataFrame):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_threshold_parties()
    nation2021.set_leveling_seats_factors()
    nation2021.set_leveling_seat_per_party()
    nation2021.distribute_leveling_seats_to_parties()
    pd.testing.assert_frame_equal(results2021_leveling_seats, nation2021.leveling_seats, check_names=False)


def test_apply_leveling_seat_results(nation2021: Nation, results2021_leveling_seats: pd.DataFrame):
    nation2021.calc_ordinary_representatives()
    nation2021.set_national_district()
    nation2021.set_threshold_parties()
    nation2021.set_leveling_seats_factors()
    nation2021.set_leveling_seat_per_party()
    nation2021.distribute_leveling_seats_to_parties()
    nation2021.apply_leveling_seat_results()
    diff = nation2021.party_representatives - nation2021.ordinary_party_representatives
    diff = diff.loc[:, ~(diff == 0).all(axis=0)]  # The diff should be the leveling seats
    pd.testing.assert_frame_equal(results2021_leveling_seats, diff, check_names=False)
