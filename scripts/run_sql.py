"""Execute SQL examples against SQLite database created by the pipeline."""
from pathlib import Path
import sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
with sqlite3.connect(ROOT/'database/retail_analysis.sqlite') as con:
    for path in sorted((ROOT/'sql').glob('*.sql')):
        if path.name.startswith('00_'):
            con.executescript(path.read_text(encoding='utf8'))
            print(f'{path.name}: created index(es)')
            continue
        q=path.read_text(encoding='utf8')
        df=pd.read_sql_query(q,con)
        df.to_csv(ROOT/'reports'/f'{path.stem}.csv',index=False)
        print(f'{path.name}: {len(df)} rows -> reports/{path.stem}.csv')