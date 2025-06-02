from pathlib import Path
from typing import Dict, Optional, List
import logging
import shutil
from src.parsers.java_parser import JavaCodeParser
from src.prompts.documentation_system_prompts import DOCUMENTATION_SYS_PROMPT
from src.services.llm_service import LLMService
from src.models.parser_models import ExistingDocMode
from src.services.documentation_inserter import apply_documentation
from src.schemas.documentation_schema import FileDocumentation

logger = logging.getLogger(__name__)


class CodeDocumentationService:

    def __init__(self):
        self.llm_service = LLMService()
        self.parser = JavaCodeParser()

    def document_project(
        self,
        existing_mode: ExistingDocMode,
        project_path: str,
        output_dir: str = None,
        make_copy: bool = True,
    ) -> Dict[str, str]:
        """Document the project."""
        if make_copy:
            source_path = Path(project_path)
            output_path = Path(output_dir) / "output" / source_path.name
            project_path = self._copy_project(project_path, str(output_path))
            logger.info(f"Created documented copy at: {project_path}")

        return self._process_directory(project_path, existing_mode)

    def _process_directory(
        self,
        dir_path: str,
        existing_mode: ExistingDocMode,
    ) -> Dict[str, str]:
        curr_path = Path(dir_path)
        java_files = (
            [curr_path]
            if curr_path.is_file() and curr_path.suffix == ".java"
            else list(curr_path.glob("**/*.java"))
        )

        logger.info(f"Processing {len(java_files)} Java files")

        results = {}
        for i, file_path in enumerate(java_files, 1):
            try:
                documented = self._document_file(str(file_path), existing_mode)
                results[str(file_path)] = documented
                logger.info(f"Documented ({i}/{len(java_files)}): {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")

        return results

    def _document_file(self, file_path: str, existing_mode: ExistingDocMode) -> str:
        file_path_obj = Path(file_path)
        parsed_result = self.parser.parse_file(file_path)

        file_doc = self.llm_service.invoke(
            FileDocumentation,
            DOCUMENTATION_SYS_PROMPT,
            file_path_obj.read_text(),
        )

        file_doc.license_header = (
            file_doc.license_header or parsed_result.license_header
        )

        documented_code = apply_documentation(file_doc, parsed_result, existing_mode)
        file_path_obj.write_text(documented_code)
        return documented_code

    def _copy_project(self, source_path: str, target_path: str) -> str:
        source_path = Path(source_path)
        target_path = Path(target_path)

        shutil.copytree(
            source_path,
            target_path,
            ignore=shutil.ignore_patterns(
                ".git",
                "target",
                "*.class",
                ".gradle",
                "build",
            ),
            dirs_exist_ok=True,
        )

        return str(target_path)
