from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateRange:
    from_date: date
    to_date: date


@dataclass(frozen=True)
class Charge:
    rate_usd_per_kwh: float
    consumed_kwh: float
    charge_cents: int


@dataclass(frozen=True)
class TierCharge:
    dates: DateRange | None
    up_to_kwh: int
    charge: Charge


@dataclass(frozen=True)
class DatedCharge:
    dates: DateRange | None
    charge: Charge    


@dataclass(frozen=True)
class ElectricityBill:
    dates: DateRange
    used_kwh: int
    basic_charge_cents: int
    tier_1: list[TierCharge]
    tier_2: list[TierCharge]
    energy_exchange_credit: list[DatedCharge]
    electric_cons_program_charge: list[DatedCharge]
    federal_wind_power_credit: list[DatedCharge]
    renewable_energy_credit: list[DatedCharge]
    power_cost_adjustment: list[DatedCharge]
    other: Charge
    subtotal_cents: int
    state_utility_tax: float
    total_cents: int
