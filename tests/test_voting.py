from pandas import testing


def test_results2021(results2021_ordinary_representatives, nation2021):
    nation2021.calc_ordinary_representatives()
    testing.assert_frame_equal(
        nation2021.party_representatives, results2021_ordinary_representatives, check_names=False
    )
