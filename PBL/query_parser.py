import re

class QueryParser:
    """SQL-like query parser with support for DDL, DML, TCL, DCL and Constraints"""
    
    @staticmethod
    def parse(query):
        """Parse SQL-like query"""
        query = query.strip().rstrip(';')
        
        # --- TCL COMMANDS ---
        if query.upper() in ('START TRANSACTION', 'BEGIN'):
            return {'type': 'START_TRANSACTION'}
        if query.upper() == 'COMMIT':
            return {'type': 'COMMIT'}
        if query.upper() == 'ROLLBACK':
            return {'type': 'ROLLBACK'}

        # --- DCL COMMANDS ---
        if query.upper().startswith('GRANT'):
            match = re.match(r'GRANT\s+(\w+)\s+TO\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'GRANT', 'role': match.group(1), 'user': match.group(2)}
        
        if query.upper().startswith('REVOKE'):
            match = re.match(r'REVOKE\s+(\w+)\s+FROM\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'REVOKE', 'role': match.group(1), 'user': match.group(2)}

        # --- DDL COMMANDS ---
        if query.upper().startswith('CREATE DATABASE'):
            match = re.match(r'CREATE DATABASE\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'CREATE_DATABASE', 'database': match.group(1)}
        
        if query.upper().startswith('DROP DATABASE'):
            match = re.match(r'DROP DATABASE\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'DROP_DATABASE', 'database': match.group(1)}
        
        if query.upper().startswith('USE'):
            match = re.match(r'USE\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'USE_DATABASE', 'database': match.group(1)}
        
        if re.match(r'SHOW\s+DATABASES', query, re.IGNORECASE):
            return {'type': 'SHOW_DATABASES'}
        
        if re.match(r'SHOW\s+TABLES', query, re.IGNORECASE):
            return {'type': 'SHOW_TABLES'}
        
        if query.upper().startswith(('DESC ', 'DESCRIBE ')):
            match = re.match(r'(?:DESCRIBE|DESC)\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'DESCRIBE_TABLE', 'table': match.group(1)}
        
        # CREATE TABLE
        if query.upper().startswith('CREATE TABLE'):
            match = re.match(r'CREATE TABLE\s+(\w+)\s*\((.*)\)', query, re.IGNORECASE | re.DOTALL)
            if match:
                table_name = match.group(1)
                columns_str = match.group(2)
                columns_data = QueryParser._parse_column_definitions(columns_str)
                if not columns_data:
                    raise ValueError("CREATE TABLE must define at least one column.")
                return {'type': 'CREATE_TABLE', 'table': table_name, 'columns': columns_data}
        
        # DROP TABLE
        if query.upper().startswith('DROP TABLE'):
            match = re.match(r'DROP TABLE\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'DROP_TABLE', 'table': match.group(1)}
        
        # TRUNCATE TABLE
        if query.upper().startswith('TRUNCATE TABLE'):
            match = re.match(r'TRUNCATE TABLE\s+(\w+)', query, re.IGNORECASE)
            if match:
                return {'type': 'TRUNCATE_TABLE', 'table': match.group(1)}

        # ALTER TABLE (ADD COLUMN)
        if query.upper().startswith('ALTER TABLE'):
            match = re.match(r'ALTER TABLE\s+(\w+)\s+ADD\s+(.+)', query, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                col_def_str = match.group(2)
                column_def = QueryParser._parse_single_column(col_def_str)
                return {'type': 'ALTER_TABLE', 'table': table_name, 'column_def': column_def}
        
        # --- DML COMMANDS ---
        if query.upper().startswith('INSERT'):
            return QueryParser._parse_insert(query)
        if query.upper().startswith('SELECT'):
            return QueryParser._parse_select(query)
        if query.upper().startswith('UPDATE'):
            return QueryParser._parse_update(query)
        if query.upper().startswith('DELETE'):
            return QueryParser._parse_delete(query)
        
        raise ValueError("Invalid query syntax")
    
    @staticmethod
    def _parse_insert(query):
        match = re.match(r'INSERT\s+INTO\s+(\w+)\s+VALUES\s*(.+)', query, re.IGNORECASE | re.DOTALL)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        table_name = match.group(1)
        values_section = match.group(2).strip()
        all_values = QueryParser._parse_multiple_value_sets(values_section)
        if not all_values:
            raise ValueError("No values provided for INSERT")
        return {'type': 'INSERT', 'table': table_name, 'values_list': all_values}
    
    @staticmethod
    def _parse_multiple_value_sets(values_section):
        all_values = []
        current_set = ''
        paren_level = 0
        in_quotes = False
        quote_char = None
        for char in values_section:
            if char in ('"', "'") and (quote_char is None or quote_char == char):
                if in_quotes and quote_char == char:
                    in_quotes = False
                    quote_char = None
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
            if not in_quotes:
                if char == '(':
                    paren_level += 1
                    if paren_level == 1:
                        current_set = ''
                        continue
                elif char == ')':
                    paren_level -= 1
                    if paren_level == 0:
                        if current_set.strip():
                            values = QueryParser._parse_values(current_set)
                            all_values.append(values)
                        current_set = ''
                        continue
                elif char == ',' and paren_level == 0:
                    continue
            if paren_level > 0:
                current_set += char
        return all_values
    
    @staticmethod
    def _parse_select(query):
        # Improved Regex to handle SELECT col, AGG(col) FROM ... GROUP BY col
        # Capture groups: 1=OptCol, 2=Func, 3=AggCol, 4=Table, 5=Where, 6=GroupBy, 7=Order, 8=Limit
        agg_match = re.match(r'SELECT\s+(?:(\w+)\s*,\s*)?(COUNT|SUM|AVG|MIN|MAX)\((\*|\w+)\)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?(?:\s+GROUP\s+BY\s+(\w+))?(?:\s+ORDER\s+BY\s+(.+?))?(?:\s+LIMIT\s+(\d+))?$', query, re.IGNORECASE | re.DOTALL)
        
        if agg_match:
            leading_col, function, column, table, where_str, group_by_col, order_str, limit_str = agg_match.groups()
            
            where_clause = QueryParser._parse_where(where_str) if where_str else None
            
            return {
                'type': 'AGGREGATE', 
                'function': function.upper(), 
                'column': column if column != '*' else None, 
                'table': table, 
                'where': where_clause,
                'group_by': group_by_col
            }

        # Standard SELECT (Fallback)
        match = re.match(r'SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+?))?(?:\s+ORDER\s+BY\s+(.+?))?(?:\s+LIMIT\s+(\d+))?$', query, re.IGNORECASE | re.DOTALL)
        if match:
            columns_str, table, where_str, order_str, limit_str = match.groups()
            columns = [col.strip() for col in columns_str.split(',')] if columns_str != '*' else None
            where_clause = QueryParser._parse_where(where_str) if where_str else None
            order_by = QueryParser._parse_order_by(order_str) if order_str else None
            limit = int(limit_str) if limit_str else None
            return {'type': 'SELECT', 'columns': columns, 'table': table, 'where': where_clause, 'order_by': order_by, 'limit': limit}
        
        raise ValueError("Invalid SELECT syntax")
    
    @staticmethod
    def _parse_update(query):
        match = re.match(r'UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+?)$', query, re.IGNORECASE | re.DOTALL)
        if match:
            table, set_str, where_str = match.groups()
            set_clause = QueryParser._parse_set(set_str)
            where_clause = QueryParser._parse_where(where_str)
            return {'type': 'UPDATE', 'table': table, 'set': set_clause, 'where': where_clause}
        raise ValueError("Invalid UPDATE syntax - missing WHERE clause")
    
    @staticmethod
    def _parse_delete(query):
        match = re.match(r'DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.+?)$', query, re.IGNORECASE | re.DOTALL)
        if match:
            table, where_str = match.groups()
            where_clause = QueryParser._parse_where(where_str)
            return {'type': 'DELETE', 'table': table, 'where': where_clause}
        raise ValueError("Invalid DELETE syntax - missing WHERE clause")
    
    @staticmethod
    def _parse_where(where_str):
        if not where_str: return None
        conditions = []
        parts = re.split(r'\s+AND\s+', where_str.strip(), flags=re.IGNORECASE)
        for part in parts:
            match = re.match(r'(\w+)\s*(=|!=|>|<|>=|<=)\s*(.+)', part.strip())
            if match:
                column, operator, value = match.groups()
                value = QueryParser._clean_value(value.strip())
                conditions.append((column, operator, value))
        return conditions
    
    @staticmethod
    def _parse_set(set_str):
        set_clause = {}
        parts = re.split(r',\s*(?=\w+\s*=)', set_str.strip())
        for part in parts:
            match = re.match(r'(\w+)\s*=\s*(.+)', part.strip())
            if match:
                column, value = match.groups()
                set_clause[column] = QueryParser._clean_value(value.strip())
        return set_clause
    
    @staticmethod
    def _parse_order_by(order_str):
        match = re.match(r'(\w+)\s*(ASC|DESC)?', order_str.strip(), re.IGNORECASE)
        if match:
            column, direction = match.groups()
            return (column, direction.upper() if direction else 'ASC')
        return None

    @staticmethod
    def _parse_column_definitions(columns_str):
        definitions = []
        current_def = ''
        paren_level = 0
        for char in columns_str:
            if char == '(': paren_level += 1
            elif char == ')': paren_level -= 1
            if char == ',' and paren_level == 0:
                if current_def.strip():
                    definitions.append(QueryParser._parse_single_column(current_def.strip()))
                current_def = ''
            else:
                current_def += char
        if current_def.strip():
            definitions.append(QueryParser._parse_single_column(current_def.strip()))
        return definitions

    @staticmethod
    def _parse_single_column(col_def_str):
        parts = col_def_str.split(None, 1)
        name = parts[0]
        rest = parts[1] if len(parts) > 1 else 'TEXT'
        constraints = {
            'primary_key': False, 'not_null': False, 'unique': False,
            'default': None, 'check': None, 'foreign_key': None
        }
        if re.search(r'\bPRIMARY KEY\b', rest, re.IGNORECASE):
            constraints['primary_key'] = True
            rest = re.sub(r'\bPRIMARY KEY\b', '', rest, flags=re.IGNORECASE)
        if re.search(r'\bNOT NULL\b', rest, re.IGNORECASE):
            constraints['not_null'] = True
            rest = re.sub(r'\bNOT NULL\b', '', rest, flags=re.IGNORECASE)
        if re.search(r'\bUNIQUE\b', rest, re.IGNORECASE):
            constraints['unique'] = True
            rest = re.sub(r'\bUNIQUE\b', '', rest, flags=re.IGNORECASE)
        default_match = re.search(r'\bDEFAULT\s+([^\s]+)', rest, re.IGNORECASE)
        if default_match:
            val = default_match.group(1)
            constraints['default'] = QueryParser._clean_value(val)
            rest = re.sub(r'\bDEFAULT\s+[^\s]+', '', rest, flags=re.IGNORECASE)
        check_match = re.search(r'\bCHECK\s*\((.*?)\)', rest, re.IGNORECASE)
        if check_match:
            constraints['check'] = check_match.group(1)
            rest = re.sub(r'\bCHECK\s*\(.*?\)', '', rest, flags=re.IGNORECASE)
        fk_match = re.search(r'\bREFERENCES\s+(\w+)\s*\((\w+)\)', rest, re.IGNORECASE)
        if fk_match:
            constraints['foreign_key'] = {'table': fk_match.group(1), 'column': fk_match.group(2)}
            rest = re.sub(r'\bREFERENCES\s+\w+\s*\(\w+\)', '', rest, flags=re.IGNORECASE)
        data_type = rest.strip()
        if not data_type: data_type = 'TEXT'
        return {'name': name, 'definition': col_def_str, 'type': data_type, 'constraints': constraints}

    @staticmethod
    def _parse_values(values_str):
        values = []
        current = ''
        in_quotes = False
        quote_char = None
        for char in values_str:
            if char in ('"', "'") and (quote_char is None or quote_char == char):
                if in_quotes and quote_char == char:
                    in_quotes = False
                    quote_char = None
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
                continue
            elif char == ',' and not in_quotes:
                if current.strip(): values.append(QueryParser._clean_value(current.strip()))
                current = ''
                continue
            current += char
        if current.strip(): values.append(QueryParser._clean_value(current.strip()))
        return values
    
    @staticmethod
    def _clean_value(value):
        value = str(value).strip()
        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            return value[1:-1]
        if value.upper() == 'NULL': return None
        try:
            if '.' in value: return float(value)
            return int(value)
        except ValueError:
            return value