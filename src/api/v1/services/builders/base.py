from abc import ABC, abstractmethod

from api.v1.models import Card
from api.v1.services.schemas.input import InputContext
from api.v1.services.schemas.input_contents import InputType
from api.v1.services.schemas.presentation import PresentationContext, PresentationType


class IInputBuilder(ABC):

    @abstractmethod
    async def build(self, card: Card) -> InputContext:
        ...

    @abstractmethod
    async def is_available(self, card: Card) -> bool:
        ...

    @property
    @abstractmethod
    def TYPE(self) -> InputType:
        ...

class IPresentationBuilder(ABC):
    @abstractmethod
    async def is_available(self, card: Card) -> bool:
        ...

    @property
    @abstractmethod
    def TYPE(self) -> PresentationType:
        ...

    @abstractmethod
    async def build(self, card: Card) -> PresentationContext:
        ...
