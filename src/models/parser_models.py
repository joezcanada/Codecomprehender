from dataclasses import dataclass
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from src.parsers.models.java_class import JavaClass


class ExistingDocMode(Enum):
    SKIP = "skip"
    OVERRIDE = "override"
    KEEP_BOTH = "keep-both"


class ElementType(Enum):
    CLASS = "class"
    METHOD = "method"
    FIELD = "field"
    CONSTRUCTOR = "constructor"
    INTERFACE = "interface"
    ENUM = "enum"


@dataclass
class DocumentationPosition:
    element_type: ElementType
    name: str
    line: int
    column: int
    token_index: int
    has_existing_javadoc: bool
    class_name: Optional[str] = None
    context: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.element_type.value,
            "name": self.name,
            "line": self.line,
            "column": self.column,
            "token_index": self.token_index,
            "has_existing_javadoc": self.has_existing_javadoc,
            "class_name": self.class_name,
            "context": self.context,
        }


@dataclass
class ParsedJavaFile:
    package: str
    imports: List[str]
    license_header: str
    classes: Dict[str, "JavaClass"]
    relationships: List[Any]
    documentation_positions: List[DocumentationPosition]
    source_text: str
    token_stream: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package": self.package,
            "imports": self.imports,
            "license_header": self.license_header,
            "classes": self.classes,
            "relationships": self.relationships,
            "documentation_positions": [
                pos.to_dict() if hasattr(pos, "to_dict") else pos
                for pos in self.documentation_positions
            ],
            "source_text": self.source_text,
            "token_stream": self.token_stream,
        }
