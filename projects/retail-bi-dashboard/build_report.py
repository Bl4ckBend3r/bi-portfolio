"""Build an offline SQLite star schema and an interactive, self-contained HTML report."""
from __future__ import annotations

import csv
import json
import sqlite3
from collections import defaultdict
from decimal import Decimal
from html import escape
from pathlib import Path

from generate_data import OUTPUT_DIR, generate_dates, main as generate_source

ROOT = Path(__file__).parent
DB = ROOT / 'output' / 'retail.db'
REPORT = ROOT / 'output' / 'dashboard.html'


def read_rows(name: str) -> list[dict[str, str]]:
    with (OUTPUT_DIR / name).open(encoding='utf-8', newline='') as source:
        return list(csv.DictReader(source))


def build() -> None:
    generate_source()
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    with sqlite3.connect(DB) as con:
        con.executescript('''
            PRAGMA foreign_keys=ON;
            CREATE TABLE DimDate(DateKey INTEGER PRIMARY KEY, Date TEXT NOT NULL, Year INTEGER NOT NULL, MonthNumber INTEGER NOT NULL);
            CREATE TABLE DimProduct(ProductKey INTEGER PRIMARY KEY, ProductName TEXT NOT NULL, Category TEXT NOT NULL);
            CREATE TABLE DimStore(StoreKey INTEGER PRIMARY KEY, StoreName TEXT NOT NULL, City TEXT NOT NULL);
            CREATE TABLE FactSales(SaleKey INTEGER PRIMARY KEY, OrderID INTEGER NOT NULL, DateKey INTEGER NOT NULL REFERENCES DimDate(DateKey), ProductKey INTEGER NOT NULL REFERENCES DimProduct(ProductKey), StoreKey INTEGER NOT NULL REFERENCES DimStore(StoreKey), Quantity INTEGER NOT NULL CHECK(Quantity>0), RevenueCents INTEGER NOT NULL CHECK(RevenueCents>=0), CostCents INTEGER NOT NULL CHECK(CostCents>=0));
            CREATE INDEX IX_FactSales_Date ON FactSales(DateKey);
            CREATE INDEX IX_FactSales_Product ON FactSales(ProductKey);
            CREATE INDEX IX_FactSales_Store ON FactSales(StoreKey);
        ''')
        con.executemany('INSERT INTO DimDate VALUES(?,?,?,?)', [(r['DateKey'], r['Date'], r['Year'], r['MonthNumber']) for r in read_rows('dates.csv')])
        con.executemany('INSERT INTO DimProduct VALUES(?,?,?)', [(r['ProductKey'], r['ProductName'], r['Category']) for r in read_rows('products.csv')])
        con.executemany('INSERT INTO DimStore VALUES(?,?,?)', [(r['StoreKey'], r['StoreName'], r['City']) for r in read_rows('stores.csv')])
        sales = read_rows('sales.csv')
        def cents(value: str) -> int:
            return int(Decimal(value) * 100)
        con.executemany('INSERT INTO FactSales VALUES(?,?,?,?,?,?,?,?)', [
            (r['SaleKey'], r['OrderID'], r['DateKey'], r['ProductKey'], r['StoreKey'], r['Quantity'], cents(r['Revenue']), cents(r['Cost'])) for r in sales
        ])
        facts = con.execute('''SELECT d.Year, d.MonthNumber, p.Category, s.StoreName, f.OrderID, f.Quantity, f.RevenueCents, f.CostCents
            FROM FactSales f JOIN DimDate d ON f.DateKey=d.DateKey JOIN DimProduct p ON f.ProductKey=p.ProductKey JOIN DimStore s ON f.StoreKey=s.StoreKey''').fetchall()
        assert len(facts) == len(sales)
        assert con.execute('PRAGMA foreign_key_check').fetchall() == []
        assert sum(row[6] for row in facts) == sum(cents(r['Revenue']) for r in sales)
    payload = [list(row) for row in facts]
    template = (ROOT / 'dashboard_template.html').read_text(encoding='utf-8')
    REPORT.write_text(template.replace('/*DATA*/null', json.dumps(payload, ensure_ascii=False)), encoding='utf-8')
    print(f'Report: {REPORT} | rows: {len(facts)} | revenue: {sum(r[6] for r in facts)/100:,.2f} PLN')


if __name__ == '__main__':
    build()
