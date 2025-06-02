from typing import List, Dict, Optional
from src.parsers.generated.JavaParserListener import JavaParserListener
from src.parsers.generated.JavaParser import JavaParser
from ..models.java_class import JavaClass, JavaMethod, JavaConstructor, JavaField
from ..models.relationship import Relationship
from src.models.parser_models import DocumentationPosition, ElementType, ParsedJavaFile
import logging

logger = logging.getLogger(__name__)


class JavaCodeListener(JavaParserListener):

    def __init__(self):
        self.classes: Dict[str, JavaClass] = {}
        self.relationships: list[Relationship] = []
        self.current_class: Optional[str] = None
        self.modifiers: List[str] = []
        self.annotations: List[str] = []
        self.package_name: Optional[str] = None
        self.imports: List[str] = []
        self.license_header: Optional[str] = None
        self.source_text: Optional[str] = None
        self.documentation_positions: List[DocumentationPosition] = []
        self.token_stream = None

    def get_results(self) -> ParsedJavaFile:
        return ParsedJavaFile(
            package=self.package_name,
            imports=self.imports,
            license_header=self.license_header or "",
            classes=self.classes,
            relationships=[rel.to_tuple() for rel in self.relationships],
            documentation_positions=self.documentation_positions,
            source_text=self.source_text,
            token_stream=self.token_stream,
        )

    def enterCompilationUnit(self, ctx: JavaParser.CompilationUnitContext):
        if self.source_text:
            self.license_header = self._extract_license_header_from_source(
                self.source_text
            )

    def enterPackageDeclaration(self, ctx: JavaParser.PackageDeclarationContext):
        self.package_name = ctx.qualifiedName().getText()

    def enterImportDeclaration(self, ctx: JavaParser.ImportDeclarationContext):
        import_text = "import "
        if ctx.STATIC():
            import_text += "static "
        import_text += ctx.qualifiedName().getText()
        if ctx.MUL():
            import_text += ".*"
        import_text += ";"
        self.imports.append(import_text)

    def enterAnnotation(self, ctx: JavaParser.AnnotationContext):
        annotation = "@" + ctx.qualifiedName().getText()
        if ctx.LPAREN():
            if ctx.elementValue():
                annotation += f"({ctx.elementValue().getText()})"
            elif ctx.elementValuePairs():
                annotation += f"({ctx.elementValuePairs().getText()})"
            else:
                annotation += "()"
        self.annotations.append(annotation)

    def enterClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = ctx.identifier().getText()
        self._add_documentation_position(ctx, ElementType.CLASS, class_name)

        java_class = JavaClass(
            name=class_name,
            modifiers=self.modifiers[:],
            annotations=self.annotations[:],
            javadoc=self._extract_javadoc(ctx),
            original_code=self._get_original_code(ctx),
            line_number=ctx.start.line if ctx.start else 0,
        )

        if ctx.EXTENDS() and ctx.typeType():
            java_class.extends = ctx.typeType().getText()

        if ctx.IMPLEMENTS() and ctx.typeList():
            type_list = ctx.typeList()
            if hasattr(type_list, "typeType") and type_list.typeType():
                java_class.implements = [t.getText() for t in type_list.typeType()]
            else:
                java_class.implements = []

        self.classes[class_name] = java_class
        self.current_class = class_name
        self._clear_modifiers_and_annotations()

    def enterMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        if self.current_class:
            method_name = ctx.identifier().getText()
            self._add_documentation_position(ctx, ElementType.METHOD, method_name)

            method = self._create_element(ctx, JavaMethod, method_name)
            self.classes[self.current_class].methods[method_name] = method

        self._clear_modifiers_and_annotations()

    def enterConstructorDeclaration(
        self, ctx: JavaParser.ConstructorDeclarationContext
    ):
        if self.current_class:
            constructor_name = ctx.identifier().getText()
            self._add_documentation_position(ctx, ElementType.METHOD, constructor_name)

            constructor = self._create_element(ctx, JavaConstructor, constructor_name)
            self.classes[self.current_class].constructors[
                constructor_name
            ] = constructor

        self._clear_modifiers_and_annotations()

    def enterFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        if self.current_class:
            field_type = ctx.typeType().getText() if ctx.typeType() else "Object"

            var_declarators = ctx.variableDeclarators()
            if var_declarators and hasattr(var_declarators, "variableDeclarator"):
                for var_declarator in var_declarators.variableDeclarator():
                    field_name = var_declarator.variableDeclaratorId().getText()
                    self._add_documentation_position(ctx, ElementType.FIELD, field_name)

                    field = JavaField(
                        name=field_name,
                        field_type=field_type,
                        modifiers=self.modifiers[:],
                        annotations=self.annotations[:],
                        javadoc=self._extract_javadoc(ctx),
                        original_code=self._get_original_code(ctx),
                        line_number=ctx.start.line if ctx.start else 0,
                    )
                    self.classes[self.current_class].fields[field_name] = field

        self._clear_modifiers_and_annotations()

    def _extract_license_header_from_source(self, source_text: str) -> Optional[str]:
        if not source_text:
            return None

        lines = source_text.split("\n")
        header_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("package ", "import ")):
                break
            if stripped.startswith(("//", "/*", "*")) or not stripped:
                header_lines.append(line)
            elif stripped:
                break

        while header_lines and not header_lines[-1].strip():
            header_lines.pop()

        return "\n".join(header_lines) if header_lines else None

    def _extract_javadoc(self, ctx) -> str:
        if not self.source_text or not ctx.start:
            return ""

        lines = self.source_text.split("\n")
        target_line = ctx.start.line - 1

        for i in range(target_line - 1, max(0, target_line - 10), -1):
            line = lines[i].strip()
            if line.startswith("/**"):
                javadoc_lines = []
                for j in range(i, target_line):
                    javadoc_lines.append(lines[j])
                    if lines[j].strip().endswith("*/"):
                        return "\n".join(javadoc_lines)
                break
            elif line and not line.startswith(("@", "*", "//")):
                break

        return ""

    def _get_original_code(self, ctx) -> str:
        if not ctx.start or not ctx.stop:
            return ""

        if self.source_text:
            token_stream = ctx.parser._input
            start_pos = token_stream.get(ctx.start.tokenIndex).start
            end_pos = token_stream.get(ctx.stop.tokenIndex).stop + 1
            return self.source_text[start_pos:end_pos]

        return ""

    def _create_element(self, ctx, element_class, name: str):
        return element_class(
            name=name,
            modifiers=self.modifiers[:],
            annotations=self.annotations[:],
            javadoc=self._extract_javadoc(ctx),
            original_code=self._get_original_code(ctx),
            line_number=ctx.start.line if ctx.start else 0,
        )

    def _add_documentation_position(self, ctx, element_type: ElementType, name: str):
        if ctx.start:
            self.documentation_positions.append(
                DocumentationPosition(
                    element_type=element_type,
                    name=name,
                    class_name=self.current_class,
                    token_index=ctx.start.tokenIndex,
                    line=ctx.start.line,
                    column=ctx.start.column,
                    has_existing_javadoc=bool(self._extract_javadoc(ctx).strip()),
                    context=ctx,
                )
            )

    def _clear_modifiers_and_annotations(self):
        self.modifiers.clear()
        self.annotations.clear()
