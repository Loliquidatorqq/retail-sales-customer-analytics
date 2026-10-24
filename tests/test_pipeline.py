import sys
import unittest
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_pipeline import transform

class TestRetailPipeline(unittest.TestCase):
    def setUp(self):
        self.source=pd.DataFrame([
            ['1','A','Mug',2,'2011-01-01 12:00',3.0,'101','UK'],
            ['1','B','Lamp',1,'2011-01-01 12:00',4.0,'101','UK'],
            ['2','A','Mug',1,'2011-02-02 12:00',3.0,'101','UK'],
            ['3','A','Mug',2,'2011-02-02 12:00',3.0,None,'UK'],
            ['C1','A','Mug',-2,'2011-02-04 12:00',3.0,'101','UK'],
            ['4','POST','POSTAGE',1,'2011-02-05 12:00',9.0,'102','UK'],
            ['5','A','Mug',1,'bad date',3.0,'103','UK'],
            ['6','A','Mug',2,'2011-02-07 12:00',0.0,'104','UK'],
            ['1','A','Mug',2,'2011-01-01 12:00',3.0,'101','UK'],
        ],columns=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country'])
        self.result=transform(self.source)

    def test_merchandise_gross_excludes_cancellation_postage_duplicates(self):
        x=self.result['sales']
        self.assertEqual(len(x),4)
        self.assertAlmostEqual(x.line_revenue.sum(),19.0)
        self.assertEqual(self.result['invoices'].invoice_no.nunique(),3)

    def test_unidentified_contributes_revenue_but_not_rfm(self):
        rfm=self.result['rfm']
        self.assertEqual(set(rfm.customer_id),{'101'})
        self.assertEqual(int(rfm.iloc[0].frequency),2)
        self.assertAlmostEqual(float(rfm.iloc[0].monetary),13.0)

    def test_refunds_are_separate_proxy(self):
        canceled=self.result['cancellations']
        self.assertEqual(len(canceled),1)
        self.assertAlmostEqual(float(canceled.iloc[0].refund_value_proxy),6.0)

    def test_monthly_aggregation_matches_sales(self):
        m=self.result['monthly_sales']
        self.assertAlmostEqual(m.gross_sales.sum(),self.result['sales'].line_revenue.sum())
        self.assertEqual(list(m.order_month),['2011-01','2011-02'])

if __name__=='__main__':unittest.main()