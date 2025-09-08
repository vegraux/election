import pandas as pd

from election.nation import Nation


def test_results2021_ordinary_representatives(results2021_ordinary_representatives: pd.DataFrame, nation2021: Nation):
    nation2021.calc_ordinary_representatives()
    pd.testing.assert_frame_equal(
        nation2021.ordinary_party_representatives,
        results2021_ordinary_representatives,
        check_names=False,
    )


def test_results2021_district_representatives_count(
    results2021_ordinary_representatives: pd.DataFrame, nation2021: Nation
):
    district_representatives = results2021_ordinary_representatives.sum(axis=1)
    nation2021.calc_district_representatives()
    pd.testing.assert_series_equal(
        nation2021.ordinary_district_representatives.index.value_counts().sort_index(),
        district_representatives.sort_index(),
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


def test_result_without_electoral_threshold(nation2021: Nation):
    """VG has a page where one can experiment with different variables, and see the election result.

    This test compares the result of this code with VG's results. https://www.vg.no/spesial/2017/stortingsvalg/
    """
    data = [
        (0, 1, 3, 2, 0, 0, 0, 0, 0, 2, 1, 0),
        (1, 1, 5, 2, 1, 0, 0, 0, 2, 5, 2, 0),
        (2, 3, 4, 0, 2, 0, 0, 0, 3, 5, 1, 0),
        (0, 0, 3, 2, 1, 0, 0, 0, 0, 1, 0, 0),
        (0, 0, 2, 2, 1, 0, 0, 0, 0, 1, 0, 0),
        (0, 0, 3, 1, 0, 0, 0, 0, 1, 2, 1, 0),
        (0, 0, 2, 1, 1, 0, 0, 0, 0, 2, 1, 0),
        (0, 0, 2, 1, 0, 0, 0, 1, 0, 1, 1, 0),
        (0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0),
        (0, 0, 1, 1, 0, 0, 0, 2, 0, 1, 1, 0),
        (1, 1, 3, 2, 0, 0, 0, 1, 0, 4, 2, 0),
        (1, 1, 4, 2, 0, 0, 0, 1, 1, 4, 2, 0),
        (0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0),
        (0, 1, 2, 2, 0, 0, 0, 0, 0, 1, 2, 0),
        (1, 1, 3, 2, 0, 0, 0, 0, 0, 2, 1, 0),
        (0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1),
        (1, 1, 3, 2, 0, 0, 0, 0, 0, 1, 1, 0),
        (0, 1, 2, 1, 0, 0, 0, 0, 0, 1, 1, 0),
        (0, 0, 2, 1, 0, 1, 0, 0, 0, 0, 0, 1),
    ]
    districts = [
        "Østfold",
        "Akershus",
        "Oslo",
        "Hedmark",
        "Oppland",
        "Buskerud",
        "Vestfold",
        "Telemark",
        "Aust-Agder",
        "Vest-Agder",
        "Rogaland",
        "Hordaland",
        "Sogn og Fjordane",
        "Møre og Romsdal",
        "Sør-Trøndelag",
        "Nord-Trøndelag",
        "Nordland",
        "Troms Romsa",
        "Finnmark Finnmárku",
    ]
    parties = ["RØDT", "SV", "A", "SP", "MDG", "PF", "PP", "KRF", "V", "H", "FRP", "DEMN"]
    target = pd.DataFrame(data, columns=parties, index=districts)

    nation2021.electoral_threshold = 0.0
    nation2021.simulate_election()
    pd.testing.assert_frame_equal(
        nation2021.party_representatives[target.columns].sort_index(), target.sort_index(), check_names=False
    )
