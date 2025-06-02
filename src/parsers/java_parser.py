from pathlib import Path
from typing import List
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from .generated.JavaLexer import JavaLexer
from .generated.JavaParser import JavaParser
from .listeners.java_listener import JavaCodeListener
from src.models.parser_models import ParsedJavaFile


class JavaCodeParser:

    def parse_file(self, file_path: str | Path) -> ParsedJavaFile:
        file_path = Path(file_path)

        with open(file_path, "r") as f:
            source_text = f.read()

        input_stream = FileStream(str(file_path))
        lexer = JavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        tree = parser.compilationUnit()

        listener = JavaCodeListener()
        listener.source_text = source_text
        listener.token_stream = stream
        walker = ParseTreeWalker()
        walker.walk(listener, tree)

        return listener.get_results()
