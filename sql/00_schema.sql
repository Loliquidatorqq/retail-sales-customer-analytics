-- Tables are created by scripts/run_pipeline.py using pandas.to_sql.
-- Relational grain:
-- sales: one retained merchandise line on an invoice
-- invoices: one commercial invoice with >= 1 valid merchandise line
-- rfm: one identified customer
-- cancellations: negative cancellation line (not reconciled to specific orders)

CREATE INDEX IF NOT EXISTS idx_sales_invoice ON sales(invoice_no);
CREATE INDEX IF NOT EXISTS idx_invoice_month ON invoices(order_month);