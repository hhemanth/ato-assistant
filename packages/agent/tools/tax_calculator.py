"""
Pure Python Australian tax calculator — 2025-26 and 2026-27 only.
No LLM calls. All figures from ATO.
"""
from typing import Literal
from pydantic import BaseModel, field_validator

FinancialYear = Literal["2025-26", "2026-27"]

# Income tax brackets: list of (lower_bound, rate, base_tax_at_lower_bound)
_BRACKETS: dict[FinancialYear, list[tuple[float, float, float]]] = {
    "2025-26": [
        (190_001, 0.45, 51_638),
        (135_001, 0.37, 31_288),
        (45_001,  0.30,  4_288),
        (18_201,  0.16,      0),
        (0,       0.00,      0),
    ],
    "2026-27": [
        (190_001, 0.45, 51_370),
        (135_001, 0.37, 31_020),
        (45_001,  0.30,  4_020),
        (18_201,  0.15,      0),
        (0,       0.00,      0),
    ],
}


class TaxInput(BaseModel):
    income: float
    financial_year: FinancialYear = "2025-26"
    has_help_debt: bool = False
    has_private_hospital_cover: bool = False

    @field_validator("income")
    @classmethod
    def income_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("income must be non-negative")
        return round(v, 2)


class TaxResult(BaseModel):
    gross_income: float
    financial_year: str
    income_tax: float
    lito: float
    medicare_levy: float
    medicare_levy_surcharge: float
    help_repayment: float
    total_tax: float
    net_income: float
    effective_rate: float   # percentage, e.g. 21.6


def _income_tax(income: float, year: FinancialYear) -> float:
    for lower, rate, base in _BRACKETS[year]:
        if income >= lower:
            return round(base + (income - lower + (1 if lower > 0 else 0)) * rate, 2)
    return 0.0


def _lito(income: float) -> float:
    if income <= 37_500:
        offset = 700.0
    elif income <= 45_000:
        offset = 700 - (income - 37_500) * 0.05
    elif income <= 66_667:
        offset = 325 - (income - 45_000) * 0.015
    else:
        offset = 0.0
    return round(max(offset, 0.0), 2)


def _medicare_levy(income: float) -> float:
    if income <= 26_000:
        return 0.0
    elif income <= 32_500:
        return round((income - 26_000) * 0.10, 2)
    return round(income * 0.02, 2)


def _medicare_levy_surcharge(income: float, has_cover: bool) -> float:
    if has_cover or income <= 101_000:
        return 0.0
    elif income <= 118_000:
        rate = 0.010
    elif income <= 158_000:
        rate = 0.0125
    else:
        rate = 0.015
    return round(income * rate, 2)


def _help_repayment(income: float, has_help: bool) -> float:
    if not has_help or income <= 67_000:
        return 0.0
    elif income <= 125_000:
        return round((income - 67_000) * 0.15, 2)
    elif income <= 179_285:
        return round(8_700 + (income - 125_000) * 0.17, 2)
    return round(income * 0.10, 2)


def calculate(inp: TaxInput) -> TaxResult:
    income = inp.income
    year = inp.financial_year

    gross_tax = _income_tax(income, year)
    lito = min(_lito(income), gross_tax)          # can't reduce below zero
    income_tax = round(max(gross_tax - lito, 0), 2)

    medicare = _medicare_levy(income)
    mls = _medicare_levy_surcharge(income, inp.has_private_hospital_cover)
    help_rep = _help_repayment(income, inp.has_help_debt)

    total = round(income_tax + medicare + mls + help_rep, 2)
    net = round(income - total, 2)
    eff = round((total / income * 100) if income > 0 else 0.0, 2)

    return TaxResult(
        gross_income=income,
        financial_year=year,
        income_tax=income_tax,
        lito=lito,
        medicare_levy=medicare,
        medicare_levy_surcharge=mls,
        help_repayment=help_rep,
        total_tax=total,
        net_income=net,
        effective_rate=eff,
    )
