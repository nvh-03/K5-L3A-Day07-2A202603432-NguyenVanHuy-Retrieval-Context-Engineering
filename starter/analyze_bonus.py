import json
import re
import pypdf

reader = pypdf.PdfReader('data/bonus.pdf')

tables = {}
figures = {}

for p_num, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ''
    # Find table headings
    for match in re.finditer(r'(Table\s+(\d+\.\d+)[^\n]*)', text):
        t_full = match.group(1).strip()
        t_id = match.group(2)
        if t_id not in tables:
            tables[t_id] = {'page': p_num, 'heading': t_full, 'pages': [p_num]}
        else:
            if p_num not in tables[t_id]['pages']:
                tables[t_id]['pages'].append(p_num)

    # Find figure headings
    for match in re.finditer(r'(Figure\s+(\d+\.\d+)[^\n]*)', text):
        f_full = match.group(1).strip()
        f_id = match.group(2)
        if f_id not in figures:
            figures[f_id] = {'page': p_num, 'heading': f_full}

print('=== TABLES FOUND ===')
for k, v in sorted(tables.items(), key=lambda x: [int(p) for p in x[0].split('.')]):
    print(f"Table {k} (Page {v['pages']}): {v['heading']}")

print(f'\nTotal tables: {len(tables)}')

print('\n=== FIGURES FOUND ===')
for k, v in sorted(figures.items(), key=lambda x: [int(p) for p in x[0].split('.')]):
    print(f"Figure {k} (Page {v['page']}): {v['heading']}")

print(f'\nTotal figures: {len(figures)}')

