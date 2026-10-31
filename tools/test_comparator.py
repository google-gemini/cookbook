#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for tools/nb_tester/comparator.py exact_or_fuzzy comparison logic."""

import unittest

from tools.nb_tester.comparator import CellOutputSnapshot, OutputComparator
from tools.nb_tester.config import TesterConfig


class TestOutputComparatorExactOrFuzzy(unittest.TestCase):
    """Test suite for OutputComparator deterministic exact_or_fuzzy evaluation."""

    def setUp(self) -> None:
        self.config = TesterConfig()
        self.comparator = OutputComparator(config=self.config)

    def _compare(self, old_text: str, new_text: str):
        old_snap = CellOutputSnapshot(
            text_content=old_text, image_count=0, audio_count=0, html_present=False
        )
        new_snap = CellOutputSnapshot(
            text_content=new_text, image_count=0, audio_count=0, html_present=False
        )
        return self.comparator._compare_exact_or_fuzzy(
            cell_index=0,
            source_code="test()",
            old_snap=old_snap,
            new_snap=new_snap,
            old_snip=old_text,
            new_snip=new_text,
        )

    def test_status_text_change_is_regression(self) -> None:
        """Regression test for #1442: changed status text with same digits must be a regression."""
        report = self._compare("PASS: 1 checks", "FAIL: 1 checks")
        self.assertEqual(report.verdict, "REGRESSION")
        self.assertTrue(report.is_regression)

    def test_sign_flip_is_regression(self) -> None:
        """Regression test for #1442: sign reversal must be flagged as a regression."""
        report = self._compare("Balance: 42", "Balance: -42")
        self.assertEqual(report.verdict, "REGRESSION")
        self.assertTrue(report.is_regression)

    def test_exact_match(self) -> None:
        """Exact identical output reports MATCH."""
        report = self._compare("Result: 100", "Result: 100")
        self.assertEqual(report.verdict, "MATCH")
        self.assertFalse(report.is_regression)

    def test_acceptable_numeric_drift(self) -> None:
        """Small numeric variations within 35% tolerance report SLIGHT_VARIATION."""
        report = self._compare("Tokens: 100", "Tokens: 105")
        self.assertEqual(report.verdict, "SLIGHT_VARIATION")
        self.assertFalse(report.is_regression)

    def test_excessive_numeric_drift_is_regression(self) -> None:
        """Numeric variations exceeding 35% tolerance report REGRESSION."""
        report = self._compare("Tokens: 100", "Tokens: 150")
        self.assertEqual(report.verdict, "REGRESSION")
        self.assertTrue(report.is_regression)

    def test_nonnumeric_text_regression(self) -> None:
        """Plain textual status changes without digits report REGRESSION."""
        report = self._compare("PASS", "FAIL")
        self.assertEqual(report.verdict, "REGRESSION")
        self.assertTrue(report.is_regression)

    def test_float_numeric_drift(self) -> None:
        """Floating point values within tolerance report SLIGHT_VARIATION."""
        report = self._compare("Loss: 0.05", "Loss: 0.06")
        self.assertEqual(report.verdict, "SLIGHT_VARIATION")
        self.assertFalse(report.is_regression)

    def test_negative_values_drift(self) -> None:
        """Negative numbers with small variation report SLIGHT_VARIATION."""
        report = self._compare("Score: -10", "Score: -12")
        self.assertEqual(report.verdict, "SLIGHT_VARIATION")
        self.assertFalse(report.is_regression)

    def test_scientific_notation_drift(self) -> None:
        """Scientific notation values within tolerance report SLIGHT_VARIATION."""
        report = self._compare("Loss: 1.2e-5", "Loss: 1.3e-5")
        self.assertEqual(report.verdict, "SLIGHT_VARIATION")
        self.assertFalse(report.is_regression)

    def test_scientific_notation_regression(self) -> None:
        """Scientific notation values with large exponent drift report REGRESSION."""
        report = self._compare("Loss: 1e-5", "Loss: 1e-6")
        self.assertEqual(report.verdict, "REGRESSION")
        self.assertTrue(report.is_regression)


if __name__ == "__main__":
    unittest.main()
