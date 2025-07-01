# translator graph node
from dataclasses import dataclass

@dataclass
class TranslatorNode:
    """
    Class for Translator graph nodes.
    """

    "CURIE identifier"
    curie: str

    "name"
    label: str | None = None

    "list of biolink types"
    types: list[str] | None = None

    # TODO: add quantifiers/qualifiers?
    # TODO: add edges too?

    "list of synonymous labels"
    synonyms: list[str] | None = None

    "list of synonymous CURIE ids (in the same order as synonyms)"
    curie_synonyms: list[str] | None = None

    # identifier is just another way to access/set the CURIE.
    @property
    def identifier(self):
        """identifier is the CURIE id for the node."""
        return self.curie

    @identifier.setter
    def identifier(self, i):
        """identifier is the CURIE id for the node."""
        self.curie = i

@dataclass
class TranslatorEdge:
    """
    Class that represents Translator edges.
    """

    "The subject is a CURIE id for a node."
    subject: str

    "The object is a CURIE id for a node."
    object: str

    "Predicates"
    predicate: str
