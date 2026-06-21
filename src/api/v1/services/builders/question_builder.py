import random

from api.v1.models import Card
from api.v1.services.builders.builder_registry import PresentationBuilderRegistry, InputBuilderRegistry
from api.v1.services.builders.compatibility_registry import CompatibilityRegistry
from api.v1.services.exceptions.base_exceptions import BusinessLogicException
from api.v1.services.exceptions.error_codes.quiz_error_codes import QuizErrorCodes
from api.v1.services.schemas.input_contents import InputType
from api.v1.services.schemas.presentation import PresentationType
from api.v1.services.schemas.question import Question


class QuestionBuilder: # TODO: #poop code | rewrite (DRY)
    def __init__(
            self,
            presentation_builder_registry: PresentationBuilderRegistry,
            input_builder_registry: InputBuilderRegistry,
            compatibility_registry: CompatibilityRegistry,
        ):
        self.presentation_builder_registry = presentation_builder_registry
        self.input_builder_registry = input_builder_registry
        self.compatibility_registry = compatibility_registry

    async def build_random(
            self,
            card: Card,
            *,
            excepted_presentations: list[PresentationType] | None = None,
            excepted_inputs: list[InputType] | None = None,
    ) -> Question:
        if excepted_presentations is None:
            excepted_presentations = []
        if excepted_inputs is None:
            excepted_inputs = []

        self._validate_excepted_presentations(excepted_presentations)
        self._validate_excepted_inputs(excepted_inputs)

        presentation_builders = [
            i for i in await self.presentation_builder_registry.get_available_builders(card)
            if i.TYPE not in excepted_presentations
        ]
        input_builders = [
            x for x in await self.input_builder_registry.get_available_builders(card)
            if x.TYPE not in excepted_inputs
        ]

        if not presentation_builders or not input_builders:
            raise BusinessLogicException(
                QuizErrorCodes.ALL_FIELDS_ARE_EXCLUDED.value,
                "You have excluded all fields, it is impossible to make a question"
            )

        compatible_pairs = []
        for pb in presentation_builders:
            for ib in input_builders:
                if self.compatibility_registry.is_compatible(pb.TYPE, ib.TYPE):
                    compatible_pairs.append((pb, ib))

        if not compatible_pairs:
            raise BusinessLogicException(
                QuizErrorCodes.NO_COMPATIBLE_COMBINATIONS_FOUND.value,
                "Can't build question: no compatible presentation and input combinations available."
            )

        selected_presentation, selected_input = random.choice(compatible_pairs)

        return Question(
            presentation=await selected_presentation.build(card=card),
            input=await selected_input.build(card=card)
        )

    def _validate_excepted_inputs(self, excepted_inputs: list[InputType]):
        if len(excepted_inputs) >= len(InputType):
            raise BusinessLogicException(
                QuizErrorCodes.AT_LEAST_ONE_INPUT_TYPE_MUST_BE_AVAILABLE.value,
                "All input types are excepted, can't build question",
            )

    def _validate_excepted_presentations(self, excepted_presentations: list[PresentationType]):
        if len(excepted_presentations) >= len(PresentationType):
            raise BusinessLogicException(
                QuizErrorCodes.AT_LEAST_ONE_PRESENTATION_TYPE_MUST_BE_AVAILABLE.value,
                "All presentation types are excepted, can't build question",
            )
