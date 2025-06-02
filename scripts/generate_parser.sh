#!/bin/bash

ANTLR_JAR="/opt/homebrew/opt/antlr/antlr-4.13.2-complete.jar"
if [ ! -f "$ANTLR_JAR" ]; then
    echo "ANTLR jar not found at $ANTLR_JAR"
    echo "Please install ANTLR using: brew install antlr"
    exit 1
fi

export CLASSPATH="$ANTLR_JAR:$CLASSPATH"

mkdir -p src/parsers/generated

cd grammar
java -jar "$ANTLR_JAR" -Dlanguage=Python3 JavaLexer.g4 JavaParser.g4 -visitor -o ../src/parsers/generated