from datetime import datetime
import data_structures

class Database:
    """Database Engine with DDL, DML, Constraint Enforcement, and Aggregates"""
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.tables = {}
        self.indexes = {} 
        self.created_at = datetime.now().isoformat()
        
    def create_table(self, table_name, columns_data):
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists")
        
        column_names = [col['name'] for col in columns_data]
        pk_column = None
        for col in columns_data:
            if col['constraints']['primary_key']:
                if pk_column: raise ValueError("Multiple primary keys defined")
                pk_column = col['name']
        
        if not pk_column:
            pk_column = column_names[0]
            columns_data[0]['constraints']['primary_key'] = True

        self.tables[table_name] = {
            'columns': column_names, 
            'column_definitions': columns_data, 
            'primary_key': pk_column,
            'records': [],
            'created_at': datetime.now().isoformat()
        }
        
        self.indexes[table_name] = data_structures.HashTable()
        return f"Table '{table_name}' created successfully"
    
    def drop_table(self, table_name):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        del self.tables[table_name]
        del self.indexes[table_name]
        return f"Table '{table_name}' dropped successfully"

    def truncate_table(self, table_name):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        self.tables[table_name]['records'] = []
        self.indexes[table_name] = data_structures.HashTable()
        return f"Table '{table_name}' truncated successfully"
    
    def alter_table(self, table_name, column_def):
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        new_col_name = column_def['name']
        
        if new_col_name in table['columns']:
            raise ValueError(f"Column '{new_col_name}' already exists")

        constraints = column_def['constraints']
        default_val = constraints['default']

        if table['records']:
            if constraints['not_null'] and default_val is None:
                raise ValueError(f"Cannot add NOT NULL column '{new_col_name}' to non-empty table without DEFAULT")
            if constraints['unique'] and len(table['records']) > 1:
                 raise ValueError(f"Cannot add UNIQUE column '{new_col_name}' to table with multiple records")

        table['columns'].append(new_col_name)
        table['column_definitions'].append(column_def)

        for record in table['records']:
            record[new_col_name] = default_val

        return f"Table '{table_name}' altered. Added column '{new_col_name}'."
    
    def describe_table(self, table_name):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        table = self.tables[table_name]
        
        output = [f"--- Table: {table_name} ---"]
        output.append(f"{'Column':<15} | {'Type':<10} | {'Constraints'}")
        output.append("-" * 60)
        
        for col in table['column_definitions']:
            cons = []
            c = col['constraints']
            if c['primary_key']: cons.append("PK")
            if c['not_null']: cons.append("NOT NULL")
            if c['unique']: cons.append("UNIQUE")
            if c['default'] is not None: cons.append(f"DEFAULT {c['default']}")
            if c['check']: cons.append(f"CHECK({c['check']})")
            if c['foreign_key']: cons.append(f"FK->{c['foreign_key']['table']}({c['foreign_key']['column']})")
            
            cons_str = ", ".join(cons) if cons else ""
            output.append(f"{col['name']:<15} | {col['type']:<10} | {cons_str}")
            
        return '\n'.join(output)

    def insert_record(self, table_name, values, check_foreign_keys_callback=None):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        col_defs = table['column_definitions']
        
        if len(values) != len(col_defs):
            raise ValueError(f"Column count mismatch. Expected {len(col_defs)}, got {len(values)}")
        
        record = dict(zip(table['columns'], values))
        
        for col_def in col_defs:
            name = col_def['name']
            val = record[name]
            cons = col_def['constraints']
            
            if val is None or val == '':
                if cons['default'] is not None:
                    record[name] = cons['default']
                    val = cons['default']

            if cons['not_null'] and (val is None or val == ''):
                raise ValueError(f"Constraint Violation: Column '{name}' cannot be NULL")

            if cons['primary_key'] or cons['unique']:
                for existing in table['records']:
                    if str(existing.get(name)) == str(val):
                        ctype = "Primary Key" if cons['primary_key'] else "Unique"
                        raise ValueError(f"{ctype} Constraint Violation: Duplicate value '{val}' for column '{name}'")

            if cons['check']:
                try:
                    condition = cons['check'].replace(name, str(val))
                    if not eval(condition, {"__builtins__": None}, {}):
                         raise ValueError(f"Check Constraint Violation: Value '{val}' failed condition '{cons['check']}'")
                except Exception:
                     pass

            if cons['foreign_key'] and check_foreign_keys_callback:
                ref_table = cons['foreign_key']['table']
                ref_col = cons['foreign_key']['column']
                if not check_foreign_keys_callback(ref_table, ref_col, val):
                     raise ValueError(f"Foreign Key Violation: Value '{val}' not found in {ref_table}({ref_col})")

        record['_created_at'] = datetime.now().isoformat()
        record['_updated_at'] = datetime.now().isoformat()
        
        pk_val = record[table['primary_key']]
        table['records'].append(record)
        self.indexes[table_name].insert(pk_val, record)
        
        return "Record inserted successfully"
    
    def select_records(self, table_name, where_clause=None, order_by=None, limit=None):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        records = self.tables[table_name]['records']
        if where_clause:
            records = [r for r in records if self._evaluate_where(r, where_clause)]
        if order_by:
            col, direction = order_by
            records = sorted(records, key=lambda x: str(x.get(col, '')), reverse=(direction == 'DESC'))
        if limit:
            records = records[:limit]
        return records

    def execute_aggregate(self, table_name, function, column, where_clause=None, group_by=None):
        """Execute aggregate functions: COUNT, SUM, AVG, MIN, MAX with optional GROUP BY"""
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        
        records = self.tables[table_name]['records']
        if where_clause:
            records = [r for r in records if self._evaluate_where(r, where_clause)]

        # --- Grouping Logic ---
        groups = {}
        if group_by:
            if group_by not in self.tables[table_name]['columns']:
                raise ValueError(f"Unknown column '{group_by}' in GROUP BY")
            
            for r in records:
                key = r.get(group_by)
                if key not in groups: groups[key] = []
                groups[key].append(r)
        else:
            groups['ALL'] = records

        # --- Aggregation Logic ---
        results = []
        for key, group_records in groups.items():
            val = 0
            
            if function == 'COUNT':
                val = len(group_records)
            
            elif function in ('SUM', 'AVG', 'MIN', 'MAX'):
                if column is None: raise ValueError(f"{function} requires a column name")
                
                # Extract numeric values
                values = []
                for r in group_records:
                    v = r.get(column)
                    try:
                        values.append(float(v))
                    except (ValueError, TypeError):
                        continue # Skip non-numeric for math ops
                
                if not values:
                    val = 0 if function == 'SUM' else None
                else:
                    if function == 'SUM': val = sum(values)
                    elif function == 'AVG': val = sum(values) / len(values)
                    elif function == 'MIN': val = min(values)
                    elif function == 'MAX': val = max(values)
            
            # Format result
            row = {}
            if group_by:
                row[group_by] = key
            
            # Create a nice label like "SUM(salary)"
            col_label = f"{function}({column if column else '*'})"
            row[col_label] = val
            results.append(row)

        return results
    
    def update_records(self, table_name, set_clause, where_clause):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        records = self.tables[table_name]['records']
        updated_count = 0
        for record in records:
            if self._evaluate_where(record, where_clause):
                for col, val in set_clause.items():
                    record[col] = val
                record['_updated_at'] = datetime.now().isoformat()
                updated_count += 1
        return f"{updated_count} record(s) updated"
    
    def delete_records(self, table_name, where_clause):
        if table_name not in self.tables: raise ValueError(f"Table '{table_name}' does not exist")
        records = self.tables[table_name]['records']
        initial_len = len(records)
        remaining = [r for r in records if not self._evaluate_where(r, where_clause)]
        self.tables[table_name]['records'] = remaining
        self.indexes[table_name] = data_structures.HashTable()
        for r in remaining:
            pk = r[self.tables[table_name]['primary_key']]
            self.indexes[table_name].insert(pk, r)
        return f"{initial_len - len(remaining)} record(s) deleted"
    
    def _evaluate_where(self, record, where_clause):
        for col, op, val in where_clause:
            r_val = record.get(col)
            try:
                v1, v2 = float(r_val), float(val)
            except:
                v1, v2 = str(r_val), str(val)
            if op == '=' and not (v1 == v2): return False
            if op == '!=' and not (v1 != v2): return False
            if op == '>' and not (v1 > v2): return False
            if op == '<' and not (v1 < v2): return False
            if op == '>=' and not (v1 >= v2): return False
            if op == '<=' and not (v1 <= v2): return False
        return True

    def to_dict(self):
        return {'name': self.name, 'owner': self.owner, 'tables': self.tables, 'created_at': self.created_at}

    @staticmethod
    def from_dict(data):
        db = Database(data['name'], data['owner'])
        db.tables = data.get('tables', {})
        db.created_at = data.get('created_at', datetime.now().isoformat())
        for t_name, t_data in db.tables.items():
            db.indexes[t_name] = data_structures.HashTable()
            pk = t_data.get('primary_key', t_data['columns'][0])
            for r in t_data['records']:
                db.indexes[t_name].insert(r[pk], r)
        return db