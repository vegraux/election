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
        p = copy.deepcopy(self)
        p._votes = self._votes + other._votes
        p.representatives = self.representatives + other.representatives
        return p

    @property
    def representatives(self):
        return self._representatives

    @property
    def coefficient(self):
        return self._votes

    @representatives.setter
    def representatives(self, a):
        self._representatives = a

    @property
    def quotient(self):
        if (self.method == "modified") and (self.representatives == 0):
            quotient = self.coefficient / self.parameters["st_lagues_factor"]
        else:

            quotient = self.coefficient / (
                self.parameters["divide_factor"] * self.representatives + 1
            )
        return quotient

    def calc_quotient(self):
        if (self.method == "modified") and (self.representatives == 0):
            coeff = self.coefficient / self.parameters["st_lagues_factor"]
        else:

            coeff = self.coefficient / (self.parameters["divide_factor"] * self.representatives + 1)
        return coeff
