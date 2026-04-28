import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / ".claude" / "hooks" / "redirect_docs_to_rag_md.py"


def load_module(module_path: Path = MODULE_PATH):
    spec = importlib.util.spec_from_file_location("redirect_docs_to_rag_md", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DocRedirectHookTests(unittest.TestCase):
    def test_discovers_repo_root_from_module_location(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "portable-repo"
            hook_dir = repo_root / ".claude" / "hooks"
            hook_dir.mkdir(parents=True)
            copied_module_path = hook_dir / "redirect_docs_to_rag_md.py"
            shutil.copy2(MODULE_PATH, copied_module_path)

            module = load_module(copied_module_path)

            self.assertEqual(repo_root.resolve(), module.discover_repo_root())
            self.assertEqual(repo_root.resolve(), module.REPO_ROOT)

    def test_rewrites_supported_docs_path_into_nested_repo(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "LocalRAG"
            nested_repo = repo_root / "RAG_md"
            nested_repo.mkdir(parents=True)

            self.assertEqual(
                nested_repo / "docs" / "references.md",
                module.rewrite_target_path(
                    repo_root / "docs" / "references.md",
                    repo_root=repo_root,
                ),
            )
            self.assertEqual(
                nested_repo / "TODO.md",
                module.rewrite_target_path(repo_root / "TODO.md", repo_root=repo_root),
            )
            self.assertEqual(
                nested_repo / "docs" / "superpowers" / "plan.md",
                module.rewrite_target_path(
                    repo_root / "docs" / "superpowers" / "plan.md",
                    repo_root=repo_root,
                ),
            )

    def test_excludes_readme_evaluation_repo_guide_and_results(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "LocalRAG"
            (repo_root / "RAG_md").mkdir(parents=True)

            self.assertEqual(
                repo_root / "README.md",
                module.rewrite_target_path(repo_root / "README.md", repo_root=repo_root),
            )
            self.assertEqual(
                repo_root / "docs" / "evaluation.md",
                module.rewrite_target_path(
                    repo_root / "docs" / "evaluation.md", repo_root=repo_root
                ),
            )
            self.assertEqual(
                repo_root / "docs" / "repo_guide.md",
                module.rewrite_target_path(
                    repo_root / "docs" / "repo_guide.md", repo_root=repo_root
                ),
            )
            self.assertEqual(
                repo_root / "results" / "report.md",
                module.rewrite_target_path(
                    repo_root / "results" / "report.md", repo_root=repo_root
                ),
            )

    def test_excludes_noncanonical_evaluation_path_after_normalization(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "LocalRAG"
            (repo_root / "RAG_md").mkdir(parents=True)

            self.assertEqual(
                repo_root / "docs" / "evaluation.md",
                module.rewrite_target_path(
                    repo_root / "docs" / "superpowers" / ".." / "evaluation.md",
                    repo_root=repo_root,
                ),
            )

    def test_keeps_paths_already_under_nested_repo(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "LocalRAG"
            nested_repo = repo_root / "RAG_md"
            nested_repo.mkdir(parents=True)
            already_nested = nested_repo / "docs" / "superpowers" / "plan.md"

            self.assertEqual(
                already_nested,
                module.rewrite_target_path(already_nested, repo_root=repo_root),
            )

    def test_raises_when_nested_repo_is_missing_for_rewritten_paths(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "LocalRAG"

            with self.assertRaisesRegex(FileNotFoundError, r"RAG_md"):
                module.rewrite_target_path(repo_root / "TODO.md", repo_root=repo_root)

    def test_build_updated_input_rewrites_file_path_only(self):
        module = load_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / "LocalRAG"
            nested_repo = repo_root / "RAG_md"
            nested_repo.mkdir(parents=True)

            tool_input = {
                "file_path": str(repo_root / "docs" / "references.md"),
                "other": {"keep": True},
            }

            self.assertEqual(
                {
                    "file_path": str(nested_repo / "docs" / "references.md"),
                    "other": {"keep": True},
                },
                module.build_updated_input(tool_input, repo_root=repo_root),
            )
            self.assertEqual(
                {
                    "file_path": str(repo_root / "docs" / "references.md"),
                    "other": {"keep": True},
                },
                tool_input,
            )

    def test_main_outputs_allow_response_with_updated_input(self):
        module = load_module()

        updated_input = {"file_path": "/tmp/rewritten.md", "other": "value"}
        stdin = io.StringIO(json.dumps({"tool_input": {"file_path": "/tmp/original.md"}}))
        stdout = io.StringIO()

        with patch.object(module, "build_updated_input", return_value=updated_input):
            with patch("sys.stdin", stdin), patch("sys.stdout", stdout):
                self.assertEqual(0, module.main())

        self.assertEqual(
            {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "updatedInput": updated_input,
                },
            },
            json.loads(stdout.getvalue()),
        )

    def test_main_outputs_deny_response_when_nested_repo_missing(self):
        module = load_module()

        error_message = "Expected nested docs repo at /tmp/LocalRAG/RAG_md"
        stdin = io.StringIO(json.dumps({"tool_input": {"file_path": "/tmp/original.md"}}))
        stdout = io.StringIO()

        with patch.object(module, "build_updated_input", side_effect=FileNotFoundError(error_message)):
            with patch("sys.stdin", stdin), patch("sys.stdout", stdout):
                self.assertEqual(0, module.main())

        self.assertEqual(
            {
                "continue": False,
                "stopReason": error_message,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": error_message,
                },
            },
            json.loads(stdout.getvalue()),
        )


if __name__ == "__main__":
    unittest.main()
