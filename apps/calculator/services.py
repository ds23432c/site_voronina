from decimal import Decimal, ROUND_HALF_UP


MONEY_QUANT = Decimal("0.01")


def to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    return to_decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def format_money(value: Decimal) -> str:
    quantized = money(value)
    text = f"{quantized:,.2f}".replace(",", " ").replace(".", ",")
    return f"{text} ₽"


def format_percent(value: Decimal) -> str:
    quantized = to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{quantized}".replace(".", ",") + "%"


def calculate_ndfl(income: Decimal) -> dict:
    income = money(income)
    threshold = Decimal("5000000")
    low_rate = Decimal("0.13")
    high_rate = Decimal("0.15")
    low_part = min(income, threshold)
    high_part = max(income - threshold, Decimal("0"))
    tax = money(low_part * low_rate + high_part * high_rate)
    return {
        "income": income,
        "tax": tax,
        "net_income": money(income - tax),
        "average_rate": (tax / income * Decimal("100")) if income else Decimal("0"),
        "low_part": low_part,
        "high_part": high_part,
    }


def calculate_contributions(payroll: Decimal, injury_rate: Decimal = Decimal("0")) -> dict:
    payroll = money(payroll)
    injury_rate = to_decimal(injury_rate) / Decimal("100")
    base_limit = Decimal("2225000")
    unified_low_rate = Decimal("0.30")
    unified_high_rate = Decimal("0.151")
    low_part = min(payroll, base_limit)
    high_part = max(payroll - base_limit, Decimal("0"))
    unified = money(low_part * unified_low_rate + high_part * unified_high_rate)
    injury = money(payroll * injury_rate)
    total = money(unified + injury)
    return {
        "payroll": payroll,
        "base_limit": base_limit,
        "unified": unified,
        "injury": injury,
        "total": total,
        "low_part": low_part,
        "high_part": high_part,
        "effective_rate": (total / payroll * Decimal("100")) if payroll else Decimal("0"),
    }


def calculate_usn(income: Decimal, expenses: Decimal, tax_object: str) -> dict:
    income = money(income)
    expenses = money(expenses or Decimal("0"))
    min_tax = money(income * Decimal("0.01"))

    if tax_object == "income":
        tax_base = income
        calculated_tax = money(tax_base * Decimal("0.06"))
        final_tax = calculated_tax
        rate = Decimal("6")
    else:
        tax_base = max(income - expenses, Decimal("0"))
        calculated_tax = money(tax_base * Decimal("0.15"))
        final_tax = max(calculated_tax, min_tax)
        rate = Decimal("15")

    return {
        "income": income,
        "expenses": expenses,
        "tax_base": money(tax_base),
        "calculated_tax": calculated_tax,
        "min_tax": min_tax,
        "tax": money(final_tax),
        "rate": rate,
        "tax_object": tax_object,
    }


def calculate_vat(amount: Decimal, rate: Decimal, mode: str) -> dict:
    amount = money(amount)
    rate = to_decimal(rate) / Decimal("100")
    if mode == "included":
        net = money(amount / (Decimal("1") + rate))
        vat = money(amount - net)
        total = amount
    else:
        net = amount
        vat = money(amount * rate)
        total = money(amount + vat)

    return {
        "amount": amount,
        "rate": rate * Decimal("100"),
        "net": net,
        "vat": vat,
        "total": total,
        "mode": mode,
    }


def calculate_peni(debt: Decimal, days_overdue: int, key_rate: Decimal) -> dict:
    debt = money(debt)
    days_overdue = int(days_overdue)
    key_rate = to_decimal(key_rate)
    daily_first = key_rate / Decimal("100") / Decimal("300")
    daily_after = key_rate / Decimal("100") / Decimal("150")
    first_days = min(days_overdue, 30)
    rest_days = max(days_overdue - 30, 0)
    penalty = money(debt * daily_first * Decimal(first_days) + debt * daily_after * Decimal(rest_days))
    return {
        "debt": debt,
        "days_overdue": days_overdue,
        "key_rate": key_rate,
        "penalty": penalty,
        "first_days": first_days,
        "rest_days": rest_days,
    }


def calculate_salary(gross_salary: Decimal, bonus: Decimal = Decimal("0")) -> dict:
    gross_salary = money(gross_salary)
    bonus = money(bonus or Decimal("0"))
    total_accrual = money(gross_salary + bonus)
    ndfl = calculate_ndfl(total_accrual)
    net_salary = money(total_accrual - ndfl["tax"])
    contributions = calculate_contributions(total_accrual, Decimal("0"))
    employer_cost = money(total_accrual + contributions["total"])
    return {
        "gross_salary": gross_salary,
        "bonus": bonus,
        "total_accrual": total_accrual,
        "ndfl": ndfl["tax"],
        "net_salary": net_salary,
        "employer_cost": employer_cost,
        "contributions": contributions["total"],
    }