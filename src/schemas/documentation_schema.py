from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class DocumentationElement(BaseModel):
    comment: Optional[str] = None
    original_code: Optional[str] = None


class ClassDocumentation(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    comment: Optional[str] = None
    annotations: Optional[List[str]] = None
    original_code: Optional[str] = None
    constructors: Optional[Dict[str, DocumentationElement]] = None
    methods: Optional[Dict[str, DocumentationElement]] = None
    fields: Optional[Dict[str, DocumentationElement]] = None
    implements: Optional[List[str]] = None
    extends: Optional[str] = None


class FileDocumentation(BaseModel):
    package: Optional[str] = None
    imports: Optional[List[str]] = None
    license_header: Optional[str] = None
    classes: Optional[Dict[str, ClassDocumentation]] = None
