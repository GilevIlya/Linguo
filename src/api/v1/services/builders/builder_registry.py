from logging import getLogger

from .base import IInputBuilder, IPresentationBuilder
from ..schemas.input import InputContext
from ..schemas.input_contents import InputType
from ..schemas.presentation import PresentationType, PresentationContext
from ...models import Card

logger = getLogger("app")

# TODO : говнокод: Don't repeat yourself - вынести общую логику в базовый класс и наследоваться от него, а не копипастить код в каждом билдере

class InputBuilderRegistry:
    """Оркестраторы для всех билдеров"""
    def __init__(self):
        self._registry: dict[InputType, IInputBuilder] = {}

    def register(self, input_type: InputType, builder: IInputBuilder):
        self._registry[input_type] = builder

    async def build(self, input_type: InputType, card: Card) -> InputContext:
        builder = self._get_builder(input_type)
        return await builder.build(card)

    async def is_available(self, input_type: InputType, card: Card) -> bool:
        builder = self._get_builder(input_type)
        return await builder.is_available(card)

    def _get_builder(self, input_type: InputType) -> IInputBuilder:
        builder = self._registry.get(input_type)
        if not builder:
            logger.error(f"No input builder found for {input_type}")
            raise NotImplementedError(f"No builder for {input_type}")
        return builder

    async def get_available_builders(self, card: Card) -> list[IInputBuilder]:
        return [i for i in self._registry.values() if await i.is_available(card)]



class PresentationBuilderRegistry:
    """Оркестраторы для всех билдеров"""
    def __init__(self):
        self._registry: dict[PresentationType, IPresentationBuilder] = {}

    def register(self, presentation_type: PresentationType, builder: IPresentationBuilder):
        self._registry[presentation_type] = builder

    async def build(self, presentation_type: PresentationType, card: Card) -> PresentationContext:
        builder = self._get_builder(presentation_type)
        return await builder.build(card)

    async def is_available(self, presentation_type: PresentationType, card: Card) -> bool:
        builder = self._get_builder(presentation_type)
        return await builder.is_available(card)

    def _get_builder(self, presentation_type: PresentationType) -> IPresentationBuilder:
        builder = self._registry.get(presentation_type)
        if not builder:
            logger.error(f"No presentation builder found for {presentation_type}")
            raise NotImplementedError(f"No builder for {presentation_type}")
        return builder

    async def get_available_builders(self, card: Card) -> list[IPresentationBuilder]:
        return [i for i in self._registry.values() if await i.is_available(card)]
