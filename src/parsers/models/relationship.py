from dataclasses import dataclass
from enum import Enum, auto


class RelationType(Enum):
    INHERITANCE = auto()
    IMPLEMENTATION = auto()
    ASSOCIATION = auto()
    COMPOSITION = auto()
    AGGREGATION = auto()


@dataclass
class Relationship:
    type: RelationType
    source: str
    target: str

    def to_tuple(self) -> tuple:
        return (self.type.name.lower(), self.source, self.target)

    @classmethod
    def from_tuple(cls, tup: tuple) -> "Relationship":
        type_str, source, target = tup
        return cls(type=RelationType[type_str.upper()], source=source, target=target)
