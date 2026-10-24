"""Download the original CC BY 4.0 UCI Online Retail workbook.

The script requires an internet connection. No data are scraped from other repos.
"""
from pathlib import Path
from urllib.request import urlopen, Request
from zipfile import ZipFile
from io import BytesIO

ROOT=Path(__file__).resolve().parents[1]
URL='https://archive.ics.uci.edu/static/public/352/online%2Bretail.zip'

def main():
    folder=ROOT/'data/raw';folder.mkdir(parents=True,exist_ok=True)
    dest=folder/'Online Retail.xlsx'
    if dest.exists():
        print(f'Already exists: {dest}');return
    req=Request(URL,headers={'User-Agent':'Mozilla/5.0 educational-portfolio'})
    with urlopen(req,timeout=90) as response:
        raw=response.read()
    with ZipFile(BytesIO(raw)) as bundle:
        names=[n for n in bundle.namelist() if n.lower().endswith('.xlsx')]
        if len(names)!=1:raise ValueError(f'Expected exactly one .xlsx, found {names}')
        dest.write_bytes(bundle.read(names[0]))
    print('Downloaded from UCI:',dest)

if __name__=='__main__':main()