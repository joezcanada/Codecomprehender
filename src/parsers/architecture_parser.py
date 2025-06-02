"""Architecture parser for Java files."""

from pathlib import Path
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from .generated.JavaLexer import JavaLexer
from .generated.JavaParser import JavaParser
from .listeners.architecture_listeners import CallGraphListener, ASTListener
from src.models.architecture_models import FileAnalysis


class ArchitectureParser:

    def parse_file_for_architecture(self, file_path: str | Path) -> FileAnalysis:
        file_path = Path(file_path)

        input_stream = FileStream(str(file_path))
        lexer = JavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        tree = parser.compilationUnit()

        call_graph_listener = CallGraphListener()
        ast_listener = ASTListener()

        walker = ParseTreeWalker()
        walker.walk(call_graph_listener, tree)
        walker.walk(ast_listener, tree)

        return FileAnalysis(
            file_path=str(file_path),
            classes=call_graph_listener.classes,
            method_calls=call_graph_listener.method_calls,
            ast_nodes=ast_listener.ast_nodes,
        )
