import datetime, re

from collections.abc import Iterable

from pse2json import electricity_bill

_FIRST = '(First '
_FIRST_LEN = len(_FIRST)

_RE_FLOAT = re.compile(r'(\d*,)*\d+(\.\d+)?') # r'\-?(\d+,)*\d+(\.\d+)')
_RE_DATE_RANGE = re.compile(r'(\d{1,2}/\d{1,2}/\d{4}) \- (\d{1,2}/\d{1,2}/\d{4})')

def _date_range_from_match(m: re.Match) -> electricity_bill.DateRange:
    if m:
        from_date = datetime.datetime.strptime(m.group(1), '%m/%d/%Y').date()
        to_date = datetime.datetime.strptime(m.group(2), '%m/%d/%Y').date()
        return electricity_bill.DateRange(from_date, to_date)
    else:
        return None

def _float_from_match(m: re.Match) -> float:
    return float(m.group(0).replace(',', ''))

def _parse_charge(text: str) -> electricity_bill.Charge:
    items = text.split(' ')
    assert len(items) > 4, 'More than 4 tokens expected'
    assert items[-2] == 'kWh', 'Second from last token should be ''kWh'''

    rate_usd_per_kwh = float(items[-4].replace(',', ''))
    consumed_kwh = float(items[-3].replace(',', ''))
    charge_cents = int(items[-1].replace(',', '').replace('.', ''))

    calculated_charge_cents = int(round(rate_usd_per_kwh * consumed_kwh * 100))
    if abs(calculated_charge_cents - charge_cents) > 1:
        raise ValueError(
            f'rate {rate_usd_per_kwh} x consumed {consumed_kwh} ({calculated_charge_cents / 100}) != ' +
            f'charge {charge_cents / 100} in \'{text}\'')

    return electricity_bill.Charge(rate_usd_per_kwh, consumed_kwh, charge_cents)

def _parse_dated_charge(text: str) -> electricity_bill.DatedCharge:
    dates = _date_range_from_match(_RE_DATE_RANGE.search(text))
    charge = _parse_charge(text)
    return electricity_bill.DatedCharge(dates, charge)

def _parse_tier(text: str) -> electricity_bill.TierCharge:
    tier_index = 1 if text.startswith('Tier 1') else 2
    dates = _date_range_from_match(_RE_DATE_RANGE.search(text))

    up_to_kwh = None
    idx = text.find(_FIRST)
    if idx >= 0:
        up_to_kwh = _float_from_match(_RE_FLOAT.match(text[idx + _FIRST_LEN:]))

    charge = _parse_charge(text)
    return (
        electricity_bill.TierCharge(
            dates,
            up_to_kwh,
            charge),
        tier_index)

def read_electricity_bill(rows: Iterable[str]) -> electricity_bill.ElectricityBill:
    dates: electricity_bill.DateRange = None
    used_kwh: int = None
    basic_charge_cents: int = None
    tier_1: list[electricity_bill.TierCharge] = []
    tier_2: list[electricity_bill.TierCharge] = []
    energy_exchange_credit: electricity_bill.Charge = None
    electric_cons_program_charge: list[electricity_bill.DatedCharge] = []
    federal_wind_power_credit: list[electricity_bill.DatedCharge] = []
    renewable_energy_credit: list[electricity_bill.DatedCharge] = []
    power_cost_adjustment: list[electricity_bill.DatedCharge] = []
    other: electricity_bill.Charge = None
    subtotal_cents: int = None
    state_utility_tax: float = None
    total_cents: int = None

    for row in rows:
        if row.startswith('Your Electric Charge Details'):
            pass
        elif 'used for service' in row:
            used_kwh = _float_from_match(_RE_FLOAT.match(row))
            dates = _date_range_from_match(_RE_DATE_RANGE.search(row))
        elif 'Basic Charge' in row:
            basic_charge_cents = int(round(float(row.split(' ')[-1]) * 100))
        elif row.startswith('Tier '):
            tier, tier_index = _parse_tier(row)
            if tier_index == 1:
                tier_1.append(tier)
            else:
                tier_2.append(tier)
        elif row.startswith('Energy Exchange Credit'):
            energy_exchange_credit = _parse_charge(row)
        elif row.startswith('Electric Cons. Program Charge'):
            electric_cons_program_charge.append(_parse_dated_charge(row))
        elif row.startswith('Federal Wind Power Credit'):
            federal_wind_power_credit.append(_parse_dated_charge(row))
        elif row.startswith('Renewable Energy Credit'):
            renewable_energy_credit.append(_parse_dated_charge(row))
        elif row.startswith('Power Cost Adjustment'):
            power_cost_adjustment.append(_parse_dated_charge(row))
        elif row.startswith('Other Electric Charges & Credits'):
            other = _parse_charge(row)
        elif row.startswith('Subtotal'):
            subtotal_cents = int(round(float(row.split(' ')[-1]) * 100))
        elif row.startswith('Taxes State Utility Tax'):    
            state_utility_tax = _float_from_match(_RE_FLOAT.search(row.split(") ")[-1])) / 100
        elif row.startswith('Current Electric Charges'):
            total_cents = int(round(float(row.split(' ')[-1]) * 100))
        else:
            raise ValueError(f'Unknown value found: {row}')

    energy_exchange_credit_charge_cents = (
        energy_exchange_credit.charge_cents if energy_exchange_credit else None)

    other_charge_cents = other.charge_cents if other else None
    values = [basic_charge_cents,
        sum(x.charge.charge_cents for x in tier_1),
        sum(x.charge.charge_cents for x in tier_2),
        energy_exchange_credit_charge_cents,
        sum(x.charge.charge_cents for x in electric_cons_program_charge),
        sum(x.charge.charge_cents for x in federal_wind_power_credit),
        sum(x.charge.charge_cents for x in renewable_energy_credit),
        sum(x.charge.charge_cents for x in power_cost_adjustment),
        other_charge_cents]
    total_sum = sum(v for v in values if v)

    if total_sum:
        assert total_sum == subtotal_cents, f'Subtotal doesn\'t match with calculated sum: expected {total_sum}, actual {subtotal_cents}'
        assert total_sum == total_cents, 'Total doesn\'t match with calculated sum'


    return electricity_bill.ElectricityBill(
        dates,
        used_kwh,
        basic_charge_cents,
        tier_1,
        tier_2,
        energy_exchange_credit,
        electric_cons_program_charge,
        federal_wind_power_credit,
        renewable_energy_credit,
        power_cost_adjustment,
        other,
        subtotal_cents,
        state_utility_tax,
        total_cents)
