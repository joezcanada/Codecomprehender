from typing import List, Optional
from src.schemas.documentation_schema import FileDocumentation
from src.models.parser_models import ParsedJavaFile, ExistingDocMode


def apply_documentation(
    file_doc: FileDocumentation,
    parsed_result: ParsedJavaFile,
    existing_mode: ExistingDocMode,
) -> str:
    if not parsed_result.documentation_positions:
        return parsed_result.source_text

    lines = parsed_result.source_text.split("\n")
    positions = sorted(
        parsed_result.documentation_positions, key=lambda x: x.line, reverse=True
    )

    for pos in positions:
        if pos.has_existing_javadoc and existing_mode == ExistingDocMode.SKIP:
            continue

        doc_text = _find_documentation_text(
            file_doc, pos.element_type.value, pos.name, pos.class_name
        )
        if doc_text:
            _insert_documentation_at_position(lines, pos, doc_text, existing_mode)

    return "\n".join(lines)


def _find_documentation_text(
    file_doc: FileDocumentation, element_type: str, element_name: str, class_name: str
) -> Optional[str]:
    if not file_doc.classes:
        return None

    if element_type == "class":
        class_doc = file_doc.classes.get(element_name)
        return class_doc.comment if class_doc else None

    if not class_name:
        return None

    class_doc = file_doc.classes.get(class_name)
    if not class_doc:
        return None

    if class_doc.constructors and element_name in class_doc.constructors:
        return class_doc.constructors[element_name].comment

    if (
        element_type == "method"
        and class_doc.methods
        and element_name in class_doc.methods
    ):
        return class_doc.methods[element_name].comment

    if (
        element_type == "field"
        and class_doc.fields
        and element_name in class_doc.fields
    ):
        return class_doc.fields[element_name].comment

    return None


def _insert_documentation_at_position(
    lines: List[str], pos, doc_text: str, existing_mode: ExistingDocMode
):
    target_line = pos.line - 1
    if pos.has_existing_javadoc and existing_mode == ExistingDocMode.OVERRIDE:
        target_line = _remove_existing_javadoc(lines, target_line)

    insertion_line = _find_insertion_point(lines, target_line)

    indent_spaces = (
        _calculate_indent(lines[insertion_line]) if insertion_line < len(lines) else 0
    )
    javadoc = _format_javadoc(doc_text, indent_spaces)
    javadoc_lines = javadoc.split("\n")

    if insertion_line > 0 and lines[insertion_line - 1].strip():
        javadoc_lines.insert(0, "")

    for i, line in enumerate(javadoc_lines):
        lines.insert(insertion_line + i, line)


def _find_insertion_point(lines: List[str], target_line: int) -> int:
    for i in range(target_line - 1, -1, -1):
        line = lines[i].strip()
        if line.startswith("@"):
            target_line = i
        elif line and not line.startswith(("//", "/*")):
            break
    return target_line


def _remove_existing_javadoc(lines: List[str], target_line: int) -> int:
    start = end = None

    for i in range(target_line - 1, -1, -1):
        line = lines[i].strip()
        if line.endswith("*/") and not line.startswith("//") and end is None:
            end = i
        elif line.startswith("/**") and end is not None:
            start = i
            break
        elif line and not line.startswith(("@", "*", "//")):
            break

    if start is not None and end is not None:
        del lines[start : end + 1]
        while start > 0 and not lines[start - 1].strip():
            del lines[start - 1]
            start -= 1
        return start

    return target_line


def _calculate_indent(line: str) -> int:
    return len(line) - len(line.lstrip()) if line.strip() else 0


def _format_javadoc(comment: str, indent_spaces: int = 0) -> str:
    if not comment or not comment.strip():
        return ""

    indent = " " * indent_spaces
    content = comment.strip()
    if content.startswith("/**") and content.endswith("*/"):
        content = content[3:-2]

    clean_lines = []
    for line in content.split("\n"):
        cleaned = line.strip()
        if cleaned.startswith("*"):
            cleaned = cleaned[1:].strip()
        if cleaned:
            clean_lines.append(cleaned)

    result = [f"{indent}/**"]
    for line in clean_lines:
        result.append(f"{indent} * {line}")
    result.append(f"{indent} */")

    return "\n".join(result)
