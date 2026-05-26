"""
Unit tests for the ATO tax calculator.
Run: uv run --directory packages/agent pytest tests/test_tax_calculator.py -v
"""
import pytest
from tools.tax_calculator import TaxInput, calculate, _income_tax, _lito, _medicare_levy, _medicare_levy_surcharge, _help_repayment


# ── Income tax ─────────────────────────────────────────────────────────────────

class TestIncomeTax2526:
    def test_zero_income(self):
        assert _income_tax(0, "2025-26") == 0.0

    def test_below_tax_free_threshold(self):
        assert _income_tax(18_200, "2025-26") == 0.0

    def test_at_18201(self):
        # 1 dollar in 16% band
        assert _income_tax(18_201, "2025-26") == pytest.approx(0.16, abs=0.01)

    def test_mid_first_band(self):
        # $30,000: (30000 - 18200) * 0.16 = 11800 * 0.16 = 1888
        assert _income_tax(30_000, "2025-26") == pytest.approx(1_888.0, abs=0.5)

    def test_at_45000(self):
        # Full first band: (45000 - 18200) * 0.16 = 26800 * 0.16 = 4288
        assert _income_tax(45_000, "2025-26") == pytest.approx(4_288.0, abs=0.5)

    def test_at_45001(self):
        # $1 into 30% band: 4288 + 0.30 = 4288.30
        assert _income_tax(45_001, "2025-26") == pytest.approx(4_288.30, abs=0.01)

    def test_mid_second_band(self):
        # $90,000: 4288 + (90000 - 45000) * 0.30 = 4288 + 13500 = 17788
        assert _income_tax(90_000, "2025-26") == pytest.approx(17_788.0, abs=0.5)

    def test_at_135000(self):
        # 4288 + (135000 - 45000) * 0.30 = 4288 + 27000 = 31288
        assert _income_tax(135_000, "2025-26") == pytest.approx(31_288.0, abs=0.5)

    def test_at_135001(self):
        assert _income_tax(135_001, "2025-26") == pytest.approx(31_288.37, abs=0.01)

    def test_at_190000(self):
        # 31288 + (190000 - 135000) * 0.37 = 31288 + 20350 = 51638
        assert _income_tax(190_000, "2025-26") == pytest.approx(51_638.0, abs=0.5)

    def test_at_190001(self):
        assert _income_tax(190_001, "2025-26") == pytest.approx(51_638.45, abs=0.01)

    def test_high_income(self):
        # $250,000: 51638 + (250000 - 190000) * 0.45 = 51638 + 27000 = 78638
        assert _income_tax(250_000, "2025-26") == pytest.approx(78_638.0, abs=0.5)


class TestIncomeTax2627:
    """2026-27 has 15% instead of 16% in the second band."""

    def test_below_tax_free_threshold(self):
        assert _income_tax(18_200, "2026-27") == 0.0

    def test_at_45000(self):
        # (45000 - 18200) * 0.15 = 26800 * 0.15 = 4020
        assert _income_tax(45_000, "2026-27") == pytest.approx(4_020.0, abs=0.5)

    def test_at_135000(self):
        # 4020 + (135000 - 45000) * 0.30 = 4020 + 27000 = 31020
        assert _income_tax(135_000, "2026-27") == pytest.approx(31_020.0, abs=0.5)

    def test_at_190000(self):
        # 31020 + 55000 * 0.37 = 31020 + 20350 = 51370
        assert _income_tax(190_000, "2026-27") == pytest.approx(51_370.0, abs=0.5)

    def test_difference_from_2526(self):
        # At $45,000 the 2026-27 tax should be $268 lower (26800 * 0.01)
        diff = _income_tax(45_000, "2025-26") - _income_tax(45_000, "2026-27")
        assert diff == pytest.approx(268.0, abs=0.5)


# ── LITO ───────────────────────────────────────────────────────────────────────

class TestLITO:
    def test_zero(self):
        assert _lito(0) == 700.0

    def test_at_37500(self):
        assert _lito(37_500) == 700.0

    def test_at_37501(self):
        assert _lito(37_501) == pytest.approx(699.95, abs=0.01)

    def test_at_45000(self):
        # 700 - 7500 * 0.05 = 700 - 375 = 325
        assert _lito(45_000) == pytest.approx(325.0, abs=0.01)

    def test_at_45001(self):
        assert _lito(45_001) == pytest.approx(324.985, abs=0.01)

    def test_at_66667(self):
        assert _lito(66_667) == pytest.approx(0.0, abs=1.0)

    def test_above_66667(self):
        assert _lito(100_000) == 0.0


# ── Medicare levy ──────────────────────────────────────────────────────────────

class TestMedicareLevy:
    def test_below_threshold(self):
        assert _medicare_levy(26_000) == 0.0

    def test_shade_in_start(self):
        assert _medicare_levy(26_001) == pytest.approx(0.10, abs=0.01)

    def test_shade_in_midpoint(self):
        # (29250 - 26000) * 0.10 = 325
        assert _medicare_levy(29_250) == pytest.approx(325.0, abs=0.5)

    def test_at_32500(self):
        # Both methods should give same: (32500-26000)*0.10 = 650; 32500*0.02 = 650
        assert _medicare_levy(32_500) == pytest.approx(650.0, abs=0.5)

    def test_above_shade_in(self):
        assert _medicare_levy(50_000) == pytest.approx(1_000.0, abs=0.5)

    def test_standard_rate(self):
        assert _medicare_levy(100_000) == pytest.approx(2_000.0, abs=0.5)


# ── MLS ────────────────────────────────────────────────────────────────────────

class TestMLS:
    def test_no_cover_below_threshold(self):
        assert _medicare_levy_surcharge(100_000, False) == 0.0

    def test_with_cover_no_surcharge(self):
        assert _medicare_levy_surcharge(200_000, True) == 0.0

    def test_tier1(self):
        assert _medicare_levy_surcharge(110_000, False) == pytest.approx(1_100.0, abs=0.5)

    def test_tier1_boundary(self):
        assert _medicare_levy_surcharge(101_001, False) == pytest.approx(1_010.01, abs=0.5)

    def test_tier2(self):
        assert _medicare_levy_surcharge(120_000, False) == pytest.approx(1_500.0, abs=0.5)

    def test_tier3(self):
        assert _medicare_levy_surcharge(200_000, False) == pytest.approx(3_000.0, abs=0.5)


# ── HELP ───────────────────────────────────────────────────────────────────────

class TestHELP:
    def test_no_debt(self):
        assert _help_repayment(100_000, False) == 0.0

    def test_below_threshold(self):
        assert _help_repayment(67_000, True) == 0.0

    def test_at_67001(self):
        assert _help_repayment(67_001, True) == pytest.approx(0.15, abs=0.01)

    def test_mid_first_band(self):
        # (96000 - 67000) * 0.15 = 29000 * 0.15 = 4350
        assert _help_repayment(96_000, True) == pytest.approx(4_350.0, abs=0.5)

    def test_at_125000(self):
        # (125000 - 67000) * 0.15 = 58000 * 0.15 = 8700
        assert _help_repayment(125_000, True) == pytest.approx(8_700.0, abs=0.5)

    def test_at_125001(self):
        assert _help_repayment(125_001, True) == pytest.approx(8_700.17, abs=0.01)

    def test_mid_second_band(self):
        # 8700 + (150000 - 125000) * 0.17 = 8700 + 4250 = 12950
        assert _help_repayment(150_000, True) == pytest.approx(12_950.0, abs=0.5)

    def test_at_179285(self):
        # 8700 + (179285 - 125000) * 0.17 = 8700 + 9228.45 = 17928.45
        assert _help_repayment(179_285, True) == pytest.approx(17_928.45, abs=1.0)

    def test_above_179285(self):
        # 200000 * 0.10 = 20000
        assert _help_repayment(200_000, True) == pytest.approx(20_000.0, abs=0.5)


# ── Integration: calculate() ───────────────────────────────────────────────────

class TestCalculate:
    def test_zero_income(self):
        result = calculate(TaxInput(income=0, financial_year="2025-26"))
        assert result.total_tax == 0.0
        assert result.net_income == 0.0
        assert result.effective_rate == 0.0

    def test_below_tax_free_threshold(self):
        result = calculate(TaxInput(income=18_200, financial_year="2025-26"))
        assert result.income_tax == 0.0
        assert result.total_tax == 0.0

    def test_typical_income_2526(self):
        # $85,000: income_tax = 4288 + (85000-45000)*0.30 = 4288+12000 = 16288
        # lito = 0 (above 66667)
        # medicare = 85000 * 0.02 = 1700
        # total = 16288 + 1700 = 17988
        result = calculate(TaxInput(income=85_000, financial_year="2025-26"))
        assert result.income_tax == pytest.approx(16_288.0, abs=1.0)
        assert result.medicare_levy == pytest.approx(1_700.0, abs=1.0)
        assert result.total_tax == pytest.approx(17_988.0, abs=1.0)

    def test_typical_income_2627(self):
        # $85,000 in 2026-27: income_tax = 4020 + (85000-45000)*0.30 = 4020+12000 = 16020
        result = calculate(TaxInput(income=85_000, financial_year="2026-27"))
        assert result.income_tax == pytest.approx(16_020.0, abs=1.0)

    def test_lito_applies_below_37500(self):
        result = calculate(TaxInput(income=30_000, financial_year="2025-26"))
        assert result.lito == pytest.approx(700.0, abs=1.0)

    def test_with_help_debt(self):
        result = calculate(TaxInput(income=85_000, financial_year="2025-26", has_help_debt=True))
        # help = (85000 - 67000) * 0.15 = 18000 * 0.15 = 2700
        assert result.help_repayment == pytest.approx(2_700.0, abs=1.0)

    def test_with_mls(self):
        result = calculate(TaxInput(income=110_000, financial_year="2025-26", has_private_hospital_cover=False))
        assert result.medicare_levy_surcharge == pytest.approx(1_100.0, abs=1.0)

    def test_with_private_cover_no_mls(self):
        result = calculate(TaxInput(income=110_000, financial_year="2025-26", has_private_hospital_cover=True))
        assert result.medicare_levy_surcharge == 0.0

    def test_negative_income_raises(self):
        with pytest.raises(Exception):
            TaxInput(income=-1, financial_year="2025-26")

    def test_net_income_consistency(self):
        result = calculate(TaxInput(income=95_000, financial_year="2025-26"))
        assert result.net_income == pytest.approx(result.gross_income - result.total_tax, abs=0.01)

    def test_effective_rate_consistency(self):
        result = calculate(TaxInput(income=95_000, financial_year="2025-26"))
        expected_rate = result.total_tax / 95_000 * 100
        assert result.effective_rate == pytest.approx(expected_rate, abs=0.01)
