"""Run with `python -m unittest discover -s projects/retail-bi-dashboard`."""
import csv
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


class RetailIntegrationTest(unittest.TestCase):
    def test_reproducible_star_schema_and_report(self):
        script = ROOT / 'build_report.py'
        subprocess.run([sys.executable, str(script)], check=True, stdout=subprocess.DEVNULL)
        with sqlite3.connect(ROOT / 'output' / 'retail.db') as con:
            row = con.execute('SELECT COUNT(*), SUM(RevenueCents), SUM(CostCents), COUNT(DISTINCT OrderID) FROM FactSales').fetchone()
            self.assertEqual(row[0], 19359)
            self.assertEqual(row[3], 12000)
            self.assertGreater(row[1], row[2])
            self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(), [])
        report = (ROOT / 'output' / 'dashboard.html').read_text(encoding='utf-8')
        self.assertIn('Monthly revenue', report)
        self.assertIn('Zielona Gora Focus', report)
        self.assertNotIn('/*DATA*/null', report)
        subprocess.run([sys.executable, str(script)], check=True, stdout=subprocess.DEVNULL)
        with sqlite3.connect(ROOT / 'output' / 'retail.db') as con:
            self.assertEqual(con.execute('SELECT COUNT(*), SUM(RevenueCents) FROM FactSales').fetchone(), row[:2])


if __name__ == '__main__':
    unittest.main()
