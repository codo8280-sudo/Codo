import unittest

from app.services.chunking import split_text


class ChunkingTests(unittest.TestCase):
    def test_empty_text_has_no_chunks(self):
        self.assertEqual(split_text("   \n "), [])

    def test_chunks_keep_content_with_overlap(self):
        text = " ".join(f"mot{i}" for i in range(300))
        chunks = split_text(text, target_chars=180, overlap_chars=30)
        self.assertGreater(len(chunks), 2)
        self.assertTrue(all(chunk.strip() for chunk in chunks))
        self.assertIn("mot0", chunks[0])
        self.assertIn("mot299", chunks[-1])


if __name__ == "__main__":
    unittest.main()
