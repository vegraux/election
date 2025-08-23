import copy
import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class Party:
    parameters = {
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    @classmethod
    def set_parameters(cls, new_parameters: dict):
        """

        :param new_parameters:
        """
        cls.parameters = {**cls.parameters, **new_parameters}

    def __init__(self, name: str, votes: int, short_name: str = None, method: str = "modified"):
        """
        A political party
        :param name: name of political party
        :param votes: nr of votes
        :param short_name: Abbreviation of party name
        :param method: normal or modified St Lagües
        """

        self.name = name
        self.district = None
        self.short_name = short_name
        self._votes = votes
        self.method = method
        self._representatives = 0

    def __repr__(self):
        return self.name

    def __add__(self, other):
        """
        Used to add votes and representatives from the same Party in different districts
        """
        if self.name != other.name:
            msg = (
                f"Party names differ: '{self.name}' and '{other.name}'. "
                f"Resulting party is named '{self.name}'"
            )
            logger.warning(msg)
        party = copy.deepcopy(self)
        party._votes = self._votes + other._votes
        party.representatives = self.representatives + other.representatives
        return party

    @property
    def representatives(self) -> int:
        return self._representatives

    @property
    def coefficient(self) -> int:
        """
        Coefficient (dividend) used to distribute party representatives. The same as the number
        of votes
        """
        return self._votes

    @representatives.setter
    def representatives(self, a):
        self._representatives = a


    @property
    def dividend(self) -> float:
        if (self.method == "modified") and (self.representatives == 0):
            return self.parameters["st_lagues_factor"]
        else:
            return self.parameters["divide_factor"] * self.representatives + 1

    @property
    def quotient(self) -> float:
        """
        Quotient that is sorted among all parties when distributing representatives
        """

        return self.coefficient / self.dividend

    def reset_representatives(self):
        """
        Resets the distributed representatives to 0. Used when calculating leveling seats
        """
        self.representatives = 0

    def vote_share(self, total_votes: int) -> float:
        """
        Party's share of total votes
        """
        return self._votes / total_votes

    def level_seat_factor(self, votes_per_representative: float) -> float:
        """
        Factor used to distribute leveling seat.
        """
        return self.quotient / votes_per_representative
