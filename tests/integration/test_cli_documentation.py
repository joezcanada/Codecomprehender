import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

from src.cli import cli
from src.schemas.documentation_schema import (
    FileDocumentation,
    ClassDocumentation,
    DocumentationElement,
)


class TestCLIDocumentation:

    @pytest.fixture
    def temp_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_java_project(self):
        return Path(__file__).parent.parent / "fixtures" / "example_java_project"

    @pytest.fixture
    def complex_java_project(self):
        return Path(__file__).parent.parent / "fixtures" / "complex_java_project"

    @pytest.fixture
    def mock_llm_responses(self):
        calculator_class = ClassDocumentation(
            type="class",
            name="Calculator",
            comment="/**\n * A simple calculator class for basic arithmetic operations.\n */",
            constructors={
                "Calculator": DocumentationElement(
                    comment="/**\n * Creates a new Calculator with initial result of 0.\n */"
                )
            },
            methods={
                "add": DocumentationElement(
                    comment="/**\n * Adds two integers and stores the result.\n */"
                ),
                "getResult": DocumentationElement(
                    comment="/**\n * Returns the last calculated result.\n */"
                ),
            },
        )

        user_service_class = ClassDocumentation(
            type="class",
            name="UserService",
            methods={
                "saveUser": DocumentationElement(
                    comment="/**\n * Saves user information to the system.\n */"
                )
            },
        )

        order_manager_class = ClassDocumentation(
            type="class",
            name="OrderManager",
            comment="/**\n * Manages customer orders and provides order processing functionality.\n */",
            constructors={
                "OrderManager": DocumentationElement(
                    comment="/**\n * Creates a new OrderManager with an empty order list.\n */"
                )
            },
            methods={
                "addOrder": DocumentationElement(
                    comment="/**\n * Adds a new order to the system.\n */"
                ),
                "getOrdersByCustomer": DocumentationElement(
                    comment="/**\n * Retrieves all orders for a specific customer.\n */"
                ),
                "calculateTotal": DocumentationElement(
                    comment="/**\n * Calculates the total amount of all orders.\n */"
                ),
            },
        )

        return {
            "Calculator": FileDocumentation(classes={"Calculator": calculator_class}),
            "UserService": FileDocumentation(
                classes={"UserService": user_service_class}
            ),
            "OrderManager": FileDocumentation(
                classes={"OrderManager": order_manager_class}
            ),
        }

    def test_basic_documentation_without_copy(
        self, sample_java_project, mock_llm_responses
    ):
        runner = CliRunner()

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                if "Calculator" in user_input:
                    return mock_llm_responses["Calculator"]
                elif "UserService" in user_input:
                    return mock_llm_responses["UserService"]
                elif "OrderManager" in user_input:
                    return mock_llm_responses["OrderManager"]
                return FileDocumentation(classes={})

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(cli, ["document", str(sample_java_project)])
            assert result.exit_code == 0
            assert "files successfully documented" in result.output

    def test_documentation_with_copy_option(
        self, sample_java_project, mock_llm_responses, temp_dir
    ):
        runner = CliRunner()
        output_dir = Path(temp_dir) / "documented_output"

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                if "Calculator" in user_input:
                    return mock_llm_responses["Calculator"]
                elif "UserService" in user_input:
                    return mock_llm_responses["UserService"]
                elif "OrderManager" in user_input:
                    return mock_llm_responses["OrderManager"]
                return FileDocumentation(classes={})

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(
                cli,
                [
                    "document",
                    str(sample_java_project),
                    "--copy",
                    "--output-dir",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            assert output_dir.exists()
            output_project = output_dir / "output" / "example_java_project"
            assert (output_project / "Calculator.java").exists()
            assert (output_project / "UserService.java").exists()
            assert (output_project / "OrderManager.java").exists()

    def test_existing_documentation_skip_mode(
        self, sample_java_project, mock_llm_responses
    ):
        runner = CliRunner()

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                if "Calculator" in user_input:
                    return mock_llm_responses["Calculator"]
                elif "UserService" in user_input:
                    return mock_llm_responses["UserService"]
                elif "OrderManager" in user_input:
                    return mock_llm_responses["OrderManager"]
                return FileDocumentation(classes={})

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(
                cli, ["document", str(sample_java_project), "--existing", "skip"]
            )
            assert result.exit_code == 0

    def test_existing_documentation_override_mode(
        self, sample_java_project, mock_llm_responses
    ):
        runner = CliRunner()

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                if "Calculator" in user_input:
                    return mock_llm_responses["Calculator"]
                elif "UserService" in user_input:
                    return mock_llm_responses["UserService"]
                elif "OrderManager" in user_input:
                    return mock_llm_responses["OrderManager"]
                return FileDocumentation(classes={})

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(
                cli, ["document", str(sample_java_project), "--existing", "override"]
            )
            assert result.exit_code == 0

    def test_existing_documentation_keep_both_mode(
        self, sample_java_project, mock_llm_responses
    ):
        runner = CliRunner()

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                if "Calculator" in user_input:
                    return mock_llm_responses["Calculator"]
                elif "UserService" in user_input:
                    return mock_llm_responses["UserService"]
                elif "OrderManager" in user_input:
                    return mock_llm_responses["OrderManager"]
                return FileDocumentation(classes={})

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(
                cli, ["document", str(sample_java_project), "--existing", "keep-both"]
            )
            assert result.exit_code == 0

    def test_single_file_documentation(self, sample_java_project, mock_llm_responses):
        runner = CliRunner()
        single_file = sample_java_project / "Calculator.java"

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                return mock_llm_responses["Calculator"]

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(cli, ["document", str(single_file)])
            assert result.exit_code == 0

    def test_empty_directory_handling(self, temp_dir):
        runner = CliRunner()
        empty_dir = Path(temp_dir) / "empty_project"
        empty_dir.mkdir()

        result = runner.invoke(cli, ["document", str(empty_dir)])
        assert result.exit_code in [0, 1]

    def test_documentation_content_integration(
        self, sample_java_project, mock_llm_responses, temp_dir
    ):
        runner = CliRunner()
        output_dir = Path(temp_dir) / "content_test_output"

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, user_input):
                if "Calculator" in user_input:
                    return mock_llm_responses["Calculator"]
                elif "UserService" in user_input:
                    return mock_llm_responses["UserService"]
                elif "OrderManager" in user_input:
                    return mock_llm_responses["OrderManager"]
                return FileDocumentation(classes={})

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(
                cli,
                [
                    "document",
                    str(sample_java_project),
                    "--copy",
                    "--output-dir",
                    str(output_dir),
                ],
            )

            assert result.exit_code == 0
            output_project = output_dir / "output" / "example_java_project"
            calculator_content = (output_project / "Calculator.java").read_text()
            assert "/**" in calculator_content
            assert (
                "Creates a new Calculator" in calculator_content
                or "Adds two integers" in calculator_content
            )

    def test_llm_service_error_handling(self, sample_java_project):
        runner = CliRunner()

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance
            mock_instance.invoke.side_effect = Exception("API Error")

            result = runner.invoke(cli, ["document", str(sample_java_project)])
            assert result.exit_code in [0, 1]
            if result.exit_code == 1:
                error_output = result.output + (result.stderr or "")
                assert "Error" in error_output or "API Error" in error_output

    def test_invalid_existing_mode(self, sample_java_project):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["document", str(sample_java_project), "--existing", "invalid_mode"]
        )
        assert result.exit_code != 0

    def test_nonexistent_path(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["document", "/nonexistent/path"])
        assert result.exit_code != 0

    def test_complex_project_structure(self, complex_java_project):
        runner = CliRunner()

        with patch("src.services.llm_service.LLMService") as mock_llm_class:
            mock_instance = MagicMock()
            mock_llm_class.return_value = mock_instance

            def mock_invoke(_response_model, _system_prompt, _user_input):
                return FileDocumentation(
                    classes={
                        "MainApplication": ClassDocumentation(
                            type="class",
                            name="MainApplication",
                            comment="/**\n * Main application entry point.\n */",
                        )
                    }
                )

            mock_instance.invoke.side_effect = mock_invoke
            result = runner.invoke(cli, ["document", str(complex_java_project)])
            assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
