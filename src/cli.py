import click
from pathlib import Path
from src.services.code_documentation_service import CodeDocumentationService
from src.services.architecture_analysis_service import ArchitectureAnalysisService
from src.models.parser_models import ExistingDocMode
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ExistingDocModeType(click.Choice):
    def __init__(self):
        super().__init__([mode.value for mode in ExistingDocMode], case_sensitive=False)

    def convert(self, value, param, ctx):
        str_value = super().convert(value, param, ctx)
        return ExistingDocMode(str_value)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--copy",
    "-c",
    is_flag=True,
    help="Create a copy of the project and add documentation to the copy",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    help="Directory where to create the documented copy",
)
@click.option(
    "--existing",
    type=ExistingDocModeType(),
    default=ExistingDocMode.SKIP.value,
    help="How to handle existing documentation: skip (default), override, or keep-both",
)
def document(path: str, copy: bool, output_dir: str, existing: ExistingDocMode):
    """Generate documentation for Java files.

    PATH: Path to the project to document.
    """
    try:
        service = CodeDocumentationService()
        results = service.document_project(
            existing_mode=existing,
            project_path=path,
            output_dir=os.path.abspath(output_dir) if output_dir else None,
            make_copy=copy,
        )

        file_count = len(results)
        if copy and output_dir:
            click.echo(
                f"Documentation completed. {file_count} files successfully documented and copied to {output_dir}/output/"
            )
        else:
            click.echo(
                f"Documentation completed. {file_count} files successfully documented."
            )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise click.ClickException(f"Error: {str(e)}")


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="./output/architecture",
    help="Directory where to save the analysis results",
)
def architecture(path: str, output_dir: str):
    """Analyze Java code architecture and generate AST/call graphs.

    PATH: Path to a directory containing Java files
    """
    try:
        service = ArchitectureAnalysisService()
        service.analyze_project(path, output_dir)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise click.ClickException(f"Error: {str(e)}")


if __name__ == "__main__":
    cli()
