from typing import List, Dict, Optional
from src.models.architecture_models import (
    ClassInfo,
    MethodInfo,
    FieldInfo,
    MethodCall,
    ASTNode,
)
from src.parsers.generated.JavaParser import JavaParser
from src.parsers.generated.JavaParserListener import JavaParserListener


class CallGraphListener(JavaParserListener):

    def __init__(self):
        self.classes: List[ClassInfo] = []
        self.method_calls: List[MethodCall] = []
        self.current_class: Optional[ClassInfo] = None
        self.current_method: Optional[str] = None
        self.imports: Dict[str, str] = {}
        self.fields: Dict[str, str] = {}
        self.local_vars: Dict[str, str] = {}

    def _safe_get_text(self, ctx, default: str = "") -> str:
        return ctx.getText() if ctx else default

    def _safe_get_line(self, ctx) -> int:
        return ctx.start.line if ctx and ctx.start else 0

    def _get_or_create_class(self, class_name: str) -> ClassInfo:
        for cls in self.classes:
            if cls.name == class_name:
                return cls
        new_class = ClassInfo(name=class_name)
        self.classes.append(new_class)
        return new_class

    def _resolve_target_class(self, object_name: str) -> str:
        return (
            self.local_vars.get(object_name)
            or self.fields.get(object_name)
            or self.imports.get(object_name)
            or object_name
        )

    def _add_method_call(self, called_class: str, called_method: str, line_number: int):
        if not self.current_class or not self.current_method:
            return

        method_call = MethodCall(
            caller_class=self.current_class.name,
            caller_method=self.current_method,
            called_class=called_class,
            called_method=called_method,
            line_number=line_number,
        )
        self.method_calls.append(method_call)

    def enterImportDeclaration(self, ctx: JavaParser.ImportDeclarationContext):
        qualified_name = self._safe_get_text(ctx.qualifiedName())
        if qualified_name:
            parts = qualified_name.split(".")
            simple_name = parts[-1]
            self.imports[simple_name] = qualified_name

    def enterClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = self._safe_get_text(ctx.identifier())
        if class_name:
            self.current_class = self._get_or_create_class(class_name)

    def exitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        self.current_class = None

    def enterFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        if not self.current_class:
            return

        type_text = self._safe_get_text(ctx.typeType(), "Object")
        field_type = type_text.split("<")[0]

        declarators = self._safe_get_text(ctx.variableDeclarators())
        for part in declarators.split(","):
            field_name = part.split("=")[0].strip()
            if field_name and field_name.isidentifier():
                field_info = FieldInfo(
                    name=field_name,
                    class_type=field_type,
                    declaring_class=self.current_class.name,
                )
                self.current_class.fields.append(field_info)
                self.fields[field_name] = field_type

    def enterMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        if not self.current_class:
            return

        method_name = self._safe_get_text(ctx.identifier())
        if not method_name:
            return

        self.current_method = method_name
        self.local_vars.clear()

        return_type = "void"
        if ctx.typeTypeOrVoid():
            return_type = self._safe_get_text(ctx.typeTypeOrVoid())

        method_info = MethodInfo(
            name=method_name,
            class_name=self.current_class.name,
            return_type=return_type,
        )
        self.current_class.methods.append(method_info)

    def exitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        self.current_method = None
        self.local_vars.clear()

    def enterConstructorDeclaration(
        self, ctx: JavaParser.ConstructorDeclarationContext
    ):
        if not self.current_class:
            return

        constructor_name = self._safe_get_text(ctx.identifier())
        if constructor_name:
            self.current_method = constructor_name
            self.local_vars.clear()

            method_info = MethodInfo(
                name=constructor_name,
                class_name=self.current_class.name,
                return_type="void",
            )
            self.current_class.methods.append(method_info)

    def exitConstructorDeclaration(self, ctx: JavaParser.ConstructorDeclarationContext):
        self.current_method = None
        self.local_vars.clear()

    def enterLocalVariableDeclaration(
        self, ctx: JavaParser.LocalVariableDeclarationContext
    ):
        type_text = self._safe_get_text(ctx.typeType(), "Object")
        var_type = type_text.split("<")[0]

        declarators = self._safe_get_text(ctx.variableDeclarators())
        for part in declarators.split(","):
            var_name = part.split("=")[0].strip()
            if var_name and var_name.isidentifier():
                self.local_vars[var_name] = var_type

    def enterMethodCall(self, ctx: JavaParser.MethodCallContext):
        if not self.current_class or not self.current_method:
            return

        full_text = self._safe_get_text(ctx)
        method_name = self._safe_get_text(ctx.identifier())
        line_number = self._safe_get_line(ctx)

        parent_text = self._safe_get_text(ctx.parentCtx) if ctx.parentCtx else ""

        if "." in parent_text and method_name:
            method_call_start = parent_text.find(full_text)
            if method_call_start > 0:
                object_part = parent_text[: method_call_start - 1]
                target_class = self._resolve_target_class(object_part)
                self._add_method_call(target_class, method_name, line_number)
            else:
                self._add_method_call(self.current_class.name, method_name, line_number)
        elif method_name:
            self._add_method_call(self.current_class.name, method_name, line_number)

    def enterMethodCallExpression(self, ctx: JavaParser.MethodCallExpressionContext):
        if not self.current_class or not self.current_method:
            return

        full_text = self._safe_get_text(ctx)
        line_number = self._safe_get_line(ctx)

        if "." in full_text:
            parts = full_text.split(".")
            method_part = parts[-1].split("(")[0]
            object_part = ".".join(parts[:-1])

            target_class = self._resolve_target_class(object_part)
            self._add_method_call(target_class, method_part, line_number)
        else:
            method_name = full_text.split("(")[0]
            self._add_method_call(self.current_class.name, method_name, line_number)

    def enterObjectCreationExpression(
        self, ctx: JavaParser.ObjectCreationExpressionContext
    ):
        if not self.current_class or not self.current_method:
            return

        creator = ctx.creator()
        if creator and creator.createdName():
            class_name = self._safe_get_text(creator.createdName())
            if class_name:
                target_class = self._resolve_target_class(class_name)
                line_number = self._safe_get_line(ctx)
                self._add_method_call(target_class, "<constructor>", line_number)


class ASTListener(JavaParserListener):

    def __init__(self):
        self.ast_nodes: List[ASTNode] = []
        self.node_stack: List[ASTNode] = []

    def _create_node(self, ctx, node_type: str, name: str = None):
        line_number = ctx.start.line if ctx and ctx.start else 0
        node_name = name or (ctx.getText()[:50] if ctx else node_type)

        node = ASTNode(
            node_type=node_type,
            name=node_name,
            line_number=line_number,
        )

        if self.node_stack:
            self.node_stack[-1].children.append(node)
        else:
            self.ast_nodes.append(node)

        self.node_stack.append(node)

    def _exit_node(self):
        if self.node_stack:
            self.node_stack.pop()

    def enterCompilationUnit(self, ctx: JavaParser.CompilationUnitContext):
        self._create_node(ctx, "CompilationUnit", "CompilationUnit")

    def exitCompilationUnit(self, ctx: JavaParser.CompilationUnitContext):
        self._exit_node()

    def enterClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        class_name = (
            ctx.identifier().getText() if ctx.identifier() else "AnonymousClass"
        )
        self._create_node(ctx, "ClassDeclaration", class_name)

    def exitClassDeclaration(self, ctx: JavaParser.ClassDeclarationContext):
        self._exit_node()

    def enterMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        method_name = (
            ctx.identifier().getText() if ctx.identifier() else "AnonymousMethod"
        )
        self._create_node(ctx, "MethodDeclaration", method_name)

    def exitMethodDeclaration(self, ctx: JavaParser.MethodDeclarationContext):
        self._exit_node()

    def enterFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        field_names = []
        if ctx.variableDeclarators():
            declarators = ctx.variableDeclarators().getText()
            for part in declarators.split(","):
                field_name = part.split("=")[0].strip()
                if field_name.isidentifier():
                    field_names.append(field_name)

        field_label = ", ".join(field_names) if field_names else "field"
        self._create_node(ctx, "FieldDeclaration", field_label)

    def exitFieldDeclaration(self, ctx: JavaParser.FieldDeclarationContext):
        self._exit_node()

    def enterConstructorDeclaration(
        self, ctx: JavaParser.ConstructorDeclarationContext
    ):
        constructor_name = (
            ctx.identifier().getText() if ctx.identifier() else "Constructor"
        )
        self._create_node(ctx, "ConstructorDeclaration", constructor_name)

    def exitConstructorDeclaration(self, ctx: JavaParser.ConstructorDeclarationContext):
        self._exit_node()
