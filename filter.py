import pandas as pd

# keep the switch statment in sync with the json by copying it here
Menu = (
    'Select',
    None,  # ""
    'Text contains',
    'Text does not contain',
    'Text is exactly',
    None,
    'Cell is empty',
    'Cell is not empty',
    None,
    'Equals',
    'Greater than',
    'Greater than or equals',
    'Less than',
    'Less than or equals',
    None,
    'Date is',
    'Date is before',
    'Date is after',
)


def render(table, params):
    cond = Menu[params['condition']]
    keep = params.get('keep', 0) == 0
    val = params.get('value', '')
    col = params.get('column', '')

    if not col:
        return table

    if cond == 'Select':
        return table
    if cond is None:
        return 'Please choose a condition'

    keeprows = None

    # simple date coercion logic for strings and columns
    def dateval(val):
        if val.strip() == '':
            raise ValueError(str(val) + 'Please enter a date')
        d = pd.to_datetime(val, errors='coerce')  # coerce turns invalid dates into NaT
        if d is pd.NaT:
            raise ValueError(str(val) + ' is not a valid date')
        return d

    # Simple coercion logic to numbers
    def datevals(table, col):
        # numeric columns, just... no. Never really want to interpret as seconds since 1970
        if table[col].dtype == 'int64' or table[col].dtype == 'float64':
            raise ValueError('Column %s is not dates' % col)

        # see if Pandas can make dates out of this column
        try:
            dates = pd.to_datetime(table[col])
        except (ValueError, TypeError):
            raise ValueError('Column %s is not dates' % col)

        return dates

    def numericval(val):
        numval = None
        try:
            numval = float(val)
        except:
            raise ValueError(str(val) + ' is not a valid number')

        return numval

    def numericvals(table, col):
        try:
            vals = pd.to_numeric(table[col], errors='raise')
        except:
            raise ValueError('Column %s is not numeric' % col)

        return vals

    # all conditions except empty cell should NOP if no value
    if cond != 'Cell is empty' and cond != 'Cell is not empty':
        if not val:
            return table

    try:

        if cond=='Text contains':
            case_sensitive = params['casesensitive']
            regex = params['regex']
            # keeprows = matching, not NaN
            keeprows = table[col].str.contains(val, case=case_sensitive,
                                               regex=regex) == True

        elif cond=='Text does not contain':
            case_sensitive = params['casesensitive']
            regex = params['regex']
            # keeprows = not matching, allow NaN
            keeprows = table[col].str.contains(val, case=case_sensitive,
                                               regex=regex) != True

        elif cond=='Text is exactly':
            case_sensitive = params['casesensitive']
            regex = params['regex']
            if regex:
                keeprows = table[col].str.match(val,
                                                case=case_sensitive) == True
            else:
                if case_sensitive:
                    keeprows = (table[col] == val)
                else:
                    keeprows = (table[col].str.lower() == val.lower())

        elif cond=='Cell is empty':
            keeprows = table[col].isnull()

        elif cond=='Cell is not empty':
            keeprows = (table[col].isnull() != True)

        elif cond=='Equals':
            keeprows = (numericvals(table, col) == numericval(val))

        elif cond=='Greater than':
            keeprows = (numericvals(table, col) > numericval(val))

        elif cond=='Greater than or equals':
            keeprows = (numericvals(table, col) >= numericval(val))

        elif cond=='Less than':
            keeprows = (numericvals(table, col) < numericval(val))

        elif cond=='Less than or equals':
            keeprows = (numericvals(table, col) <= numericval(val))

        elif cond=='Date is':
            keeprows = (datevals(table, col) == dateval(val))

        elif cond=='Date is before':
            keeprows = (datevals(table, col) < dateval(val))

        elif cond=='Date is after':
            keeprows = (datevals(table, col) > dateval(val))

        else:
            return 'Please choose a condition'

        if keep:
            return table[keeprows]
        else:
            return table[~keeprows]

    except AttributeError as err:
        if str(err).startswith('Can only use .str accessor with string'):
            return f'Column {col} is not text'
        else:
            raise

    except ValueError as e: # capture datevals exceptions
        # TODO be far more specific when catching an exception here
        return str(e)       # string return type means error

    return table
