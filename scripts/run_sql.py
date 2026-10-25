"""Запускаем SQL-запросы и сохраняем результаты в CSV."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)

with sqlite3.connect(ROOT / 'database/retail_analysis.sqlite') as connection:
    for sql_file in sorted((ROOT / 'sql').glob('*.sql')):
        query = sql_file.read_text(encoding='utf-8')
        if sql_file.name.startswith('00_'):
            connection.executescript(query)
            print(sql_file.name, '- indexes created')
        else:
            result = pd.read_sql_query(query, connection)
            output = REPORTS / f'{sql_file.stem}.csv'
            result.to_csv(output, index=False)
            print(sql_file.name, '-', len(result), 'rows')
