import unittest

from submission.common import address_lines


class AssignmentAddressWrapTests(unittest.TestCase):
    def test_early_comma_does_not_leave_short_line(self):
        address = "No. 8, Building 16, Beilun Industrial Park, Haidian District, Beijing"
        lines = address_lines(address, "", width=40)
        self.assertEqual(lines[0], "No. 8, Building 16, Beilun Industrial")
        self.assertEqual(" ".join(lines), address)
        self.assertTrue(all(len(line) <= 40 for line in lines))

    def test_nearby_comma_is_preferred(self):
        address = "No. 601 Huangpu Avenue West, Tianhe District, Guangzhou"
        lines = address_lines(address, "", width=35)
        self.assertEqual(lines[0], "No. 601 Huangpu Avenue West,")
        self.assertEqual(" ".join(lines), address)

    def test_no_comma_breaks_at_word_boundary(self):
        address = "Building Sixteen Beilun Industrial Park Haidian District"
        lines = address_lines(address, "", width=25)
        self.assertEqual(" ".join(lines), address)
        self.assertTrue(all(len(line) <= 25 for line in lines))

    def test_explicit_address_boundary_is_preserved(self):
        self.assertEqual(address_lines("Room 101, Building 6", "Haidian District, Beijing", 50),
                         ["Room 101, Building 6", "Haidian District, Beijing"])


if __name__ == "__main__":
    unittest.main()
