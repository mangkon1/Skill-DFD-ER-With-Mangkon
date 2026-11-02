# -*- coding: utf-8 -*-
"""Generate MariaDB DDL from the Data Dictionary JSON (same file used for the report tables), so DD = ER = SQL.
Usage: python dd_to_sql.py ../dd/dd_spare_part.json > schema_mariadb.sql
Rules: PK -> PRIMARY KEY (int PK = AUTO_INCREMENT, varchar PK = natural code); Unique=Yes (not PK) -> UNIQUE;
FK -> FOREIGN KEY to the PK of 'references'; tables are emitted parents-first; utf8mb4 + InnoDB."""
import sys, json
def coltype(c):
    t = c['type'].lower(); s = c.get('size', '')
    if t in ('varchar', 'char', 'decimal') and s: return '%s(%s)' % (t.upper(), s)
    return {'int': 'INT', 'tinyint': 'TINYINT(1)', 'date': 'DATE', 'datetime': 'DATETIME', 'text': 'TEXT'}.get(t, t.upper())
def main(path):
    D = json.load(open(path, encoding='utf-8')); T = {t['table']: t for t in D['tables']}
    pk = {n: [c['name'] for c in t['columns'] if c['key'] == 'PK'][0] for n, t in T.items()}
    order, seen = [], set()
    def visit(n, stack=()):
        if n in seen: return
        for c in T[n]['columns']:
            r = c.get('references')
            if c['key'] == 'FK' and r and r != n and r not in stack: visit(r, stack + (n,))
        seen.add(n); order.append(n)
    for n in T: visit(n)
    out = ['-- Generated from the Data Dictionary (%d tables). MariaDB 10.6+' % len(T), 'SET NAMES utf8mb4;', '']
    for n in order:
        t = T[n]; lines = []
        for c in t['columns']:
            s = '  `%s` %s' % (c['name'], coltype(c))
            s += ' NOT NULL' if c['not_null'] == 'Yes' else ' NULL'
            if c['key'] == 'PK' and c['type'].lower() == 'int': s += ' AUTO_INCREMENT'
            s += " COMMENT '%s'" % c['description'].replace("'", "''")
            lines.append(s)
        lines.append('  PRIMARY KEY (`%s`)' % pk[n])
        for c in t['columns']:
            if c['unique'] == 'Yes' and c['key'] != 'PK': lines.append('  UNIQUE KEY `uq_%s_%s` (`%s`)' % (n, c['name'], c['name']))
        for c in t['columns']:
            if c['key'] == 'FK':
                r = c['references']
                lines.append('  CONSTRAINT `fk_%s_%s` FOREIGN KEY (`%s`) REFERENCES `%s` (`%s`)' % (n, c['name'], c['name'], r, pk[r]))
        out.append("-- %s: %s" % (t['no'], t['title_th']))
        out.append('CREATE TABLE `%s` (\n%s\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n' % (n, ',\n'.join(lines)))
    print('\n'.join(out))
if __name__ == '__main__': main(sys.argv[1])
