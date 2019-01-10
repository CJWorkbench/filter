import unittest
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from filter import render, migrate_params

# turn menu strings into indices for parameter dictionary
# must be kept in sync with filter.json
menutext = "Select||Text contains|Text does not contain|Text is exactly||Text contains regex|Text does not contain regex|Text matches regex exactly||Cell is empty|Cell is not empty||Equals|Greater than|Greater than or equals|Less than|Less than or equals||Date is|Date is before|Date is after||Filter by text"
menu = menutext.split('|')

# keep menu
keeptext = 'Keep|Drop'
keepmenu = keeptext.split('|')


class TestMigrateParams(unittest.TestCase):
    def test_v0_select_stays_select(self):
        self.assertEqual(
            migrate_params({
                'column': 'A',
                'condition': 0,  # "Select" (the default)
                'value': 'value',
                'casesensitive': False,
                'keep': 0,  # "Keep"
                'regex': False,
            }),
            {
                # Same thing, minux 'regex'
                'column': 'A',
                'condition': 0,
                'value': 'value',
                'casesensitive': False,
                'keep': 0,
            }
        )

    def test_v0_text_contains_without_regex_stays_text_contains(self):
        self.assertEqual(
            migrate_params({
                'column': 'A',
                'condition': 2,  # "Text contains"
                'value': 'value',
                'casesensitive': False,
                'keep': 0,  # "Keep"
                'regex': False,
            }),
            {
                # Same thing, minux 'regex'
                'column': 'A',
                'condition': 2,
                'value': 'value',
                'casesensitive': False,
                'keep': 0,
            }
        )

    def test_v0_text_contains_regex_changes_condition(self):
        self.assertEqual(
            migrate_params({
                'column': 'A',
                'condition': 2,  # "Text contains"
                'value': 'value',
                'casesensitive': False,
                'keep': 0,  # "Keep"
                'regex': True,
            }),
            {
                'column': 'A',
                'condition': 6,  # "Text contains regex"
                'value': 'value',
                'casesensitive': False,
                'keep': 0,
            }
        )

    def test_v0_cell_is_empty_changes_number(self):
        self.assertEqual(
            migrate_params({
                'column': 'A',
                'condition': 6,  # "Cell is empty"
                'value': 'value',
                'casesensitive': False,
                'keep': 0,  # "Keep"
                'regex': True,
            }),
            {
                'column': 'A',
                'condition': 10,  # "Cell is empty" in new menu
                'value': 'value',
                'casesensitive': False,
                'keep': 0,
            }
        )


class TestRender(unittest.TestCase):
    def setUp(self):
        # Test data includes some partially and completely empty rows because this tends to freak out Pandas
        self.table = pd.DataFrame(
            [['fred', 2, 3, 'round', '2018-1-12'],
             ['frederson', 5, np.nan, 'square', '2018-1-12 08:15'],
             [np.nan, np.nan, np.nan, np.nan, np.nan],
             ['maggie', 8, 10, 'Round', '2015-7-31'],
             ['Fredrick', 5, np.nan, 'square', '2018-3-12']],
            columns=['a', 'b', 'c', 'd', 'date'])

    def test_no_column(self):
        params = {'column': '', 'condition': 0, 'value': ''}
        result = render(self.table, params)
        assert_frame_equal(result, self.table)

    def test_no_condition(self):
        params = {
            'column': 'a',
            'condition': menu.index('Select')
        }
        result = render(self.table, params)
        assert_frame_equal(result, self.table)

    def test_no_value(self):
        params = {'column': 'a', 'condition': 0, 'value': ''}
        result = render(self.table, params)
        assert_frame_equal(result, self.table)

    def test_illegal_value(self):
        params = {'column': 'a', 'condition': 1, 'value': ''}
        result = render(self.table, params)
        self.assertEqual(result, 'Please choose a condition')

    def test_contains_case_insensitive(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text contains'),
            'value': 'fred',
            'casesensitive': False,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[True, True, False, False, True]]
        assert_frame_equal(result, expected)

    def test_contains_case_sensitive(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text contains'),
            'value': 'fred',
            'casesensitive': True,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[True, True, False, False, False]]
        assert_frame_equal(result, expected)

    def test_contains_regex(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text contains regex'),
            'value': 'f[a-zA-Z]+d',
            'casesensitive': True,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[True, True, False, False, False]]
        assert_frame_equal(result, expected)

    def test_contains_regex_drop(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text contains regex'),
            'value': 'f[a-zA-Z]+d',
            'casesensitive': True,
            'keep': keepmenu.index('Drop')
        }
        result = render(self.table, params)
        expected = self.table[[False, False, True, True, True]]
        assert_frame_equal(result, expected)

    def test_not_contains(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text does not contain'),
            'value': 'fred',
            'casesensitive': False,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[False, False, True, True, False]]
        assert_frame_equal(result, expected)

    def test_not_contains_case_sensitive(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text does not contain'),
            'value': 'fred',
            'casesensitive': True,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[False, False, True, True, True]]
        assert_frame_equal(result, expected)

    def test_not_contains_regex(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text does not contain regex'),
            'value': 'f[a-zA-Z]+d',
            'casesensitive': True,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[False, False, True, True, True]]
        assert_frame_equal(result, expected)

    def test_not_contains_regex_drop(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text does not contain regex'),
            'value': 'f[a-zA-Z]+d',
            'casesensitive': True,
            'keep': keepmenu.index('Drop')
        }
        result = render(self.table, params)
        expected = self.table[[True, True, False, False, False]]
        assert_frame_equal(result, expected)

    def test_exactly(self):
        params = {
            'column': 'a',
            'condition': menu.index('Text is exactly'),
            'value': 'fred',
            'casesensitive': True,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[True, False, False, False, False]]
        assert_frame_equal(result, expected)

    def test_exactly_regex(self):
        params = {
            'column': 'd',
            'condition': menu.index('Text matches regex exactly'),
            'value': 'round',
            'casesensitive': False,
            'keep': keepmenu.index('Keep')
        }
        result = render(self.table, params)
        expected = self.table[[True, False, False, True, False]]
        assert_frame_equal(result, expected)

    def test_exactly_non_text_column(self):
        params = {'column': 'b',
                  'condition': menu.index('Text is exactly'),
                  'casesensitive': False,
                  'value': '5',
                  'keep': keepmenu.index('Keep')}
        result = render(self.table, params)
        self.assertEqual(result, 'Column is not text. Please convert to text.')

    def test_empty(self):
        params = {'column': 'c', 'condition': menu.index('Cell is empty'),
                  'value': 'nonsense'}
        result = render(self.table, params)
        expected = self.table[[False, True, True, False, True]]
        assert_frame_equal(result, expected)

        # should not require value
        params = {'column': 'c', 'condition': menu.index('Cell is empty'),
                  'value': ''}
        result = render(self.table, params)
        assert_frame_equal(result, expected)

    def test_not_empty(self):
        params = {'column': 'c', 'condition': menu.index('Cell is not empty'),
                  'value': 'nonsense'}
        result = render(self.table, params)
        expected = self.table[[True, False, False, True, False]]
        assert_frame_equal(result, expected)

        # should not require value
        params = {'column': 'c', 'condition': menu.index('Cell is not empty'),
                  'value': ''}
        result = render(self.table, params)
        assert_frame_equal(result, expected)

    def test_equals(self):
        # working as intended
        params = {
            'column': 'c',
            'condition': menu.index('Equals'),
            'value': '3'
        }
        result = render(self.table, params)
        expected = self.table[[True, False, False, False, False]]
        assert_frame_equal(result, expected)

    def test_equals_non_number_errors(self):
        # non-numeric column should return error message
        params = {
            'column': 'a',
            'condition': menu.index('Equals'),
            'value': '3'
        }
        result = render(self.table, params)
        self.assertEqual(result,
                         'Column is not numbers. Please convert to numbers.')

        # non-numeric column should return error message
        params = {
            'column': 'date',
            'condition': menu.index('Equals'),
            'value': '3'
        }
        result = render(self.table, params)
        self.assertEqual(result,
                         'Column is not numbers. Please convert to numbers.')

        # non-numeric value should return error message
        params = {
            'column': 'c',
            'condition': menu.index('Equals'),
            'value': 'gibberish'
        }
        result = render(self.table, params)
        self.assertEqual(result,
                         'Value is not a number. Please enter a valid number.')

    def test_category_equals(self):
        table = pd.DataFrame({'A': ['foo', np.nan, 'bar']}, dtype='category')
        params = {
            'column': 'A',
            'condition': menu.index('Text is exactly'),
            'value': 'foo',
            'casesensitive': True,
        }
        result = render(table, params)
        # Output is categorical with [foo, bar] categories. We _could_ remove
        # the unused category, but there's no value added there.
        assert_frame_equal(
            result,
            pd.DataFrame({'A': ['foo']}, dtype=table['A'].dtype)
        )

    def test_greater(self):
        # edge case, first row has b=2
        params = {
            'column': 'b',
            'condition': menu.index('Greater than'),
            'value': '2'
        }
        result = render(self.table, params)
        expected = self.table[[False, True, False, True, True]]
        assert_frame_equal(result, expected)

    def test_greater_equals(self):
        # edge case, first row has b=2
        params = {
            'column': 'b',
            'condition': menu.index('Greater than or equals'),
            'value': '2'
        }
        result = render(self.table, params)
        expected = self.table[[True, True, False, True, True]]
        assert_frame_equal(result, expected)

    def test_less(self):
        # edge case, second and last row has b=5
        params = {
            'column': 'b',
            'condition': menu.index('Less than'),
            'value': '5'
        }
        result = render(self.table, params)
        expected = self.table[[True, False, False, False, False]]
        assert_frame_equal(result, expected)

    def test_less_equals(self):
        # edge case, second and last row has b=5
        params = {
            'column': 'b',
            'condition': menu.index('Less than or equals'),
            'value': '5'
        }
        result = render(self.table, params)
        expected = self.table[[True, True, False, False, True]]
        assert_frame_equal(result, expected)

    def test_date_is(self):
        params = {
            'column': 'date',
            'condition': menu.index('Date is'),
            'value': '2015-7-31'
        }
        result = render(self.table, params)
        expected = self.table[[False, False, False, True, False]]
        assert_frame_equal(result, expected)

    def test_bad_date(self):
        # columns that aren't dates -> error
        params = {'column': 'a', 'condition': menu.index('Date is'),
                  'value': '2015-7-31'}
        result = render(self.table, params)
        self.assertEqual(result,
                         'Column is not dates. Please convert to dates.')

        params = {'column': 'b', 'condition': menu.index('Date is'),
                  'value': '2015-7-31'}
        result = render(self.table, params)
        self.assertEqual(result,
                         'Column is not dates. Please convert to dates.')

        # stirng that isn't a date -> error
        params = {'column': 'date', 'condition': menu.index('Date is'),
                  'value': 'gibberish'}
        result = render(self.table, params)
        self.assertEqual(result,
                         'Value is not a date. Please enter a date and time.')

    def test_date_before(self):
        params = {'column': 'date', 'condition': menu.index(
            'Date is before'), 'value': '2016-7-31'}
        result = render(self.table, params)
        expected = self.table[[False, False, False, True, False]]
        assert_frame_equal(result, expected)

    def test_date_after(self):
        # edge case, first row is 2018-1-12 08:15 so after implied midnight of date without time
        params = {'column': 'date', 'condition': menu.index(
            'Date is after'), 'value': '2018-1-12'}
        result = render(self.table, params)
        expected = self.table[[False, True, False, False, True]]
        assert_frame_equal(result, expected)

    def test_compare_int_with_str_condition(self):
        params = {'column': 'A', 'condition': menu.index('Text is exactly'),
                  'value': ' ', 'casesensitive': False}
        result = render(pd.DataFrame({'A': []}), params)
        self.assertEqual(result, 'Column is not text. Please convert to text.')


if __name__ == '__main__':
    unittest.main()
