# translator graph node
from dataclasses import dataclass

@dataclass
class TranslatorNode:
    """
    Class for Translator graph nodes.
    """

    curie: str
    label: str | None = None
    types: list[str] | None = None
    synonyms: list[str] | None = None
