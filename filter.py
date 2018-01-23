def render(table, params):
    col = params['column']
    cond = params['condition']
    val = params['value']

    if col == '':
        return table

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
    menutext = "Text contains|Text does not contain|Text is exactly||Cell is empty|Cell is not empty||Equals|Greater than|Greater than or equals|Less than|Less than or equals||Date is|Date is before|Date is after"
    menu = menutext.split('|')
    cond = menu[cond]

    try:

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
    
    except ValueError as e: # capture datevals exceptions
        return str(e)       # string return type means error

    return table

