import copy
import logging
from typing import ClassVar, Self

from pydantic import BaseModel

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class Representative(BaseModel):
    name: str

    @staticmethod
    def is_ordinary() -> bool:
        return False


class OrdinaryRepresentative(Representative):
    nr: int
    remaining_representative: int
    quotient: float

    @staticmethod
    def is_ordinary() -> bool:
        return True


class Party:
    parameters: ClassVar = {
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    @classmethod
    def set_parameters(cls, new_parameters: dict) -> None:
        """:param new_parameters:"""
        cls.parameters = {**cls.parameters, **new_parameters}

    def __init__(self, name: str, votes: int, short_name: str | None = None, method: str = "modified") -> None:
        """A political party."""
        self.name = name
        self.district = None
        self.short_name = short_name
        self._votes = votes
        self.method = method
        self._representatives = []

    def __repr__(self) -> str:
        return self.name

    def __add__(self, other: Self) -> Self:
        """Used to add votes and representatives from the same Party in different districts."""
        if self.name != other.name:
            msg = f"Party names differ: '{self.name}' and '{other.name}'. " f"Resulting party is named '{self.name}'"
            logger.warning(msg)
        party = copy.deepcopy(self)
        party._votes = self._votes + other._votes
        party._representatives = self._representatives + other._representatives
        return party

    @property
    def representatives(self) -> list[Representative]:
        return self._representatives

    @property
    def nr_representatives(self) -> int:
        return len(self._representatives)

    @property
    def coefficient(self) -> int:
        """Coefficient (dividend) used to distribute party representatives.

        The same as the number of votes.
        """
        return self._votes

    def dividend(self, nr_reps: int) -> float:
        if (self.method == "modified") and nr_reps == 0:
            return self.parameters["st_lagues_factor"]
        else:
            return self.parameters["divide_factor"] * nr_reps + 1

    @property
    def quotient(self) -> float:
        """Quotient that is sorted among all parties when distributing representatives."""
        return self.coefficient / self.dividend(self.nr_representatives)

    def reset_representatives(self) -> None:
        """Resets the distributed representatives to 0. Used when calculating leveling seats."""
        self._representatives = []

    def vote_share(self, total_votes: int) -> float:
        """Party's share of total votes."""
        return self._votes / total_votes

    def level_seat_factor(self, votes_per_representative: float) -> float:
        """Factor used to distribute leveling seat."""
        return self.quotient / votes_per_representative

    def add_representative(self, nr: int, remaining_spots: int) -> None:
        self.representatives.append(
            OrdinaryRepresentative(
                nr=nr, remaining_representative=remaining_spots, quotient=self.quotient, name=self.name
            )
        )

    def add_leveling_representative(self) -> None:
        self.representatives.append(Representative(name=self.name))
