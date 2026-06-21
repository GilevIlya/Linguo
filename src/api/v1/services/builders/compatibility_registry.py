from api.v1.services.schemas.input_contents import InputType
from api.v1.services.schemas.presentation import PresentationType

class CompatibilityRegistry:
    """
    Centralized registry to manage the compatibility of presentation and input types.
    By default, all combinations are considered compatible unless they are added to the exclusion list.
    """
    def __init__(self):
        self._incompatible_pairs: set[tuple[PresentationType, InputType]] = set()

    def register_incompatible_pair(self, presentation: PresentationType, input_type: InputType) -> None:
        """Registers Rule: This presentation is not compatible with this input type."""
        self._incompatible_pairs.add((presentation, input_type))

    def is_compatible(self, presentation: PresentationType, input_type: InputType) -> bool:
        """Checks if the given pair is compatible"""
        return (presentation, input_type) not in self._incompatible_pairs