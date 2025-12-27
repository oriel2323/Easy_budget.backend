from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class TableRow(BaseModel):
    key: str
    label: str
    values: List[Decimal]


class TableSection(BaseModel):
    title: str
    rows: List[TableRow]
    total_row: Optional[TableRow] = None


class FullPnLTable(BaseModel):
    columns: List[str]  # 12 חודשים + "שנתי"
    sections: List[TableSection]


class YearlySummaryRow(BaseModel):
    key: str
    label: str
    value: Decimal


class PnLReportOut(BaseModel):
    columns: List[str]
    table_full: FullPnLTable
    table_yearly_summary: List[YearlySummaryRow]
