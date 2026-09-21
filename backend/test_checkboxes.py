import unittest

from backend.checkboxes import checkbox_ok_fallo, checkbox_ok_na, checkbox_si_no


class CheckboxFormattingTests(unittest.TestCase):
    def test_bisagras_failure_marks_fallo_not_both_empty(self):
        """A failed hinge inspection must check Fallo, not leave both boxes blank."""
        self.assertEqual(checkbox_ok_fallo(True), "☑ OK  ☐ Fallo")
        self.assertEqual(checkbox_ok_fallo(False), "☐ OK  ☑ Fallo")
        self.assertIn("☑", checkbox_ok_fallo(False))
        self.assertNotEqual(checkbox_ok_fallo(False), "☐ OK  ☐ Fallo")

    def test_epp_and_na_checkboxes_toggle_the_unchecked_side(self):
        self.assertEqual(checkbox_si_no(False), "☐ Sí  ☑ No")
        self.assertEqual(checkbox_ok_na(False), "☐ OK  ☑ N/A")


if __name__ == "__main__":
    unittest.main()
