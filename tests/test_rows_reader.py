import datetime
import unittest

from pse2json import electricity_bill as eb
from pse2json import rows_reader as rr

_USED_FOR_SERVICE_ROW = '1,459 kWh used for service 12/8/2019 - 1/8/2020'
_OTHER_ELECTRIC_CHARGES_CREDITS_ROW = 'Other Electric Charges & Credits 0.006794 0 kWh 0.00'


def _add_total(rows: list[str]) -> list[str]:
    total = 0.0
    for row in rows:
        charge = float(row.split(' ')[-1])
        total += charge

    rows_with_total = rows.copy()
    rows_with_total.append(f'Subtotal {total:.2f}')
    rows_with_total.append(f'Current Electric Charges $ {total:.2f}')
    return rows_with_total

def _build_rows(
    rows_for_total: list[str] = list[str](),
    rows: list[str] = list[str](),
    add_used_for_service_row: bool = True,
    add_other_electric_charges_credits_row: bool = True,
) -> list[str]:

    rows_for_total_local = list(rows_for_total)
    if add_other_electric_charges_credits_row:
        rows_for_total_local.append(_OTHER_ELECTRIC_CHARGES_CREDITS_ROW)

    result_rows = list(rows)
    if add_used_for_service_row:
        result_rows.append(_USED_FOR_SERVICE_ROW)

    result_rows.extend(_add_total(rows_for_total_local))

    return result_rows


class RowReaderTests(unittest.TestCase):

    def _assertDates(self, from_year: int, from_month: int, from_day: int, to_year: int, to_month: int, to_day: int, dates: eb.DateRange | None):
        if dates is None:
            self.assertIsNotNone(dates)
        else:
            self.assertEqual(datetime.date(from_year, from_month, from_day), dates.from_date)
            self.assertEqual(datetime.date(to_year, to_month, to_day), dates.to_date) 

    def _assertCharge(self, rate: float, consumed: float, charge_dollars: float, charge: eb.Charge):
        self.assertEqual(rate, charge.rate_usd_per_kwh)
        self.assertEqual(consumed, charge.consumed_kwh)
        self.assertEqual(int(round(charge_dollars * 100)), charge.charge_cents)

    def test_your_electric_charge_ignored(self):
        rows = _build_rows(
            rows=['Your Electric Charge Details (32 days) Rate x Unit = Charge'],
        )
        result = rr.read_electricity_bill(rows)
        self.assertEqual(0, result.subtotal_cents)


    def test_used_info(self):
        rows = _build_rows(
            rows=['1,459 kWh used for service 12/8/2019 - 1/8/2020'],
            add_used_for_service_row=False,
        )

        result = rr.read_electricity_bill(rows)
        self.assertEqual(1459, result.used_kwh)
        self._assertDates(2019, 12, 8, 2020, 1, 8, result.dates)

    def test_basic_charge(self):
        rows = _build_rows(
            ['Basic Charge $10.01 per month 10.01'],
        )

        result = rr.read_electricity_bill(rows)
        self.assertEqual(1001, result.basic_charge_cents)

    def test_basic_charge_as_two_rows(self):
        rows = _build_rows(
            [
                'Basic Charge $7.49 per month 5.94',
                'Basic Charge $7.49 per month 1.55',
            ],
        )

        result = rr.read_electricity_bill(rows)
        self.assertEqual(749, result.basic_charge_cents)

    def test_tier1(self):
        rows = _build_rows(
            ['Tier 1 (First 460 kWh Used) (12/9/2020 - 12/31/2020) 0.094437 460 kWh 43.44'],
        )

        result = rr.read_electricity_bill(rows)
        self.assertEqual(1, len(result.tier_1))
        self.assertEqual(0, len(result.tier_2))
        self.assertEqual(460, result.tier_1[0].up_to_kwh)
        self._assertDates(2020, 12, 9, 2020, 12, 31, result.tier_1[0].dates)
        self._assertCharge(0.094437, 460, 43.44, result.tier_1[0].charge)

    def test_tier2(self):
        rows = _build_rows(
            ['Tier 2 (Above 460 kWh Used) (12/9/2020 - 12/31/2020) 0.114643 788.9 kWh 90.44'],
        )

        result = rr.read_electricity_bill(rows)
        self.assertEqual(0, len(result.tier_1))
        self.assertEqual(1, len(result.tier_2))
        self.assertIsNone(result.tier_2[0].up_to_kwh)
        self._assertDates(2020, 12, 9, 2020, 12, 31, result.tier_2[0].dates)
        self._assertCharge(0.114643, 788.9, 90.44, result.tier_2[0].charge)

    def test_energy_exchange_credit(self):
        rows = _build_rows(
            ['Energy Exchange Credit (10/7/2021 - 10/31/2021) -0.007386 1,629 kWh -12.03'],
        )
        
        result = rr.read_electricity_bill(rows)

        self.assertEqual(1, len(result.energy_exchange_credit))
        self._assertDates(2021, 10, 7, 2021, 10, 31, result.energy_exchange_credit[0].dates)
        self._assertCharge(-0.007386, 1629, -12.03, result.energy_exchange_credit[0].charge)

    def test_federal_wind_power_credit(self):
        rows = _build_rows(
            ['Federal Wind Power Credit (12/9/2020 - 12/31/2020) -0.001893 1,248.9 kWh -2.36'],
        )
        
        result = rr.read_electricity_bill(rows)
        self.assertEqual(1, len(result.federal_wind_power_credit))
        self._assertDates(2020, 12, 9, 2020, 12, 31, result.federal_wind_power_credit[0].dates)
        self._assertCharge(-0.001893, 1248.9, -2.36, result.federal_wind_power_credit[0].charge)

    def test_dated_charge_no_dates(self):
        rows = _build_rows(
            ['Federal Wind Power Credit -0.001893 1,248.9 kWh -2.36'],
        )
        
        result = rr.read_electricity_bill(rows)
        self.assertEqual(1, len(result.federal_wind_power_credit))
        self.assertIsNone(result.federal_wind_power_credit[0].dates)
        self._assertCharge(-0.001893, 1248.9, -2.36, result.federal_wind_power_credit[0].charge)
    
    def test_renewable_energy_credit(self):
        rows = _build_rows(
            ['Renewable Energy Credit (12/9/2020 - 12/31/2020) -0.000082 1,248.9 kWh -0.10'],
        )
        result = rr.read_electricity_bill(rows)
        self.assertEqual(1, len(result.renewable_energy_credit))
        self._assertDates(2020, 12, 9, 2020, 12, 31, result.renewable_energy_credit[0].dates)
        self._assertCharge(-0.000082, 1248.9, -0.10, result.renewable_energy_credit[0].charge)
    
    def test_other_electric_charges_and_credits(self):
        rows = _build_rows(
            ['Other Electric Charges & Credits 0.006794 1,629 kWh 11.07'],
            add_other_electric_charges_credits_row=False,
        )
        result = rr.read_electricity_bill(rows)
        self._assertCharge(0.006794, 1629, 11.07, result.other)

    def test_electric_cons_program_charge(self):
        rows = _build_rows(
            ['Electric Cons. Program Charge (4/7/2021 - 4/30/2021) 0.004659 1,024.8 kWh 4.77'],
        )
        result = rr.read_electricity_bill(rows)
        self.assertEqual(1, len(result.electric_cons_program_charge))
        self._assertDates(2021, 4, 7, 2021, 4, 30, result.electric_cons_program_charge[0].dates)
        self._assertCharge(0.004659, 1024.8, 4.77, result.electric_cons_program_charge[0].charge)

    def test_power_cost_adjustment(self):
        rows = _build_rows(
            ['Power Cost Adjustment (6/8/2021 - 6/30/2021) 0.002135 887.8 kWh 1.90'],
        )
        result = rr.read_electricity_bill(rows)
        self.assertEqual(1, len(result.power_cost_adjustment))
        self._assertDates(2021, 6, 8, 2021, 6, 30, result.power_cost_adjustment[0].dates)
        self._assertCharge(0.002135, 887.8, 1.90, result.power_cost_adjustment[0].charge)

    def test_subtotal_total(self):
        rows = _build_rows(
            [
                'Basic Charge $7.49 per month 20.00',
                'Energy Exchange Credit -0.007386 1,629 kWh -12.03'
            ],
        )
        result = rr.read_electricity_bill(rows)
        self.assertEqual(797, result.subtotal_cents)
        self.assertEqual(797, result.total_cents)

    def test_state_utility_tax(self):
        rows = _build_rows(
            rows=['Taxes State Utility Tax ($6.89 included in above charges) 3.873%'],
        )
        result = rr.read_electricity_bill(rows)
        self.assertEqual(0.03873, result.state_utility_tax)

    def test_unknown_value(self):
        unknown_charge = 'Unknown Charge -0.000082 1,248.9 kWh -0.10'
        rows = [unknown_charge]
        with self.assertRaises(ValueError) as context:
            rr.read_electricity_bill(rows)
        exception = context.exception
        self.assertEqual(str(exception), 'Unknown value found: ' + unknown_charge)

    def test_charge_too_big(self):
        rows = _build_rows(
            ['Energy Exchange Credit -0.007386 1,629 kWh -12.05'],
        )
        with self.assertRaises(ValueError) as context:
            rr.read_electricity_bill(rows)
        exception = context.exception
        self.assertTrue(str(exception).startswith('rate '))

    def test_charge_too_small(self):
        rows = _build_rows(
            ['Energy Exchange Credit -0.007386 1,629 kWh -12.01'],
        )
        with self.assertRaises(ValueError) as context:
            rr.read_electricity_bill(rows)
        exception = context.exception
        self.assertTrue(str(exception).startswith('rate '))


if __name__ == '__main__':
    unittest.main()