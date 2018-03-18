def render(table, params):
    cond = params['condition']
    val = params['value']

    #if col == '':
    #    return table

    import pandas as pd

    # simple date coercion logic for strings and columns
    def dateval(val):
        if val.strip() == '':
            raise ValueError(str(val) + 'Please enter a date')
        d = pd.to_datetime(val, errors='coerce')  # coerce turns invalid dates into NaT
        if d is pd.NaT:
            raise ValueError(str(val) + ' is not a valid date')
        return d

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


    # keep the switch statment in sync with the json by copying it here
    # This way we can switch on menu values not indices
    menutext = "Text contains|Text does not contain|Text is exactly||Cell is empty|Cell is not empty||Equals|Greater than|Greater than or equals|Less than|Less than or equals||Date is|Date is before|Date is after||Filter by text"
    menu = menutext.split('|')
    cond = menu[cond]

    # all conditions except empty cell should NOP if no value
    if cond!='Cell is empty' and cond!='Cell is not empty':
        if val=='':
            return table

    try:

        if cond != 'Filter by text':
            # We are using 'col' if condition isn't filter by text

            col = params['column']

            if col == '':
                return table

            if cond=='Text contains':
                table = table[table[col].str.contains(val)==True]   # == True to handle None return on None column values

            elif cond=='Text does not contain':
                table = table[table[col].str.contains(val)!=True]

            elif cond=='Text is exactly':
                table = table[table[col]==val]

            elif cond=='Cell is empty':
                table = table[table[col].isnull()]

            elif cond=='Cell is not empty':
                table = table[table[col].isnull()!=True]

            elif cond=='Equals':
                table = table[table[col]==val]

            elif cond=='Greater than':
                table = table[table[col]>val]

            elif cond=='Greater than or equals':
                table = table[table[col]>=val]

            elif cond=='Less than':
                table = table[table[col]<val]

            elif cond=='Less than or equals':
                table = table[table[col]<=val]

            elif cond=='Date is':
                table = table[datevals(table,col)==dateval(val)]

            elif cond=='Date is before':
                table = table[datevals(table,col)<dateval(val)]

            elif cond=='Date is after':
                table = table[datevals(table,col)>dateval(val)]

        else:
            # This is basically code from textsearch.py

            query = val
            cols = params['colnames'].split(',')
            cols = [c.strip() for c in cols]
            case_sensitive = params['casesensitive']
            regex = params['regex']
            if (cols != [''] and query != ''):
                keeprows = None
                for c in cols:
                    if not c in table.columns:
                        return('There is no column named %s' % c)

                    kr = table[c].fillna('').astype(str).str.contains(query, case=case_sensitive, regex=regex)

                    # logical OR of all matching columns
                    if keeprows is not None:
                        keeprows = keeprows | kr
                    else:
                        keeprows = kr

                table = table[keeprows]

    except ValueError as e: # capture datevals exceptions
        return str(e)       # string return type means error

    return table
