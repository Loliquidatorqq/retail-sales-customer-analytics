"""Простые графики по результатам анализа."""
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def make_charts(tables, mode):
    output = ROOT / 'figures'
    output.mkdir(parents=True, exist_ok=True)
    source = 'SYNTHETIC DEMO — NOT REAL SALES' if mode == 'demo' else 'UCI Online Retail / historical'

    monthly = tables['monthly_sales'].sort_values('order_month')
    plt.figure(figsize=(10, 5))
    plt.plot(monthly['order_month'], monthly['gross_sales'], marker='o')
    plt.title(f'Monthly gross merchandise sales (£)\\n{source}')
    plt.xlabel('Month')
    plt.ylabel('GBP')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output / 'monthly_sales.png', dpi=160)
    plt.close()

    segments = tables['rfm']['segment'].value_counts().sort_values()
    plt.figure(figsize=(9, 5))
    plt.barh(segments.index, segments.values)
    plt.title(f'RFM customer segmentation\\n{source}')
    plt.xlabel('Customers')
    plt.tight_layout()
    plt.savefig(output / 'rfm_segments.png', dpi=160)
    plt.close()

    countries = tables['country_sales'].head(8).sort_values('gross_sales')
    plt.figure(figsize=(9, 5))
    plt.barh(countries['country'], countries['gross_sales'])
    plt.title(f'Gross merchandise sales by country\\n{source}')
    plt.xlabel('GBP')
    plt.tight_layout()
    plt.savefig(output / 'sales_by_country.png', dpi=160)
    plt.close()

    print('Saved 3 charts to figures/')
