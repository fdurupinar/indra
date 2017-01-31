import re
import json
from sympy.physics import units

M = units.moles / units.liter

def parse_value(value):
    # Pattern 1 example: 31.0x10^-6(molar)
    pattern = r'([0-9]+\.[0-9]+)x10\^([-]?[^ ]+)\(molar\)'
    res = re.match(pattern, value)
    if res:
        num, exponent = res.groups()
        rate_constant = float(num) * 10**float(exponent) * M
        return rate_constant
    # Kd
    # Pattern 2 example: 1.5x10^-6 ~0.5(molar)
    # could extract uncertainty following '~'
    # r'([0-9]+\.[0-9]+)x10\^([-]?[^ ]+).+~(.+)\(molar\)'
    pattern = r'([0-9]+\.[0-9]+)x10\^([-]?[^ ]+).*\(molar\)'
    res = re.match(pattern, value)
    if res:
        num, exponent = resgroups()
        rate_constant = float(num) * 10**float(exponent) * M
        return rate_constant
    # Pattern 3 example: 23.2x10^-6(mol)
    # Pattern 4 example: 0.76(second -1)
    # Pattern 5 example: 1.9x10^6 ~0.03(per mole per second)

    print('Could not parse %s' % value)
    return None

def parse_entry(entry):
    parts = entry.split('|')
    rates = {}
    for part in parts:
        prefix, value = part.split(':')
        rate_constant = parse_value(value)
        if rate_constant is not None:
            rates[prefix] = rate_constant
    return rates


if __name__ == '__main__':
    with open('parameters.json', 'r') as fh:
        all_entries = json.load(fh)
    prefixes = set()
    for entry in all_entries:
        rates = parse_entry(entry)
        if rates:
            print(rates)
