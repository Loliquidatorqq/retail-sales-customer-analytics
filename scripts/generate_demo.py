"""Generate a deterministic, synthetic sample for offline pipeline tests.

This is NOT the UCI Online Retail dataset. The synthetic data is labelled DEMO
throughout the reports and must not be presented as observed business evidence.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def make_demo(path: Path, seed=2026, orders=3600):
    rng = np.random.default_rng(seed)
    products = [
        ('85123A','WHITE HANGING HEART T-LIGHT HOLDER',2.55),
        ('71053','WHITE METAL LANTERN',3.39),
        ('22752','SET 7 BABUSHKA NESTING BOXES',7.65),
        ('22633','HAND WARMER UNION JACK',1.85),
        ('22726','ALARM CLOCK BAKELIKE GREEN',3.75),
        ('84879','ASSORTED COLOUR BIRD ORNAMENT',1.69),
        ('22114','HOT WATER BOTTLE TEA AND SYMPATHY',3.45),
        ('22326','ROUND SNACK BOXES SET OF4 WOODLAND',2.95),
        ('21913','VINTAGE SEASIDE JIGSAW PUZZLES',3.75),
        ('48187','DOORMAT NEW ENGLAND',7.95),
        ('POST','POSTAGE',18.0),
    ]
    countries=['United Kingdom','France','Germany','EIRE','Spain']
    probabilities=[0.76,0.09,0.07,0.05,0.03]
    rows=[]
    for order in range(orders):
        customer=int(rng.integers(12000,12650))
        country=str(rng.choice(countries,p=probabilities))
        invoice=f'{540000+order}'
        # Seasonal effect: stronger Nov-Dec. Uneven dates are deliberate demo behavior.
        month=int(rng.choice(np.arange(1,13),p=np.array([.06,.06,.06,.07,.07,.07,.07,.08,.08,.09,.14,.15])))
        day=int(rng.integers(1, min(28,31)+1))
        date=pd.Timestamp(2011,month,day,int(rng.integers(8,19)),int(rng.integers(0,60)))
        n_lines=int(rng.integers(1,6))
        chosen=rng.choice(len(products)-1,size=n_lines,replace=False)
        for j in chosen:
            stock,desc,price=products[j]
            qty=int(rng.choice([1,2,3,4,6,8,12,24],p=[.16,.22,.18,.14,.10,.09,.08,.03]))
            rows.append([invoice,stock,desc,qty,date,price,customer,country])
        if rng.random()<.07: # identifiable shipping line to exclude from merchandise sales
            stock,desc,price=products[-1]
            rows.append([invoice,stock,desc,1,date,price,customer,country])
        if rng.random()<.06:
            stock,desc,price=products[int(rng.integers(0,len(products)-1))]
            rows.append(['C'+invoice,stock,desc,-int(rng.integers(1,4)),date+pd.Timedelta(days=1),price,customer,country])
        if rng.random()<.04:
            rows[-1][-2]=None
    df=pd.DataFrame(rows,columns=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country'])
    path.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path,index=False)
    print(f'Generated {len(df):,} SYNTHETIC demo rows -> {path}')
    return df

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'data/demo/online_retail_demo.csv')
    args=parser.parse_args()
    make_demo(args.output)