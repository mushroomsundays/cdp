import gspread

# NOTE: gspread uses 'sheet1', 'sheet2' etc instead of actual sheet name

def read_cells(doc_name, sheet, _range):

    # create gspread client
    # service account credentials are stored here: '~/.config/gspread/service_account.json'
    gc = gspread.service_account()

    doc = gc.open(doc_name)
    obj = getattr(doc, sheet)
    content = obj.get(_range)

    print(content)

    return content

def write_cells(doc_name, sheet, key_cell, value):

    gc = gspread.service_account()
    doc = gc.open(doc_name)
    obj = getattr(doc, sheet)

    # Or update a single cell
    obj.update(key_cell, value)

    # Format the header
    #obj.format('A1:B1', {'textFormat': {'bold': True}})

    print(f"{key_cell} updated")

def main():

    read_cells(
        doc_name='api_test',
        sheet='sheet1',
        _range='A:A',
    )

    # write a single cell
    write_cells(
        doc_name='api_test',
        sheet='sheet1',
        key_cell='A3',
        value='this cell was changed by gspread Python library'
    )

    # write to a block of cells using the top-left cell as a key
    write_cells(
        doc_name='api_test',
        sheet='sheet1',
        key_cell='C1',
        value=[[1, 2], [3, 4]]
    )

if __name__ == '__main__':
    main()