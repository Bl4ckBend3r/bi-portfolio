"""Run with `python -m unittest discover -s projects/etl-data-warehouse`."""
import csv
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('etl_pipeline.py')


class ETLIntegrationTest(unittest.TestCase):
    def test_incremental_idempotence_and_customer_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / 'warehouse.db'
            for _ in range(2):
                subprocess.run([sys.executable, str(SCRIPT), '--db', str(db)], check=True, stdout=subprocess.DEVNULL)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute('SELECT COUNT(*) FROM FactOrders').fetchone()[0], 5)
                self.assertEqual(con.execute('SELECT ROUND(SUM(Amount),2) FROM FactOrders').fetchone()[0], 2227.39)
                self.assertEqual(con.execute('SELECT City FROM DimCustomer WHERE CustomerID=2 AND IsCurrent=1').fetchone()[0], 'Zielona Gora')
                self.assertEqual(con.execute('SELECT COUNT(*) FROM DimCustomer WHERE CustomerID=2').fetchone()[0], 2)
                self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])
                self.assertEqual(con.execute('SELECT SUM(RowsLoaded) FROM AuditLog WHERE BatchName="2026-09-02"').fetchone()[0], 4)

    def test_rejected_row_does_not_advance_watermark(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch = root / 'source' / '2026-09-03'
            batch.mkdir(parents=True)
            customers = batch / 'customers.csv'
            customers.write_text('CustomerID,CustomerName,City,ModifiedAt\n7,Ada,Łódź,2026-09-03T09:00:00\n', encoding='utf-8')
            orders = batch / 'orders.csv'
            orders.write_text('OrderID,CustomerID,OrderDate,Amount,ModifiedAt\n77,7,2026-09-03,-1,2026-09-03T10:00:00\n', encoding='utf-8')
            db = root / 'warehouse.db'
            command = [sys.executable, str(SCRIPT), '--source', str(root / 'source'), '--db', str(db)]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute("SELECT LastModifiedAt FROM ETLWatermark WHERE SourceName='orders'").fetchone()[0], '1900-01-01T00:00:00')
                self.assertEqual(con.execute('SELECT COUNT(*) FROM DataQualityLog').fetchone()[0], 1)
            orders.write_text('OrderID,CustomerID,OrderDate,Amount,ModifiedAt\n77,7,2026-09-03,19.99,2026-09-03T10:00:00\n', encoding='utf-8')
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute('SELECT Amount FROM FactOrders').fetchone()[0], 19.99)


if __name__ == '__main__':
    unittest.main()
