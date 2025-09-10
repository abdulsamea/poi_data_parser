from decimal import Decimal
from django.test import SimpleTestCase

from pois.utils import parse_ratings


def D(x: str) -> Decimal:
    return Decimal(x)


class ParseRatingsTests(SimpleTestCase):
    def test_none_returns_empty(self):
        self.assertEqual(parse_ratings(None), [])  # None -> []

    def test_empty_string_returns_empty(self):
        self.assertEqual(parse_ratings(""), [])  # "" -> []
        self.assertEqual(parse_ratings("   "), [])  # spaces -> []

    def test_list_of_numbers(self):
        self.assertEqual(parse_ratings([1, 2, 3]), [D("1"), D("2"), D("3")])  # ints -> Decimals
        self.assertEqual(
            parse_ratings([1.5, 2.0, 3.25]),
            [D("1.5"), D("2.0"), D("3.25")],
        )  # floats -> Decimals

    def test_tuple_of_strings(self):
        self.assertEqual(
            parse_ratings(("4", "5.0", "6.25")), [D("4"), D("5.0"), D("6.25")]
        )  # tuple[str] -> Decimals

    def test_csv_string(self):
        self.assertEqual(parse_ratings("3,4,5"), [D("3"), D("4"), D("5")])  # CSV -> list
        self.assertEqual(
            parse_ratings("  3 ,  4 , 5  "), [D("3"), D("4"), D("5")]
        )  # trims whitespace

    def test_braced_csv_string(self):
        self.assertEqual(parse_ratings("{3,4,5}"), [D("3"), D("4"), D("5")])  # check if it parses with brases removed
        self.assertEqual(
            parse_ratings("{ 3 ,  4 , 5 }"), [D("3"), D("4"), D("5")]
        )  # trims inside braces

    def test_single_scalar(self):
        self.assertEqual(parse_ratings(7), [D("7")])  # int -> single-item list
        self.assertEqual(parse_ratings(7.5), [D("7.5")])  # float -> single-item list
        self.assertEqual(parse_ratings("7.75"), [D("7.75")])  # str -> single-item list

    def test_ignores_empty_tokens(self):
        self.assertEqual(parse_ratings("3,,4, ,5,"), [D("3"), D("4"), D("5")])  # skips blanks

    def test_non_numeric_tokens_are_skipped(self):
        # Mixed valid/invalid tokens: invalid ones are ignored by try/except
        self.assertEqual(
            parse_ratings("3, x, 4.5, NaN, 6"),
            [D("3"), D("4.5"), D("6")],
        )  # skips non-numerics and NaN

    def test_whitespace_and_newlines(self):
        self.assertEqual(
            parse_ratings(" \n 1 , 2 \t, 3 \r\n "),
            [D("1"), D("2"), D("3")],
        )  # handles mixed whitespace

    def test_large_and_negative(self):
        self.assertEqual(
            parse_ratings(["-2", "0", "1000000000000000000"]),
            [D("-2"), D("0"), D("1000000000000000000")],
        )  # big ints preserved as Decimals

    def test_curly_braces_with_spaces_only(self):
        self.assertEqual(parse_ratings("{  }"), [])

    def test_curly_braces_with_data_only(self):
        self.assertEqual(parse_ratings("{ 1, 4, 5, 7, 8 }"), [D("1"), D("4"), D("5"), D("7"), D("8")])

    def test_nan_and_inf_strings_skipped(self):
        # Decimal('NaN') / 'Infinity' could parse, but spec chooses to skip them.
        self.assertEqual(
            parse_ratings("NaN, Infinity, -Infinity, 5"),
            [D("5")],
        )  # keep finite numerics only
