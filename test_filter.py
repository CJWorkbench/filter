import unittest
import pandas as pd
from filter import render

# turn menu strings into indices for parameter dictionary
# must be kept in sync with filter.json
menutext = "Text contains|Text does not contain|Text is exactly|Cell is empty|Cell is not empty|Equals|Greater than||Greater than or equals|Less than|Less than or equals"
menu = menutext.split('|')

class TestFilter(unittest.TestCase):
 
	def setUp(self):
		# Test data includes some partially and completely empty rows because this tends to freak out Pandas
		self.table = pd.DataFrame(
			[['fred',2,3],
			['frederson',5,None], 
			[None, None, None],
			['maggie',8,10]], 
			columns=['a','b','c'])

	def test_no_column(self):
		params = { 'column': '', 'condition': 0, 'value':''}
		out = render(self.table, params)
		self.assertTrue(out.equals(self.table)) # should NOP when first applied

	def test_contains(self):
		params = { 'column': 'a', 'condition': menu.index('Text contains'), 'value':'fred'}
		out = render(self.table, params)
		ref = self.table[[True, True, False, False]]
		self.assertTrue(out.equals(ref))

	def test_not_contains(self):
		params = { 'column': 'a', 'condition': menu.index('Text does not contain'), 'value':'fred'}
		out = render(self.table, params)
		ref = self.table[[False, False, True, True]]
		self.assertTrue(out.equals(ref))

	def test_exactly(self):
		params = { 'column': 'a', 'condition': menu.index('Text is exactly'), 'value':'fred'}
		out = render(self.table, params)
		ref = self.table[[True, False, False, False]]
		self.assertTrue(out.equals(ref))
 
		# Do numeric equals on a numeric column
		params = { 'column': 'b', 'condition': menu.index('Text is exactly'), 'value':5}
		out = render(self.table, params)
		ref = self.table[[False, True, False, False]]
		self.assertTrue(out.equals(ref))
 
	def test_empty(self):
		params = { 'column': 'c', 'condition': menu.index('Cell is empty'), 'value':'nonsense'}
		out = render(self.table, params)
		ref = self.table[[False, True, True, False]]
		self.assertTrue(out.equals(ref))

	def test_not_empty(self):
		params = { 'column': 'c', 'condition': menu.index('Cell is not empty'), 'value':'nonsense'}
		out = render(self.table, params)
		ref = self.table[[True, False, False, True]]
		self.assertTrue(out.equals(ref))

	def test_equals(self):
		params = { 'column': 'c', 'condition': menu.index('Equals'), 'value':3}
		out = render(self.table, params)
		ref = self.table[[True, False, False, False]]
		self.assertTrue(out.equals(ref))

	def test_greater(self):
		# edge case, first row has b=2
		params = { 'column': 'b', 'condition': menu.index('Greater than'), 'value':2}
		out = render(self.table, params)
		ref = self.table[[False, True, False, True]]
		self.assertTrue(out.equals(ref))

	def test_greater_equals(self):
		# edge case, first row has b=2
		params = { 'column': 'b', 'condition': menu.index('Greater than or equals'), 'value':2}
		out = render(self.table, params)
		ref = self.table[[True, True, False, True]]
		self.assertTrue(out.equals(ref))

	def test_less(self):
		# edge case, second row has b=5
		params = { 'column': 'b', 'condition': menu.index('Less than'), 'value':5}
		out = render(self.table, params)
		ref = self.table[[True, False, False, False]]
		self.assertTrue(out.equals(ref))

	def test_less_equals(self):
		# edge case, second row has b=5
		params = { 'column': 'b', 'condition': menu.index('Less than or equals'), 'value':5}
		out = render(self.table, params)
		ref = self.table[[True, True, False, False]]
		self.assertTrue(out.equals(ref))

if __name__ == '__main__':
    unittest.main()
