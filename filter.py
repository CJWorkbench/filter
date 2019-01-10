import functools
from typing import Any, Dict
import pandas as pd
from pandas.api.types import is_numeric_dtype


class UserVisibleError(Exception):
    """A message for the user. Use str(err) to see it."""
    pass


class MissingValue(Exception):
    """User has not finished filling in the form."""
    pass


def series_to_text(series, strict=False):
    """
    Convert to text, or raise UserVisibleError.

    TODO [adamhooper, 2018-12-19] nix this and quick-fix coltypes
    """
    if hasattr(series, 'cat') or series.dtype == object:
        return series
    else:
        raise UserVisibleError('Column is not text. Please convert to text.')


def series_to_number(series):
    """
    Convert to number, or raise UserVisibleError.

    TODO [adamhooper, 2018-12-19] nix this and quick-fix coltypes
    """
    try:
        return pd.to_numeric(series, errors='raise')
    except ValueError:
        raise UserVisibleError(
            'Column is not numbers. Please convert to numbers.'
        )


def value_to_number(value):
    """
    Convert to number, or raise UserVisibleError.
    """
    try:
        return pd.to_numeric(value, errors='raise')
    except ValueError:
        raise UserVisibleError(
            'Value is not a number. Please enter a valid number.'
        )


def series_to_datetime(series):
    """
    Convert to datetime, or raise UserVisibleError.

    TODO [adamhooper, 2018-12-19] nix this and quick-fix coltypes
    """
    try:
        if is_numeric_dtype(series):
            # numeric columns, just... no. Never really want to interpret as
            # seconds since 1970
            raise ValueError('Refusing to convert numbers to dates')

        return pd.to_datetime(series)
    except ValueError:
        raise UserVisibleError(
            'Column is not dates. Please convert to dates.'
        )


def value_to_datetime(value):
    """
    Convert to datetime, or raise UserVisibleError.
    """
    try:
        return pd.to_datetime(value)
    except ValueError:
        raise UserVisibleError(
            'Value is not a date. Please enter a date and time.'
        )


def type_text(f, strict=False):
    @functools.wraps(f)
    def inner(series, value, *args, **kwargs):
        series = series_to_text(series)  # raises UserVisibleError
        if not value:
            raise MissingValue
        return f(series, value, *args, **kwargs)
    return inner


def type_number(f):
    @functools.wraps(f)
    def inner(series, value, *args, **kwargs):
        series = series_to_number(series)  # raises UserVisibleError
        if not value:
            raise MissingValue
        value = value_to_number(value)  # raises UserVisibleError
        return f(series, value, *args, **kwargs)
    return inner


def type_date(f):
    @functools.wraps(f)
    def inner(series, value, *args, **kwargs):
        series = series_to_datetime(series)  # raises UserVisibleError
        if not value:
            raise MissingValue
        value = value_to_datetime(value)  # raises UserVisibleError
        return f(series, value, *args, **kwargs)
    return inner


@type_text
def mask_text_contains(series, text, params):
    case_sensitive = params['casesensitive']
    # keeprows = matching, not NaN
    contains = series.str.contains(text, case=case_sensitive, regex=False)
    return contains == True  # noqa: E712


@type_text
def mask_text_contains_regex(series, text, params):
    case_sensitive = params['casesensitive']
    # keeprows = matching, not NaN
    contains = series.str.contains(text, case=case_sensitive, regex=True)
    return contains == True  # noqa: E712


@type_text
def mask_text_does_not_contain(series, text, params):
    # keeprows = not matching, allow NaN
    case_sensitive = params['casesensitive']
    contains = series.str.contains(text, case=case_sensitive, regex=False)
    return contains != True  # noqa: E712


@type_text
def mask_text_does_not_contain_regex(series, text, params):
    # keeprows = not matching, allow NaN
    case_sensitive = params['casesensitive']
    contains = series.str.contains(text, case=case_sensitive, regex=True)
    return contains != True  # noqa: E712


@type_text
def mask_text_is_exactly(series, text, params):
    case_sensitive = params['casesensitive']
    if case_sensitive:
        return series == text
    else:
        return series.str.lower() == text.lower()


@type_text
def mask_text_is_exactly_regex(series, text, params):
    case_sensitive = params['casesensitive']
    matches = series.str.match(text, case=case_sensitive)
    return matches == True  # noqa: E712


def mask_cell_is_empty(series, val, params):
    return series.isnull()


def mask_cell_is_not_empty(series, val, params):
    return ~series.isnull()


@type_number
def mask_number_equals(series, number, params):
    return series == number


@type_number
def mask_number_is_greater_than(series, number, params):
    return series > number


@type_number
def mask_number_is_greater_than_or_equals(series, number, params):
    return series >= number


@type_number
def mask_number_is_less_than(series, number, params):
    return series < number


@type_number
def mask_number_is_less_than_or_equals(series, number, params):
    return series <= number


@type_date
def mask_date_is(series, date, params):
    return series == date


@type_date
def mask_date_is_before(series, date, params):
    return series < date


@type_date
def mask_date_is_after(series, date, params):
    return series > date


# keep the switch statment in sync with the json by copying it here
MaskGenerators = (
    None,  # 'Select'
    None,  # ''
    mask_text_contains,  # 'Text contains'...
    mask_text_does_not_contain,
    mask_text_is_exactly,
    None,
    mask_text_contains_regex,  # 'Text contains regex'...
    mask_text_does_not_contain_regex,
    mask_text_is_exactly_regex,
    None,
    mask_cell_is_empty,
    mask_cell_is_not_empty,
    None,
    mask_number_equals,
    mask_number_is_greater_than,
    mask_number_is_greater_than_or_equals,
    mask_number_is_less_than,
    mask_number_is_less_than_or_equals,
    None,
    mask_date_is,
    mask_date_is_before,
    mask_date_is_after,
)


def migrate_params_v0_to_v1(params: Dict[str, Any]) -> Dict[str, Any]:
    is_regex = params['regex']
    condition = params['condition']

    # v0:
    # Select|| (0,1)
    # Text contains|Text does not contain|Text is exactly|| (2, 3, 4, 5)
    # Cell is empty|Cell is not empty|| (6, 7, 8)
    # Equals|Greater than|Greater than or equals|Less than|Less than or
    #   equals|| (9, 10, 11, 12, 13, 14)
    # Date is|Date is before|Date is after (15, 16, 17)
    #
    # v1:
    # Select|| (0,1)
    # Text contains|Text does not contain|Text is exactly|| (2, 3, 4, 5)
    # Text contains regex|Text does not contain regex|Text matches regex
    #   exactly|| (6, 7, 8, 9)
    # Cell is empty|Cell is not empty|| (10, 11, 12)
    # Equals|Greater than|Greater than or equals|Less than|Less than or
    #   equals|| (13, 14, 15, 16, 17, 18)
    # Date is|Date is before|Date is after (19, 20, 21)

    if is_regex and condition in (2, 3, 4, 5):
        condition += 4  # 2 => 6, 3 => 7, ...
    elif condition > 5:
        condition += 4

    ret = dict(params)
    del ret['regex']
    ret['condition'] = condition
    return ret


def migrate_params(params: Dict[str, Any]):
    # v0: 'regex' is a checkbox. Migrate it to a menu entry.
    if 'regex' in params:
        params = migrate_params_v0_to_v1(params)

    return params


def render(table, params):
    condition = params['condition']
    keep = params.get('keep', 0) == 0
    value = params.get('value', '')
    column = params.get('column', '')

    if not column or condition == 0:
        return table

    mask_generator = MaskGenerators[condition]

    if mask_generator is None:
        return 'Please choose a condition'

    series = table[column]
    try:
        mask = mask_generator(series, value, params)
    except MissingValue:
        return table  # User hasn't finished filling stuff in
    except UserVisibleError as err:
        return str(err)

    if keep:
        return table[mask]
    else:
        return table[~mask]
