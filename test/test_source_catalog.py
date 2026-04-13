import unittest
from pathlib import Path

from source_catalog import ROOT, REGISTRY_REL_PATH, SOURCE_DOCUMENTS, documents_for_category


class ApolloSourceCatalogTests(unittest.TestCase):
    def test_apollo_catalog_matches_raw_directory(self):
        expected = {
            path.name
            for path in (ROOT / "data" / "sources" / "raw" / "apollo").glob("*.pdf")
        }
        actual = {Path(doc.raw_relpath).name for doc in documents_for_category("apollo")}
        self.assertEqual(expected, actual)

    def test_apollo_output_paths_land_in_apollo_directory(self):
        actual = {doc.clean_relpath for doc in documents_for_category("apollo")}
        self.assertEqual(
            {
                "data/sources/apollo/apollo-devcenter-learning-path.md",
                "data/sources/apollo/apollo-cyber-rt.md",
                "data/sources/apollo/apollo-channel-data-format.md",
                "data/sources/apollo/apollo-open-platform-overview.md",
                "data/sources/apollo/apollo-perception-fusion-overview.md",
                "data/sources/apollo/apollo-vision-perception-overview.md",
                "data/sources/apollo/apollo-vision-prediction-overview.md",
                "data/sources/apollo/apollo-vision-plan-overview.md",
                "data/sources/apollo/apollo-vision-control-overview.md",
                "data/sources/apollo/apollo-vision-location-overview.md",
            },
            actual,
        )

    def test_source_ids_are_unique(self):
        source_ids = [doc.source_id for doc in SOURCE_DOCUMENTS]
        self.assertEqual(len(source_ids), len(set(source_ids)))


class FullSourceCatalogTests(unittest.TestCase):
    def test_catalog_matches_all_raw_pdfs(self):
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "data" / "sources" / "raw").rglob("*.pdf")
        }
        actual = {doc.raw_relpath for doc in SOURCE_DOCUMENTS}
        self.assertEqual(expected, actual)

    def test_source_document_metadata_contract(self):
        for doc in SOURCE_DOCUMENTS:
            self.assertIn(doc.category, {"apollo", "standards", "papers"})
            self.assertIn(doc.source_type, {"official_doc", "standard", "paper", "report"})
            if doc.category == "apollo":
                self.assertEqual("official_doc", doc.source_type)
            elif doc.category == "standards":
                self.assertEqual("standard", doc.source_type)
            else:
                self.assertIn(doc.source_type, {"paper", "report"})
            self.assertTrue(doc.raw_relpath.endswith(".pdf"))
            self.assertTrue(doc.clean_relpath.endswith(".md"))
            self.assertGreater(len(doc.topic_tags), 0)
            self.assertTrue(doc.origin_url == "unknown" or doc.origin_url.startswith("https://"))

    def test_category_counts_match_scope(self):
        self.assertEqual(10, len(documents_for_category("apollo")))
        self.assertEqual(9, len(documents_for_category("standards")))
        self.assertEqual(7, len(documents_for_category("papers")))

    def test_registry_path_is_stable(self):
        self.assertEqual("data/evaluation/shared/source_registry.json", REGISTRY_REL_PATH)

    def test_clean_paths_are_unique(self):
        clean_paths = [doc.clean_relpath for doc in SOURCE_DOCUMENTS]
        self.assertEqual(len(clean_paths), len(set(clean_paths)))


if __name__ == "__main__":
    unittest.main()
