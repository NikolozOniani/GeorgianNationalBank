"""Identify Geostat series by hierarchy, code and label in the previous-month CPI sheet."""

# At level 2, codes 11 and 12 are divisions. At level 3 the same numbers
# denote Food and Non-alcoholic beverages within division 01.
SERIES = {
    11: (3, 'Food'),
    12: (3, 'Non-alcoholic beverages'),
    21: (3, 'Alcoholic beverages'),
    3: (2, 'Clothing and footwear'),
    5: (2, 'Furnishings, household equipment and routine maintenance of the house'),
    6: (2, 'Health'),
    4: (2, 'Housing, water, electricity, gas and other fuels'),
    7: (2, 'Transport'),
    10: (2, 'Education'),
}


def select_series(rows):
    """Return workbook row numbers and data. Fail on missing, renamed or duplicate series."""
    selected = {}
    for number, row in enumerate(rows, start=5):
        level, code, label = row[:3]
        if code not in SERIES or level != SERIES[code][0]:
            continue
        if label != SERIES[code][1]:
            raise ValueError(f'Unexpected CPI label for level {level}, code {code}: {label}')
        if code in selected:
            raise ValueError(f'Duplicate CPI series at level {level}, code {code}')
        selected[code] = (number, row)
    if selected.keys() != SERIES.keys():
        raise ValueError(f'Missing CPI series: {SERIES.keys() - selected.keys()}')
    return selected
