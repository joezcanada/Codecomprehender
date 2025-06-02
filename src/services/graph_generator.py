import logging
from typing import Optional
from src.models.architecture_models import ProjectAnalysis

logger = logging.getLogger(__name__)

try:
    import graphviz

    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    logger.warning("Graphviz not available")


class GraphGenerator:
    def render_call_graph(
        self, analysis: ProjectAnalysis, output_path: str, format: str = "png"
    ) -> Optional[str]:
        dot_source = self._generate_call_graph_dot(analysis)
        return self._render_graph(dot_source, output_path, format, "Call")

    def render_ast_graph(
        self, analysis: ProjectAnalysis, output_path: str, format: str = "png"
    ) -> Optional[str]:
        dot_source = self._generate_ast_graph_dot(analysis)
        return self._render_graph(dot_source, output_path, format, "AST")

    def is_graphviz_available(self) -> bool:
        return GRAPHVIZ_AVAILABLE

    def _generate_call_graph_dot(self, analysis: ProjectAnalysis) -> str:
        dot_lines = ["digraph CallGraph {"]
        dot_lines.append("    rankdir=TB;")
        dot_lines.append("    compound=true;")
        dot_lines.append("    node [shape=box];")

        all_classes = analysis.get_all_classes()
        class_counter = 0

        for cls in all_classes:
            class_counter += 1
            cluster_name = f"cluster_{class_counter}"

            class_label = self._sanitize_dot_label(cls.name)
            dot_lines.append(f"    subgraph {cluster_name} {{")
            dot_lines.append(f'        label="{class_label}";')
            dot_lines.append("        style=filled;")
            dot_lines.append("        color=lightblue;")
            dot_lines.append("        fontsize=16;")
            dot_lines.append("        fontweight=bold;")

            for method in cls.methods:
                method_id = self._sanitize_dot_identifier(f"{cls.name}_{method.name}")
                method_label = self._sanitize_dot_label(
                    f"{method.name}\\n({method.return_type})"
                )
                dot_lines.append(
                    f'        "{method_id}" [label="{method_label}", style=filled, fillcolor=lightgreen];'
                )

            dot_lines.append("    }")

        all_calls = analysis.get_all_method_calls()
        for call in all_calls:
            caller_id = self._sanitize_dot_identifier(
                f"{call.caller_class}_{call.caller_method}"
            )
            called_id = self._sanitize_dot_identifier(
                f"{call.called_class}_{call.called_method}"
            )

            edge_label = self._sanitize_dot_label(f"line {call.line_number}")
            dot_lines.append(
                f'    "{caller_id}" -> "{called_id}" [label="{edge_label}", color=red, fontsize=10];'
            )

        dot_lines.append("    subgraph cluster_legend {")
        dot_lines.append('        label="Legend";')
        dot_lines.append("        style=filled;")
        dot_lines.append("        color=lightyellow;")
        dot_lines.append(
            '        legend_class [label="Class", style=filled, fillcolor=lightblue, shape=box];'
        )
        dot_lines.append(
            '        legend_method [label="Method", style=filled, fillcolor=lightgreen, shape=box];'
        )
        dot_lines.append(
            '        legend_call [label="Method Call", color=red, shape=none];'
        )
        dot_lines.append("        legend_class -> legend_method [style=invisible];")
        dot_lines.append("        legend_method -> legend_call [style=invisible];")
        dot_lines.append("    }")

        dot_lines.append("}")
        return "\n".join(dot_lines)

    def _generate_ast_graph_dot(self, analysis: ProjectAnalysis) -> str:
        dot_lines = ["digraph AST {"]
        dot_lines.append("    rankdir=TB;")
        dot_lines.append("    node [shape=ellipse];")

        node_counter = 0

        def add_ast_node(node, parent_id=None, file_name=""):
            nonlocal node_counter
            current_id = f"node_{node_counter}"
            node_counter += 1

            label = self._sanitize_dot_label(node.name or node.node_type)
            if node.line_number:
                label += f"\\n(line {node.line_number})"

            color = "lightblue"
            if node.node_type == "ClassDeclaration":
                color = "lightcoral"
            elif node.node_type == "MethodDeclaration":
                color = "lightgreen"
            elif node.node_type == "FieldDeclaration":
                color = "lightyellow"
            elif node.node_type == "MethodCall":
                color = "lightpink"
            elif node.node_type == "ConstructorDeclaration":
                color = "lightseagreen"

            dot_lines.append(
                f'    {current_id} [label="{label}", style=filled, fillcolor={color}];'
            )

            if parent_id:
                dot_lines.append(f"    {parent_id} -> {current_id};")

            for child in node.children:
                add_ast_node(child, current_id, file_name)

            return current_id

        file_counter = 0
        for file_analysis in analysis.files:
            if file_analysis.ast_nodes:
                file_counter += 1
                file_name = (
                    file_analysis.file_path.split("/")[-1]
                    if "/" in file_analysis.file_path
                    else file_analysis.file_path
                )

                file_label = self._sanitize_dot_label(f"File: {file_name}")
                dot_lines.append(f"    subgraph cluster_file_{file_counter} {{")
                dot_lines.append(f'        label="{file_label}";')
                dot_lines.append("        style=filled;")
                dot_lines.append("        color=lightgray;")
                dot_lines.append("        fontsize=14;")
                dot_lines.append("        fontweight=bold;")

                for ast_node in file_analysis.ast_nodes:
                    add_ast_node(ast_node, None, file_name)

                dot_lines.append("    }")

        dot_lines.append("    subgraph cluster_ast_legend {")
        dot_lines.append('        label="AST Legend";')
        dot_lines.append("        style=filled;")
        dot_lines.append("        color=lightyellow;")
        dot_lines.append(
            '        ast_class [label="Class", style=filled, fillcolor=lightcoral];'
        )
        dot_lines.append(
            '        ast_method [label="Method", style=filled, fillcolor=lightgreen];'
        )
        dot_lines.append(
            '        ast_field [label="Field", style=filled, fillcolor=lightyellow];'
        )
        dot_lines.append(
            '        ast_call [label="Method Call", style=filled, fillcolor=lightpink];'
        )
        dot_lines.append(
            '        ast_constructor [label="Constructor", style=filled, fillcolor=lightseagreen];'
        )
        dot_lines.append("    }")

        dot_lines.append("}")
        return "\n".join(dot_lines)

    def _render_graph(
        self, dot_source: str, output_path: str, format: str, graph_type: str
    ) -> Optional[str]:
        if not GRAPHVIZ_AVAILABLE:
            logger.warning(f"Cannot render {graph_type} graph - Graphviz not available")
            return None

        try:
            graph = graphviz.Source(dot_source)
            output_file = graph.render(output_path, format=format, cleanup=True)
            logger.info(f"{graph_type} graph rendered to: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to render {graph_type} graph: {e}")
            return None

    def _sanitize_dot_identifier(self, text: str) -> str:
        if not text:
            return "unknown"
        sanitized = (
            text.replace("@", "AT_")
            .replace(".", "_")
            .replace("<", "_LT_")
            .replace(">", "_GT_")
            .replace("(", "_LP_")
            .replace(")", "_RP_")
            .replace("[", "_LB_")
            .replace("]", "_RB_")
            .replace("{", "_LC_")
            .replace("}", "_RC_")
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace(";", "_")
            .replace(",", "_")
            .replace("=", "_EQ_")
            .replace("+", "_PLUS_")
            .replace("*", "_STAR_")
            .replace("?", "_Q_")
            .replace("!", "_EX_")
            .replace("&", "_AMP_")
            .replace("|", "_PIPE_")
            .replace("^", "_CARET_")
            .replace("%", "_PCT_")
            .replace("#", "_HASH_")
            .replace("$", "_DOLLAR_")
        )

        if sanitized and not (sanitized[0].isalpha() or sanitized[0] == "_"):
            sanitized = "ID_" + sanitized

        return sanitized or "unknown"

    def _sanitize_dot_label(self, text: str) -> str:
        if not text:
            return "unknown"
        return text.replace("\\", "\\\\").replace('"', '\\"')
