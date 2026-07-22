import json
import tempfile
import unittest
from pathlib import Path

from config.corpus_profile import load_active_corpus_profile


class ActiveCorpusProfileTests(unittest.TestCase):
    def test_repo_profile_selects_v141_formal_corpus(self):
        profile = load_active_corpus_profile()

        self.assertEqual("v1.4.1", profile.release_version)
        self.assertEqual("rag", profile.collection_name)
        self.assertEqual("doc_type_aware", profile.persist_directory.name)
        self.assertTrue(profile.corpus_fingerprint.startswith("sha256:"))

    def test_relative_corpus_path_resolves_from_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile_path = root / "active.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "contract_version": "active-corpus-v1",
                        "release_version": "test",
                        "persist_directory": "stores/formal",
                        "collection_name": "rag",
                        "corpus_fingerprint": f"sha256:{'a' * 64}",
                        "registry_fingerprint": f"sha256:{'b' * 64}",
                    }
                ),
                encoding="utf-8",
            )

            profile = load_active_corpus_profile(profile_path, project_root=root)

        self.assertEqual((root / "stores" / "formal").resolve(), profile.persist_directory)

    def test_invalid_fingerprint_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_path = Path(temp_dir) / "active.json"
            profile_path.write_text(
                json.dumps(
                    {
                        "contract_version": "active-corpus-v1",
                        "release_version": "test",
                        "persist_directory": "store",
                        "collection_name": "rag",
                        "corpus_fingerprint": "sha256:not-a-digest",
                        "registry_fingerprint": f"sha256:{'b' * 64}",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "corpus_fingerprint"):
                load_active_corpus_profile(profile_path, project_root=temp_dir)


if __name__ == "__main__":
    unittest.main()
