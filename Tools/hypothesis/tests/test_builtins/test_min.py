import unittest

from hypothesis import given, strategies as st


class TestMin(unittest.TestCase):
    @given(
        st.one_of(
            st.lists(st.integers()), st.tuples(st.integers()),
        ).filter(lambda seq: len(seq) != 0)
    )
    def test_min(self, seq):
        lower = min(seq)
        for item in seq:
            self.assertLessEqual(lower, item)
