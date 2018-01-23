def render(table, params):
    col = params['column']
    cond = params['condition']
    val = params['value']

    if col == '':
        return table

    # keep the switch statment in sync with the json by copying it here
    # This way we can switch on menu values not indices
    menutext = "Text contains|Text does not contain|Text is exactly|Cell is empty|Cell is not empty|Equals|Greater than|Greater than or equals|Less than|Less than or equals"
    menu = menutext.split('|')
    cond = menu[cond]

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
    
    return table