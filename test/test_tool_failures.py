import logging
import unittest

from langchain_core.tools import ToolException

from agent.tools.failures import (
    build_tool_failure,
    classify_tool_error,
    extract_tool_error_code,
    render_tool_error,
    render_tool_validation_error,
)


class ToolFailureContractTests(unittest.TestCase):
    def test_classifies_retry_and_permission_boundaries(self):
        self.assertEqual(
            "tool_timeout",
            classify_tool_error(TimeoutError(), default_code="default"),
        )
        self.assertEqual(
            "tool_unavailable",
            classify_tool_error(ConnectionError(), default_code="default"),
        )
        self.assertEqual(
            "tool_forbidden",
            classify_tool_error(PermissionError(), default_code="default"),
        )
        self.assertEqual(
            "tool_invalid_input",
            classify_tool_error(ValueError(), default_code="default"),
        )
        self.assertEqual(
            "default",
            classify_tool_error(RuntimeError(), default_code="default"),
        )

    def test_rendered_error_contains_code_but_not_private_exception(self):
        logger = logging.getLogger("test.tool_failure")
        with self.assertLogs(logger, level="ERROR"):
            failure = build_tool_failure(
                "知识库检索",
                RuntimeError("private database path"),
                default_code="rag_search_failed",
                logger=logger,
            )

        rendered = render_tool_error(failure)

        self.assertEqual("rag_search_failed", extract_tool_error_code(rendered))
        self.assertIn("知识库检索失败", rendered)
        self.assertNotIn("private database path", rendered)

    def test_unknown_tool_exception_uses_generic_safe_error(self):
        rendered = render_tool_error(ToolException("private details"))

        self.assertEqual("tool_execution_failed", extract_tool_error_code(rendered))
        self.assertNotIn("private details", rendered)

    def test_validation_error_uses_stable_safe_error_code(self):
        rendered = render_tool_validation_error(ValueError("private schema details"))

        self.assertEqual("tool_invalid_input", extract_tool_error_code(rendered))
        self.assertNotIn("private schema details", rendered)


if __name__ == "__main__":
    unittest.main()
