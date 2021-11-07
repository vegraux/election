class TestParty:
    def test_add_parties_votes(self, parties_with_representatives):
        """Checks that + operator works. Votes and representatives should be added together"""
        party_a, party_b = parties_with_representatives
        added_parties = party_a + party_b
        assert added_parties._votes == 300
        assert party_a._votes == 200
        assert party_b._votes == 100

    def test_add_parties_representatives(self, parties_with_representatives):
        """Checks that + operator works. Votes and representatives should be added together"""
        party_a, party_b = parties_with_representatives
        added_parties = party_a + party_b
        assert added_parties.representatives == 9  # 10 minus leveling seat
        assert party_a.representatives == 6
        assert party_b.representatives == 3

    def test_add_parties_different_names(self, parties_with_representatives, capture):
        party_b, party_a = parties_with_representatives
        _ = party_a + party_b
        msg = "Party names differ: 'Party A' and 'Party B'. Resulting party is named 'Party A'"
        capture.check(("election.party", "WARNING", msg))
