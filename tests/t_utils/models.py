from polyfactory.factories.pydantic_factory import ModelFactory

from election.party import OrdinaryRepresentative


class RepresentativeFactory(ModelFactory[OrdinaryRepresentative]):
    __model__ = OrdinaryRepresentative
    __check_model__ = True
