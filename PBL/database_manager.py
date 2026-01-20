import json
import hashlib
import os
from datetime import datetime
import csv
import database
import query_parser

class DatabaseManager:
    """Manages databases, users, and transactions"""
    def __init__(self, data_dir='structdb_data'):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.databases = {}
        self.users = {}
        self.current_user = None
        self.current_database = None
        self.query_history = []
        self.in_transaction = False
        
        os.makedirs(data_dir, exist_ok=True)
        self.load_users()
        self.load_databases()

    def _auto_save(self):
        # Only save to disk if NOT in a transaction
        if not self.in_transaction and self.current_database:
            self.save_database(self.current_database)

    def check_fk_exists(self, table_name, column_name, value):
        db = self.get_current_database()
        if table_name not in db.tables: return False
        records = db.tables[table_name]['records']
        for r in records:
            if str(r.get(column_name)) == str(value):
                return True
        return False

    def grant_role(self, user, role):
        if self.users[self.current_user]['role'] != 'admin':
            raise PermissionError("Only Admins can GRANT roles")
        if user not in self.users:
            raise ValueError(f"User '{user}' does not exist")
        self.users[user]['role'] = role
        self.save_users()
        return f"Granted role '{role}' to user '{user}'"

    def revoke_role(self, user):
        if self.users[self.current_user]['role'] != 'admin':
            raise PermissionError("Only Admins can REVOKE roles")
        if user not in self.users:
            raise ValueError(f"User '{user}' does not exist")
        self.users[user]['role'] = 'user' 
        self.save_users()
        return f"Revoked roles from '{user}'"

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        if username in self.users: raise ValueError("User exists")
        self.users[username] = {'password': self.hash_password(password), 'role': 'user', 'databases': []}
        self.save_users()
        return "Registered"

    def login(self, username, password):
        if username not in self.users or self.users[username]['password'] != self.hash_password(password):
            raise ValueError("Invalid credentials")
        self.current_user = username
        self.load_databases()
    
    def logout(self):
        if self.in_transaction: 
            self.execute_query("ROLLBACK")
        self.current_user = None
        self.current_database = None

    def execute_query(self, query):
        if not self.current_user: raise ValueError("Login required")
        
        try:
            parsed = query_parser.QueryParser.parse(query)
            self.query_history.append({'query': query, 'timestamp': datetime.now().isoformat()})
            q_type = parsed['type']

            # --- Transaction Management ---
            if q_type == 'START_TRANSACTION':
                if self.in_transaction: return "Transaction already active"
                self.in_transaction = True
                return "Transaction started. Auto-save disabled."
            
            elif q_type == 'COMMIT':
                if not self.in_transaction: return "No active transaction"
                self.in_transaction = False
                self.save_database(self.current_database) # Persist changes
                return "Transaction committed."
            
            elif q_type == 'ROLLBACK':
                if not self.in_transaction: return "No active transaction"
                self.in_transaction = False
                if self.current_database: 
                    # Revert by reloading the last saved state from disk
                    self._load_single_database(self.current_database) 
                return "Transaction rolled back."

            elif q_type == 'GRANT': return self.grant_role(parsed['user'], parsed['role'])
            elif q_type == 'REVOKE': return self.revoke_role(parsed['user'])

            elif q_type == 'CREATE_DATABASE': return self.create_database(parsed['database'])
            elif q_type == 'USE_DATABASE': return self.use_database(parsed['database'])
            elif q_type == 'SHOW_DATABASES': return self.list_databases_str()
            elif q_type == 'DROP_DATABASE': return self.drop_database(parsed['database'])

            # Database operations requiring a selected DB
            db = self.get_current_database()
            
            if q_type == 'CREATE_TABLE':
                res = db.create_table(parsed['table'], parsed['columns'])
                self._auto_save()
                return res
            elif q_type == 'ALTER_TABLE':
                res = db.alter_table(parsed['table'], parsed['column_def'])
                self._auto_save()
                return res
            elif q_type == 'TRUNCATE_TABLE':
                res = db.truncate_table(parsed['table'])
                self._auto_save()
                return res
            elif q_type == 'DROP_TABLE':
                res = db.drop_table(parsed['table'])
                self._auto_save()
                return res
            elif q_type == 'DESCRIBE_TABLE':
                return db.describe_table(parsed['table'])
            elif q_type == 'SHOW_TABLES':
                return "\n".join(db.tables.keys()) if db.tables else "No tables"

            elif q_type == 'INSERT':
                if 'values_list' in parsed:
                    count = 0
                    errors = []
                    for vals in parsed['values_list']:
                        try:
                            db.insert_record(parsed['table'], vals, self.check_fk_exists)
                            count += 1
                        except Exception as e:
                            errors.append(str(e))
                    self._auto_save()
                    return f"Inserted {count} records. Errors: {len(errors)}"
            
            elif q_type == 'SELECT':
                return db.select_records(parsed['table'], parsed['where'], parsed['order_by'], parsed['limit'])
            
            # --- NEW AGGREGATE HANDLER ---
            elif q_type == 'AGGREGATE':
                return db.execute_aggregate(
                    parsed['table'], 
                    parsed['function'], 
                    parsed['column'], 
                    parsed['where'],
                    parsed['group_by']
                )

            elif q_type == 'UPDATE':
                res = db.update_records(parsed['table'], parsed['set'], parsed['where'])
                self._auto_save()
                return res
            elif q_type == 'DELETE':
                res = db.delete_records(parsed['table'], parsed['where'])
                self._auto_save()
                return res
            return "Unknown query"

        except Exception as e:
            raise e

    def create_database(self, db_name):
        full = f"{self.current_user}_{db_name}"
        if full in self.databases: raise ValueError("DB exists")
        self.databases[full] = {'database': database.Database(db_name, self.current_user), 'owner': self.current_user, 'password_hash': None}
        self.users[self.current_user]['databases'].append(full)
        self.save_database(full)
        self.save_users()
        return "Database created"

    def use_database(self, db_name):
        full = f"{self.current_user}_{db_name}"
        if full not in self.databases: self._load_single_database(full)
        if full not in self.databases: raise ValueError("Database not found")
        self.current_database = full
        return f"Switched to {db_name}"

    def get_current_database(self):
        if not self.current_database: raise ValueError("No DB selected")
        return self.databases[self.current_database]['database']

    def drop_database(self, db_name):
        full = f"{self.current_user}_{db_name}"
        if full in self.databases: del self.databases[full]
        if full in self.users[self.current_user]['databases']:
            self.users[self.current_user]['databases'].remove(full)
        path = os.path.join(self.data_dir, f"{full}.json")
        if os.path.exists(path): os.remove(path)
        self.save_users()
        return "Dropped"

    def list_databases(self):
        """Return list of databases for current user (for GUI)"""
        if not self.current_user:
            return []
        dbs = self.users[self.current_user]['databases']
        return [d.split('_', 1)[1] for d in dbs]

    def list_databases_str(self):
        """Return databases as string (for query mode)"""
        dbs = self.list_databases()
        return "\n".join(dbs) if dbs else "No databases"

    def save_users(self):
        with open(self.users_file, 'w') as f: json.dump(self.users, f, indent=2)

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file) as f: self.users = json.load(f)
        else:
            self.users = {'admin': {'password': self.hash_password('admin123'), 'role': 'admin', 'databases': []}}
            self.save_users()

    def save_database(self, full_name):
        path = os.path.join(self.data_dir, f"{full_name}.json")
        data = {
            'database': self.databases[full_name]['database'].to_dict(),
            'owner': self.databases[full_name]['owner'],
            'password_hash': self.databases[full_name]['password_hash']
        }
        with open(path, 'w') as f: json.dump(data, f, indent=2)

    def _load_single_database(self, full_name):
        path = os.path.join(self.data_dir, f"{full_name}.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                self.databases[full_name] = {
                    'database': database.Database.from_dict(data['database']),
                    'owner': data['owner'],
                    'password_hash': data.get('password_hash')
                }

    def load_databases(self):
        if self.current_user:
            for db in self.users[self.current_user]['databases']:
                self._load_single_database(db)
    
    def export_to_csv(self, table_name, filename):
        db = self.get_current_database()
        if table_name not in db.tables: raise ValueError("Table not found")
        records = db.select_records(table_name)
        if not records: raise ValueError("No records")
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', newline='') as f:
             writer = csv.DictWriter(f, fieldnames=records[0].keys())
             writer.writeheader()
             writer.writerows(records)
        return "Exported"