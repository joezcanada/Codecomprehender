from pathlib import Path
import logging
import json
from src.parsers.architecture_parser import ArchitectureParser
from src.services.graph_generator import GraphGenerator
from src.models.architecture_models import ProjectAnalysis

logger = logging.getLogger(__name__)


class ArchitectureAnalysisService:
    def __init__(self):
        self.parser = ArchitectureParser()
        self.graph_generator = GraphGenerator()

    def analyze_project(self, project_path: str, output_dir: str) -> ProjectAnalysis:
        path_obj = Path(project_path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if not path_obj.is_dir():
            raise ValueError("Path must be a directory containing Java files")

        java_files = list(path_obj.glob("**/*.java"))
        logger.info(f"Analyzing {len(java_files)} Java files")

        project_analysis = ProjectAnalysis(directory=str(path_obj))

        for i, java_file in enumerate(java_files, 1):
            try:
                file_analysis = self.parser.parse_file_for_architecture(java_file)
                project_analysis.files.append(file_analysis)
                logger.info(f"Analyzed ({i}/{len(java_files)}): {java_file.name}")
            except Exception as e:
                logger.error(f"Failed to analyze {java_file}: {e}")

        project_analysis.total_files = len(project_analysis.files)
        project_analysis.total_methods = len(project_analysis.get_all_methods())
        project_analysis.total_method_calls = len(
            project_analysis.get_all_method_calls()
        )

        dir_name = path_obj.name
        json_file = output_path / f"{dir_name}_analysis.json"
        json_file.write_text(
            json.dumps(project_analysis.to_dict(), indent=2, default=str)
        )
        logger.info(f"Analysis saved to: {json_file}")

        if self.graph_generator.is_graphviz_available():
            self.graph_generator.render_call_graph(
                project_analysis, str(output_path / f"{dir_name}_call_graph"), "jpg"
            )
            self.graph_generator.render_ast_graph(
                project_analysis, str(output_path / f"{dir_name}_ast"), "jpg"
            )
        else:
            logger.warning("Graphviz not available for image rendering")

        logger.info(
            f"Architecture analysis completed! Analyzed {project_analysis.total_files} files, found {project_analysis.total_methods} methods, {project_analysis.total_method_calls} method calls"
        )

        return project_analysis
