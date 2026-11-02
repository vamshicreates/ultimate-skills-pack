#!/usr/bin/env python3
"""Check a production-budget control model. Standard library only."""
import argparse
import datetime
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def number(value, label):
    if isinstance(value, bool) or value is None:
        raise ValueError(f'{label}: numeric value required')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f'{label}: invalid number') from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f'{label}: must be finite and nonnegative')
    return result


def cash(value):
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def check(model):
    if not isinstance(model, dict):
        raise ValueError('Budget must be an object')
    if not isinstance(model.get('currency'), str) or not model['currency'].strip():
        raise ValueError('currency is required')
    datetime.date.fromisoformat(model.get('as_of', ''))
    rate = number(model.get('contingency_rate'), 'contingency_rate')
    if rate > 1:
        raise ValueError('contingency_rate must be a fraction between 0 and 1')
    lines = model.get('lines')
    if not isinstance(lines, list) or not lines:
        raise ValueError('At least one budget line is required')
    categories, excluded, pending, ids = {}, [], [], set()
    for row in lines:
        key = row.get('id')
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError(f'Empty or duplicate line ID: {key!r}')
        ids.add(key)
        for field in ('category', 'item', 'basis'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'{key}: {field} required')
        status = row.get('status')
        if status not in ('included', 'excluded', 'tbd'):
            raise ValueError(f'{key}: invalid status')
        factors = [row.get(k) for k in ('quantity', 'units', 'rate')]
        for field, value in zip(('quantity', 'units', 'rate'), factors):
            if value is not None:
                number(value, f'{key}.{field}')
        if status == 'tbd':
            if all(x is not None for x in factors):
                raise ValueError(f'{key}: TBD row has no missing factor; use excluded for a known excluded amount')
            pending.append(key)
            continue
        if status == 'excluded':
            excluded.append(key)
            continue
        q, units, amount = [number(v, f'{key}.{k}') for v, k in zip(factors, ('quantity', 'units', 'rate'))]
        cat = row['category']
        categories[cat] = categories.get(cat, Decimal(0)) + q * units * amount
    if not categories:
        raise ValueError('No included priced budget lines')
    # Keep exact products through the subtotal, then round for presentation.
    categories = {name: cash(value) for name, value in categories.items()}
    direct = cash(sum(categories.values(), Decimal(0)))
    contingency = cash(direct * rate)
    total = direct + contingency
    values = {'direct': direct, 'contingency': contingency, 'total': total}
    controls = model.get('expected', {})
    for key, actual in values.items():
        if key in controls and cash(number(controls[key], f'expected.{key}')) != actual:
            raise ValueError(f'{key} mismatch: calculated {actual}, expected {controls[key]}')
    expected_categories = controls.get('categories', {})
    for name, expected in expected_categories.items():
        if name not in categories or cash(categories[name]) != cash(number(expected, f'expected.categories.{name}')):
            raise ValueError(f'Category control mismatch: {name}')
    return {'currency': model['currency'], 'as_of': model['as_of'],
            'categories': {k: str(cash(v)) for k, v in categories.items()},
            **{k: str(v) for k, v in values.items()},
            'unpriced_tbd_ids': pending, 'excluded_ids': excluded}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    args = parser.parse_args()
    try:
        report = check(json.loads(args.model.read_text(encoding='utf-8')))
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        parser.exit(1, f'Budget check failed: {exc}\n')
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
