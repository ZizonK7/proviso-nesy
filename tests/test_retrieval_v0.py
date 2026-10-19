import unittest

from experiments.retrieval_v0.data import Case, Dataset, all_datasets
from experiments.retrieval_v0.score import best_k, evaluate


class RetrievalV0(unittest.TestCase):
    def test_counts_type1_and_type2(self):
        ds = Dataset("t", {"a": "", "b": "", "c": ""}, [Case("q", "", yes={"a", "c"}, no={"b"})])
        perfect_wrong = lambda q, cands: {"b": 3, "a": 2, "c": 1}  # 헛짚음을 1등에
        results, per_state = evaluate(ds, perfect_wrong, ks=(1, 2, 3))
        k1, k2, k3 = results
        self.assertEqual((k1.recall, k1.false_alarms, k1.misses), (0.0, 1.0, 2.0))
        self.assertEqual((k2.recall, k2.precision), (0.5, 0.5))
        self.assertEqual((k3.recall, k3.misses), (1.0, 0.0))
        self.assertEqual(best_k(results, 20)[0], 3)  # 놓침이 비싸면 넉넉히
        self.assertEqual(best_k(results, 0.1)[0], 1)  # 놓침이 싸면 적게

    def test_datasets_load(self):
        for ds in all_datasets():
            self.assertTrue(ds.cases)
            for c in ds.cases:
                self.assertTrue((c.yes | c.no) <= set(ds.candidates), c.id)


if __name__ == "__main__":
    unittest.main()
