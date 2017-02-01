from __future__ import absolute_import, print_function, unicode_literals
from builtins import dict, str
import re
import json
import pandas
from sympy.physics import units
from indra.statements import Agent, Complex, Evidence
from indra.databases import uniprot_client, hgnc_client

M = units.moles / units.liter
mol = units.moles
second = units.second

def read_table():
    fname = '../resources/intact.csv'
    df = pandas.read_csv(fname, index_col=None)
    return df

def parse_value(value):
    # Kd
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
        num, exponent = res.groups()
        rate_constant = float(num) * 10**float(exponent) * M
        return rate_constant
    # Pattern 3 example: 23.2x10^-6(mol)
    # 'mol' unit is incorrect and changed to M
    pattern = r'([0-9]+\.[0-9]+)x10\^([-]?[^ ]+)\(mol\)'
    res = re.match(pattern, value)
    if res:
        num, exponent = res.groups()
        rate_constant = float(num) * 10**float(exponent) * M
        return rate_constant
    # Pattern 4 example: 0.76(second -1)
    pattern = r'(\d+\.\d*)\(second -1\)'
    res = re.match(pattern, value)
    if res:
        num = res.groups()[0]
        rate_constant = float(num) / second
        return rate_constant
    # Pattern 5 example: 4.1x10^-2 ~0.03(second -1)
    pattern = r'([0-9]+\.[0-9]+)x10\^([-]?[^ ]+)\s~\d+.{0,1}\d*\(second -1\)'
    res = re.match(pattern, value)
    if res:
        num, exponent = res.groups()
        rate_constant = (float(num) * 10**float(exponent)) / second
        return rate_constant
    # Pattern  example: 4.1x10^-2 ~0.03(second -1)
    pattern = r'([0-9]+\.[0-9]+)x10\^([-]?[^ ]+)\s~\d+.{0,1}\d*\(per mole per second\)'
    res = re.match(pattern, value)
    if res:
        num, exponent = res.groups()
        rate_constant = (float(num) * 10**float(exponent)) / (mol * second)
        return rate_constant

    print('Could not parse %s' % value)
    return None

def get_agent_from_up(up_id):
    gene_name = uniprot_client.get_gene_name(up_id)
    if not gene_name:
        return None
    db_refs = {'UP': up_id}
    if uniprot_client.is_human(up_id):
        hgnc_id = hgnc_client.get_hgnc_id(gene_name)
        if hgnc_id:
            db_refs['HGNC'] = hgnc_id
    agent = Agent(gene_name, db_refs=db_refs)
    return agent

def parse_entry(entry):
    parts = entry.split('|')
    rates = {}
    for part in parts:
        prefix, value = part.split(':')
        rate_constant = parse_value(value)
        if rate_constant is not None:
            rates[prefix] = rate_constant
    return rates

def get_complexes(df):
    stmts = []
    for _, row in df.iterrows():
        a = row['#ID(s) interactor A'].decode('utf-8')
        b = row['ID(s) interactor B'].decode('utf-8')
        params = row['Interaction parameter(s)']
        if params != '-':
            rates = parse_entry(params)
        else:
            rates = {}
        if a.startswith('uniprotkb:'):
            a_id = a[10:].split('-')[0]
        else:
            continue
        if b.startswith('uniprotkb:'):
            b_id = b[10:].split('-')[0]
        else:
            continue
        agent_a = get_agent_from_up(a_id)
        agent_b = get_agent_from_up(b_id)
        ev = Evidence(source_api='intact')
        if rates:
            ev.annotations = {'kinetics': rates}
        if agent_a is None or agent_b is None:
            continue
        st = Complex([agent_a, agent_b], evidence=[ev])
        stmts.append(st)
    return stmts

if __name__ == '__main__':
    df = read_table()
    stmts = get_complexes(df)
