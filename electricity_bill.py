from typing import NamedTuple
from datetime import date

# datetime.strptime('11/7/2019', '%m/%d/%Y').date()

class DateRange(NamedTuple):
    from_date: date
    to_date: date


class Charge(NamedTuple):
    rate_usd_per_kwh: float
    consumed_kwh: int
    charge_cents: int


class TierPrice(NamedTuple):
    dates: DateRange
    up_to_kwh: int
    charge: Charge


class DatedCredit(NamedTuple):
    dates: DateRange
    charge: Charge    


class ElectricityBill(NamedTuple):
    dates: DateRange
    used_kwh: int
    basic_charge_cents: int
    tier_1: list[TierPrice]
    tier_2: list[TierPrice]
    credit: Charge
    federal_wind_power_credit: list[DatedCredit]
    renewable_energycredit: list[DatedCredit]
    other: Charge
    subtotal_cents: int
    total_cents: int
