from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class JavaMethod:
    name: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    javadoc: str = ""
    original_code: str = ""
    line_number: int = 0


@dataclass
class JavaConstructor:
    name: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    javadoc: str = ""
    original_code: str = ""
    line_number: int = 0


@dataclass
class JavaField:
    name: str
    field_type: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    javadoc: str = ""
    original_code: str = ""
    line_number: int = 0


@dataclass
class JavaClass:
    name: str
    modifiers: List[str] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    javadoc: str = ""
    original_code: str = ""
    line_number: int = 0
    methods: Dict[str, JavaMethod] = field(default_factory=dict)
    constructors: Dict[str, JavaConstructor] = field(default_factory=dict)
    fields: Dict[str, JavaField] = field(default_factory=dict)
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "line_number": self.line_number,
            "methods": {
                name: {
                    "name": method.name,
                    "line_number": method.line_number,
                    "modifiers": method.modifiers,
                    "annotations": method.annotations,
                    "javadoc": method.javadoc,
                    "original_code": method.original_code,
                }
                for name, method in self.methods.items()
            },
            "constructors": {
                name: {
                    "name": constructor.name,
                    "line_number": constructor.line_number,
                    "modifiers": constructor.modifiers,
                    "annotations": constructor.annotations,
                    "javadoc": constructor.javadoc,
                    "original_code": constructor.original_code,
                }
                for name, constructor in self.constructors.items()
            },
            "fields": {
                name: {
                    "name": field.name,
                    "line_number": field.line_number,
                    "type": field.field_type,
                    "modifiers": field.modifiers,
                    "annotations": field.annotations,
                    "javadoc": field.javadoc,
                    "original_code": field.original_code,
                }
                for name, field in self.fields.items()
            },
            "extends": self.extends,
            "implements": self.implements,
            "modifiers": self.modifiers,
            "annotations": self.annotations,
            "javadoc": self.javadoc,
            "original_code": self.original_code,
        }
