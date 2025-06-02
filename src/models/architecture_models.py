from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class ImportInfo:
    simple_name: str
    full_name: str


@dataclass
class FieldInfo:
    name: str
    class_type: str
    declaring_class: str


@dataclass
class MethodInfo:
    name: str
    class_name: str
    return_type: str
    parameters: List[str] = field(default_factory=list)


@dataclass
class MethodCall:
    caller_class: str
    caller_method: str
    called_class: str
    called_method: str
    line_number: int


@dataclass
class ClassInfo:
    name: str
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)
    fields: List[FieldInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)


@dataclass
class ASTNode:
    node_type: str
    name: Optional[str] = None
    children: List["ASTNode"] = field(default_factory=list)
    line_number: Optional[int] = None
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileAnalysis:
    file_path: str
    classes: List[ClassInfo] = field(default_factory=list)
    method_calls: List[MethodCall] = field(default_factory=list)
    ast_nodes: List[ASTNode] = field(default_factory=list)


@dataclass
class ProjectAnalysis:
    directory: str
    files: List[FileAnalysis] = field(default_factory=list)
    total_files: int = 0
    total_methods: int = 0
    total_method_calls: int = 0

    def get_all_classes(self) -> List[ClassInfo]:
        classes = []
        for file_analysis in self.files:
            classes.extend(file_analysis.classes)
        return classes

    def get_all_methods(self) -> List[MethodInfo]:
        methods = []
        for file_analysis in self.files:
            for class_info in file_analysis.classes:
                methods.extend(class_info.methods)
        return methods

    def get_all_method_calls(self) -> List[MethodCall]:
        calls = []
        for file_analysis in self.files:
            calls.extend(file_analysis.method_calls)
        return calls

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directory": self.directory,
            "total_files": self.total_files,
            "total_methods": self.total_methods,
            "total_method_calls": self.total_method_calls,
            "files": [
                {
                    "file_path": file_analysis.file_path,
                    "classes": [
                        {
                            "name": cls.name,
                            "extends": cls.extends,
                            "implements": cls.implements,
                            "methods": [
                                {
                                    "name": method.name,
                                    "return_type": method.return_type,
                                    "parameters": method.parameters,
                                }
                                for method in cls.methods
                            ],
                            "fields": [
                                {
                                    "name": field.name,
                                    "type": field.class_type,
                                }
                                for field in cls.fields
                            ],
                        }
                        for cls in file_analysis.classes
                    ],
                    "method_calls": [
                        {
                            "caller_class": call.caller_class,
                            "caller_method": call.caller_method,
                            "called_class": call.called_class,
                            "called_method": call.called_method,
                            "line_number": call.line_number,
                        }
                        for call in file_analysis.method_calls
                    ],
                }
                for file_analysis in self.files
            ],
        }
