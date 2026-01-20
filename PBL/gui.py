"""
gui.py
Tkinter-based GUI for StructDB - COMPLETE FIXED VERSION WITH AUTO-REFRESH INFO
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import database_manager


class StructDBGUI:
    """Main GUI application"""
    def __init__(self, root):
        self.root = root
        self.root.title("StructDB - Mini Database Engine")
        self.root.geometry("1200x700")
        
        self.db_manager = database_manager.DatabaseManager()
        self.current_table = None
        
        self.set_theme()
        
        self.show_login_screen()
    
    def set_theme(self):
        """Configure the black and white theme"""
        style = ttk.Style()

        # Define colors
        self.bg_dark = "#000000"
        self.fg_white = "#FFFFFF"
        self.fg_grey = "#2FFF00"
        self.bg_light_dark = "#000000"

        style.theme_use('clam')
        self.root.configure(bg=self.bg_dark)

        # General style
        style.configure('TFrame', background=self.bg_dark)
        style.configure('TLabel', background=self.bg_dark, foreground=self.fg_grey, font=('Consolas', 10))
        style.configure('TLabelframe', background=self.bg_dark, foreground=self.fg_grey, font=('Consolas', 10, 'bold'), bordercolor=self.fg_grey, relief="solid", borderwidth=1)
        style.configure('TLabelframe.Label', background=self.bg_dark, foreground=self.fg_white)

        # Entry fields
        style.configure('TEntry', fieldbackground=self.bg_light_dark, foreground=self.fg_white, insertbackground=self.fg_white, bordercolor=self.fg_grey)
        style.map('TEntry', fieldbackground=[('focus', '#555555')])

        # Buttons
        style.configure('TButton', background=self.bg_light_dark, foreground=self.fg_white, font=('Consolas', 10, 'bold'), borderwidth=1, relief="solid", bordercolor=self.fg_grey)
        style.map('TButton', background=[('active', self.fg_white)], foreground=[('active', self.bg_dark)], relief=[('pressed', 'sunken'), ('!pressed', 'ridge')])

        # Combobox
        style.configure('TCombobox', fieldbackground=self.bg_light_dark, foreground=self.fg_white, selectbackground="#555555", selectforeground=self.fg_white, background=self.bg_light_dark)
        style.map('TCombobox', fieldbackground=[('focus', '#555555')], background=[('active', '#555555')])
        
        # Notebook (tabs)
        style.configure('TNotebook', background=self.bg_dark, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.bg_light_dark, foreground=self.fg_grey, font=('Consolas', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', self.bg_dark), ('active', '#555555')], foreground=[('selected', self.fg_white), ('active', self.fg_white)])

        # PanedWindow
        style.configure('TPanedwindow', background=self.bg_dark)

        # Treeview
        style.configure('Treeview', background=self.bg_light_dark, foreground=self.fg_grey, fieldbackground=self.bg_light_dark, bordercolor=self.fg_grey)
        style.configure('Treeview.Heading', background="#555555", foreground=self.fg_white, font=('Consolas', 10, 'bold'), borderwidth=1, relief="raised")
        style.map('Treeview.Heading', background=[('active', '#777777')])
        style.map('Treeview', background=[('selected', self.fg_white)], foreground=[('selected', self.bg_dark)])

        # Scrollbars
        style.configure('Vertical.TScrollbar', background=self.bg_light_dark, troughcolor=self.bg_dark, bordercolor=self.fg_grey, arrowcolor=self.fg_grey)
        style.map('Vertical.TScrollbar', background=[('active', self.fg_grey)])
        style.configure('Horizontal.TScrollbar', background=self.bg_light_dark, troughcolor=self.bg_dark, bordercolor=self.fg_grey, arrowcolor=self.fg_grey)
        style.map('Horizontal.TScrollbar', background=[('active', self.fg_grey)])
        
        # Messagebox colors
        self.root.option_add('*Dialog*Background', self.bg_dark)
        self.root.option_add('*Dialog*Foreground', self.fg_white)
        self.root.option_add('*Dialog*Button.background', self.bg_light_dark)
        self.root.option_add('*Dialog*Button.foreground', self.fg_white)
        self.root.option_add('*Message.Background', self.bg_dark)
        self.root.option_add('*Message.Foreground', self.fg_white)

    def _create_auth_screen(self, frame_title, main_title, show_confirm=False):
        """Helper to create the base authentication screen (Login/Register)."""
        for widget in self.root.winfo_children():
            widget.destroy()

        auth_frame = ttk.LabelFrame(self.root, text=frame_title, padding=(20, 10))
        auth_frame.place(relx=0.5, rely=0.5, anchor='center')

        ttk.Label(auth_frame, text=main_title, font=('Consolas', 28, 'bold'), foreground=self.fg_white).grid(row=0, column=0, columnspan=2, pady=(10, 5))
        ttk.Label(auth_frame, text="_"*40, foreground=self.fg_grey).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(auth_frame, text="Username:", foreground=self.fg_grey).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        username_entry = ttk.Entry(auth_frame, width=30)
        username_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(auth_frame, text="Password:", foreground=self.fg_grey).grid(row=3, column=0, sticky='e', padx=5, pady=5)
        password_entry = ttk.Entry(auth_frame, width=30, show='*')
        password_entry.grid(row=3, column=1, padx=5, pady=5)

        entry_widgets = {"username": username_entry, "password": password_entry}
        next_row = 4

        if show_confirm:
            ttk.Label(auth_frame, text="Confirm Password:", foreground=self.fg_grey).grid(row=next_row, column=0, sticky='e', padx=5, pady=5)
            confirm_entry = ttk.Entry(auth_frame, width=30, show='*')
            confirm_entry.grid(row=next_row, column=1, padx=5, pady=5)
            entry_widgets["confirm"] = confirm_entry
            next_row += 1
        
        username_entry.focus()
        return auth_frame, entry_widgets, next_row


    def show_login_screen(self):
        """Display login screen"""
        auth_frame, entries, next_row = self._create_auth_screen(" [ SECURE ACCESS ] ", "StructDB Login")
        self.username_entry = entries["username"]
        self.password_entry = entries["password"]

        btn_frame = ttk.Frame(auth_frame)
        btn_frame.grid(row=next_row, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Login", command=self.login).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Register", command=self.show_register_screen).pack(side='left', padx=5)
        
        self.root.bind('<Return>', lambda e: self.login())
    
    def show_register_screen(self):
        """Display registration screen"""
        auth_frame, entries, next_row = self._create_auth_screen(" [ NEW USER REGISTRATION ] ", "Register New User", show_confirm=True)
        self.reg_username_entry = entries["username"]
        self.reg_password_entry = entries["password"]
        self.reg_confirm_entry = entries["confirm"]

        btn_frame = ttk.Frame(auth_frame)
        btn_frame.grid(row=next_row, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Register", command=self.register).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Back to Login", command=self.show_login_screen).pack(side='left', padx=5)
        
        self.root.unbind('<Return>')

    def register(self):
        """Handle user registration"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm = self.reg_confirm_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        try:
            self.db_manager.register_user(username, password)
            messagebox.showinfo("Success", f"User '{username}' registered successfully!")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def login(self):
        """Handle user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        try:
            self.db_manager.login(username, password)
            self.show_main_application()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_main_application(self):
        """Display main application interface after login"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.unbind('<Return>')
        
        # Top toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side='top', fill='x', padx=5, pady=5)
        
        ttk.Label(toolbar, text=f"User: {self.db_manager.current_user}", 
                 font=('Consolas', 10, 'bold'), foreground=self.fg_white).pack(side='left', padx=10)
        
        ttk.Button(toolbar, text="Logout", command=self.logout).pack(side='right', padx=5)
        
        # Notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: Query Mode
        self.query_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.query_frame, text='Query Mode')
        self.create_query_tab()
        
        # Tab 2: GUI Operations
        self.gui_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gui_frame, text='GUI Mode')
        self.create_gui_tab()
        
        # Tab 3: Database Info
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text='Database Info')
        self.create_info_tab()
        
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)
    
    def create_gui_tab(self):
        """Create the GUI operations tab widgets"""
        # Database and Table selection frame
        selection_frame = ttk.LabelFrame(self.gui_frame, text=" [ DATABASE & TABLE SELECTION ] ")
        selection_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(selection_frame, text="Current Database:", foreground=self.fg_grey).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.current_db_label = ttk.Label(selection_frame, text="None", foreground=self.fg_grey) 
        self.current_db_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(selection_frame, text="Select Table:", foreground=self.fg_grey).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.table_combo = ttk.Combobox(selection_frame, state='readonly', width=20)
        self.table_combo.grid(row=0, column=3, padx=5, pady=5)
        self.table_combo.bind('<<ComboboxSelected>>', self.on_table_select)
        
        ttk.Button(selection_frame, text="Refresh", command=self.refresh_gui).grid(row=0, column=4, padx=5, pady=5)
        
        # Main content area (Form on left, TreeView on right)
        content_frame = ttk.Frame(self.gui_frame)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left side: Record Form
        form_frame = ttk.LabelFrame(content_frame, text=" [ RECORD FORM ] ")
        form_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Canvas and Scrollbar for the form fields
        self.form_canvas = tk.Canvas(form_frame, bg=self.bg_dark, highlightthickness=0) 
        form_scrollbar = ttk.Scrollbar(form_frame, orient='vertical', command=self.form_canvas.yview)
        self.form_scrollable = ttk.Frame(self.form_canvas)
        self.form_scrollable.bind('<Configure>', lambda e: self.form_canvas.configure(scrollregion=self.form_canvas.bbox('all')))
        self.form_canvas.create_window((0, 0), window=self.form_scrollable, anchor='nw')
        self.form_canvas.configure(yscrollcommand=form_scrollbar.set)
        self.form_canvas.pack(side='left', fill='both', expand=True)
        form_scrollbar.pack(side='right', fill='y')
        
        self.form_fields = {}
        
        # Buttons below the form
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Insert", command=self.insert_record).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Update", command=self.update_record).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_record).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Show All", command=self.show_all_records).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Export CSV", command=self.export_csv).pack(side='left', padx=2)
        
        # Right side: Records TreeView
        tree_frame = ttk.LabelFrame(content_frame, text=" [ RECORDS ] ")
        tree_frame.pack(side='right', fill='both', expand=True)
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient='vertical')
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set, selectmode='browse')
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        tree_scroll_y.pack(side='right', fill='y')
        tree_scroll_x.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
    
    def create_query_tab(self):
        """Create the query mode tab widgets - LINE BY LINE EXECUTION"""
        main_query_frame = ttk.Frame(self.query_frame)
        main_query_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Query input section
        input_frame = ttk.LabelFrame(main_query_frame, text=" [ SQL QUERY - Press Enter to Execute Current Line ] ")
        input_frame.pack(fill='x', padx=(0, 5), pady=(0, 5)) 
        
        self.query_text = scrolledtext.ScrolledText(
            input_frame, 
            height=10, 
            wrap='word', 
            bg=self.bg_light_dark, 
            fg=self.fg_white, 
            insertbackground=self.fg_white, 
            relief="solid", 
            borderwidth=0
        ) 
        self.query_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # *** NEW: Bind Enter to execute current line ***
        self.query_text.bind('<Return>', self.execute_current_line)
        # Shift+Enter for normal newline
        self.query_text.bind('<Shift-Return>', lambda e: None)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Execute All Queries", command=self.execute_query).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.query_text.delete('1.0', 'end')).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="History", command=self.show_query_history).pack(side='left', padx=5)
        
        # Results section
        results_frame = ttk.LabelFrame(main_query_frame, text=" [ RESULTS ] ")
        results_frame.pack(fill='both', expand=True, padx=(0, 5), pady=(5, 0)) 
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame, 
            height=15, 
            wrap='word', 
            bg=self.bg_light_dark, 
            fg=self.fg_white, 
            insertbackground=self.fg_white, 
            relief="solid", 
            borderwidth=0
        ) 
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_info_tab(self):
        """Create the database info tab widgets"""
        info_frame_wrapper = ttk.LabelFrame(self.info_frame, text=" [ SYSTEM INFORMATION ] ", padding=(10, 5))
        info_frame_wrapper.pack(fill='both', expand=True, padx=10, pady=5)

        self.info_text = scrolledtext.ScrolledText(info_frame_wrapper, wrap='word', bg=self.bg_light_dark, fg=self.fg_white, insertbackground=self.fg_white, relief="solid", borderwidth=0) 
        self.info_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(info_frame_wrapper)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Refresh Info", command=self.refresh_info).pack(side='left', padx=5)
    
    def on_table_select(self, event=None):
        """Handle table selection in GUI mode combobox"""
        self.current_table = self.table_combo.get()
        if self.current_table:
            self.load_table_structure()
            self.show_all_records()
    
    def load_table_structure(self):
        """Load table structure and create form fields dynamically"""
        if not self.current_table: return
        
        try:
            db = self.db_manager.get_current_database()
            table = db.tables[self.current_table]
            
            column_defs = table['column_definitions']
            
            for widget in self.form_scrollable.winfo_children():
                widget.destroy()
            self.form_fields = {}
            
            for i, col_def in enumerate(column_defs):
                column_name = col_def['name']
                column_type = col_def['definition']
                
                ttk.Label(self.form_scrollable, text=f"{column_name}:", foreground=self.fg_grey).grid(row=i, column=0, padx=5, pady=5, sticky='e')
                entry = ttk.Entry(self.form_scrollable, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
                self.form_fields[column_name] = entry
                
                info_text = f"({column_type})"
                if column_name == table['primary_key']:
                    info_text = "(Primary Key)"
                
                ttk.Label(self.form_scrollable, text=info_text, foreground=self.fg_white, font=('Consolas', 8)).grid(row=i, column=2, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table structure: {e}")
    
    def show_all_records(self):
        """Display all records of the selected table in the TreeView"""
        if not self.current_table: return
        
        try:
            db = self.db_manager.get_current_database()
            records = db.select_records(self.current_table)
            
            self.tree.delete(*self.tree.get_children())
            
            columns_to_display = []
            if records:
                 columns_to_display = list(records[0].keys())
            elif self.current_table in db.tables:
                 columns_to_display = db.tables[self.current_table]['columns'] + ['_created_at', '_updated_at']

            if not columns_to_display: return

            self.tree['columns'] = columns_to_display
            self.tree['show'] = 'headings'
            for col in columns_to_display:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100)
            
            if records:
                for record in records:
                    values = [str(record.get(col, '')).replace('\n', '\\n') for col in columns_to_display]
                    self.tree.insert('', 'end', values=values)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load records: {e}")
    
    def on_tree_select(self, event):
        """Fill the form fields when a record is selected in the TreeView"""
        selection = self.tree.selection()
        if not selection: return
        
        item = self.tree.item(selection[0])
        values = item['values']
        columns = self.tree['columns']
        
        self.clear_form()
        
        for col, val in zip(columns, values):
            if col in self.form_fields:
                self.form_fields[col].insert(0, str(val).replace('\\n', '\n'))
    
    def insert_record(self):
        """Insert a new record using data from the form"""
        if not self.current_table:
            messagebox.showerror("Error", "Please select a table")
            return
        
        try:
            db = self.db_manager.get_current_database()
            columns = db.tables[self.current_table]['columns']
            values = [self.form_fields[col].get() for col in columns]
            
            db.insert_record(self.current_table, values)
            self.db_manager.save_database(self.db_manager.current_database)
            
            messagebox.showinfo("Success", "Record inserted successfully")
            self.show_all_records()
            self.clear_form()
            self.refresh_info()  # Auto-refresh info tab
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_record(self):
        """Update the selected record using data from the form"""
        if not self.current_table:
            messagebox.showerror("Error", "Please select a table")
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a record to update")
            return
        
        try:
            db = self.db_manager.get_current_database()
            table = db.tables[self.current_table]
            pk_column = table['primary_key']
            pk_value = self.form_fields[pk_column].get()
            
            set_clause = {}
            for col, entry in self.form_fields.items():
                if col != pk_column:
                    set_clause[col] = entry.get()
            
            where_clause = [(pk_column, '=', pk_value)]
            
            db.update_records(self.current_table, set_clause, where_clause)
            self.db_manager.save_database(self.db_manager.current_database)
            
            messagebox.showinfo("Success", "Record updated successfully")
            self.show_all_records()
            self.refresh_info()  # Auto-refresh info tab
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def delete_record(self):
        """Delete the selected record"""
        if not self.current_table:
            messagebox.showerror("Error", "Please select a table")
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a record to delete")
            return
        
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            return
        
        try:
            db = self.db_manager.get_current_database()
            table = db.tables[self.current_table]
            pk_column = table['primary_key']
            pk_value = self.form_fields[pk_column].get()
            
            where_clause = [(pk_column, '=', pk_value)]
            
            db.delete_records(self.current_table, where_clause)
            self.db_manager.save_database(self.db_manager.current_database)
            
            messagebox.showinfo("Success", "Record deleted successfully")
            self.show_all_records()
            self.clear_form()
            self.refresh_info()  # Auto-refresh info tab
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def clear_form(self):
        """Clear all entry fields in the record form"""
        for entry in self.form_fields.values():
            entry.delete(0, 'end')
    
    def export_csv(self):
        """Export the current table's data to a CSV file"""
        if not self.current_table:
            messagebox.showerror("Error", "Please select a table")
            return
        
        try:
            filename = f"{self.current_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            result = self.db_manager.export_to_csv(self.current_table, filename)
            messagebox.showinfo("Success", result)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def execute_current_line(self, event=None):
        """Execute only the current line where cursor is positioned - MySQL style with smart template"""
        # Get cursor position
        cursor_pos = self.query_text.index(tk.INSERT)
        line_num = cursor_pos.split('.')[0]
        
        # Get the current line text
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        current_line = self.query_text.get(line_start, line_end).strip()
        
        # If line is empty, create new line and move cursor
        if not current_line:
            self.query_text.insert(tk.INSERT, '\n')
            return "break"
        
        # *** SMART TEMPLATE: Extract INSERT template ***
        insert_template = None
        if current_line.upper().startswith('INSERT INTO'):
            # Extract "INSERT INTO table_name VALUES" part
            import re
            match = re.match(r'(INSERT\s+INTO\s+\w+\s+VALUES)\s*\(.*\)', current_line, re.IGNORECASE)
            if match:
                insert_template = match.group(1) + '()'
        
        # Execute the current line query
        try:
            result = self.db_manager.execute_query(current_line)
            
            # Show result in a compact MySQL-style format
            self.results_text.delete('1.0', 'end')
            self.results_text.tag_config('success', foreground='#2FFF00')  # Green like MySQL
            self.results_text.tag_config('line_info', foreground='#00BFFF', font=('Consolas', 9, 'bold'))
            
            self.results_text.insert('end', f"mysql> {current_line}\n", 'line_info')
            
            if isinstance(result, list):
                if result:
                    columns = list(result[0].keys())
                    
                    # MySQL-style table output
                    col_widths = {}
                    for col in columns:
                        col_widths[col] = max(len(str(col)), 
                                             max(len(str(r.get(col, ''))) for r in result))
                    
                    # Top border
                    border = '+' + '+'.join('-' * (col_widths[col] + 2) for col in columns) + '+'
                    self.results_text.insert('end', border + '\n', 'success')
                    
                    # Headers
                    header = '|' + '|'.join(f" {col:<{col_widths[col]}} " for col in columns) + '|'
                    self.results_text.insert('end', header + '\n', 'success')
                    self.results_text.insert('end', border + '\n', 'success')
                    
                    # Rows
                    for record in result:
                        row = '|' + '|'.join(f" {str(record.get(col, '')):<{col_widths[col]}} " for col in columns) + '|'
                        self.results_text.insert('end', row + '\n', 'success')
                    
                    # Bottom border
                    self.results_text.insert('end', border + '\n', 'success')
                    self.results_text.insert('end', f"{len(result)} row(s) in set\n", 'success')
                else:
                    self.results_text.insert('end', "Empty set\n", 'success')
            else:
                self.results_text.insert('end', f"{result}\n", 'success')
            
            self.refresh_gui()
            self.refresh_info()  # Auto-refresh info tab after query execution
            
        except Exception as e:
            self.results_text.delete('1.0', 'end')
            self.results_text.tag_config('error', foreground='red', font=('Consolas', 10, 'bold'))
            self.results_text.insert('end', f"mysql> {current_line}\n", 'line_info')
            self.results_text.insert('end', f"ERROR: {str(e)}\n", 'error')
        
        # *** SMART MOVE: Move cursor to next line with template ***
        # Move to end of current line first
        self.query_text.mark_set(tk.INSERT, line_end)
        
        # Insert newline if we're at the last line
        last_line_index = self.query_text.index('end-1c')
        current_line_end = self.query_text.index(f"{line_num}.end")
        
        # Check if we need to add a new line
        if self.query_text.compare(current_line_end, '>=', last_line_index):
            self.query_text.insert('end', '\n')
        
        # Now move to the next line
        next_line_num = str(int(line_num) + 1)
        self.query_text.mark_set(tk.INSERT, f"{next_line_num}.0")
        
        # *** AUTO-FILL: Insert template if it's an INSERT query ***
        if insert_template:
            # Check if next line is empty
            next_line_content = self.query_text.get(f"{next_line_num}.0", f"{next_line_num}.end").strip()
            if not next_line_content:
                self.query_text.insert(f"{next_line_num}.0", insert_template)
                # Position cursor inside the parentheses
                cursor_position = f"{next_line_num}.{len(insert_template)-1}"
                self.query_text.mark_set(tk.INSERT, cursor_position)
        
        self.query_text.see(tk.INSERT)
        
        return "break"  # Prevent default newline insertion
    
    def execute_query(self):
        """Execute ALL queries in the text box"""
        full_query_text = self.query_text.get('1.0', 'end').strip()
        if not full_query_text:
            messagebox.showerror("Error", "Please enter a query")
            return
        
        queries = [q.strip() for q in full_query_text.split(';') if q.strip()]
        
        self.results_text.delete('1.0', 'end')
        all_success = True
        
        self.results_text.tag_config('query_header', foreground='yellow', font=('Consolas', 10, 'bold'))
        self.results_text.tag_config('success_query', foreground=self.fg_white)
        self.results_text.tag_config('error_query', foreground='red', font=('Consolas', 10, 'bold'))
        
        for i, query in enumerate(queries):
            query_number = i + 1
            self.results_text.insert('end', f"--- Query {query_number}: {query} ---\n", 'query_header')
            
            try:
                result = self.db_manager.execute_query(query)
                
                if isinstance(result, list):
                    if result:
                        columns = list(result[0].keys())
                        self.results_text.insert('end', ' | '.join(columns) + '\n', 'success_query')
                        self.results_text.insert('end', '-' * 80 + '\n', 'success_query')
                        for record in result:
                            values = [str(record.get(col, '')).replace('\n', '\\n') for col in columns] 
                            self.results_text.insert('end', ' | '.join(values) + '\n', 'success_query')
                        self.results_text.insert('end', f"\n{len(result)} row(s) returned\n\n", 'success_query')
                    else:
                        self.results_text.insert('end', "No records found\n\n", 'success_query')
                else:
                    self.results_text.insert('end', str(result) + '\n\n', 'success_query')
                
            except ValueError as ve:
                error_message = f"Error in Query {query_number}: {str(ve)}\n\n"
                self.results_text.insert('end', error_message, 'error_query')
                all_success = False
                continue
                
            except Exception as e:
                error_message = f"Fatal Error in Query {query_number}: {str(e)}\n\n"
                self.results_text.insert('end', error_message, 'error_query')
                all_success = False
                break

        if all_success:
             self.refresh_gui()
             self.refresh_info()  # Auto-refresh info tab after batch execution
    
    def show_query_history(self):
        """Show the recent query history in a new window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Query History")
        history_window.geometry("600x400")
        history_window.configure(bg=self.bg_dark)

        history_frame = ttk.LabelFrame(history_window, text=" [ QUERY LOG ] ", padding=(10, 5))
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        history_text = scrolledtext.ScrolledText(history_frame, wrap='word', bg=self.bg_light_dark, fg=self.fg_white, insertbackground=self.fg_white, relief="solid", borderwidth=0) 
        history_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        for entry in self.db_manager.query_history[-50:]:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            history_text.insert('end', f"[{timestamp}] {entry['query']}\n\n")
    
    def refresh_gui(self):
        """Refresh GUI elements like current DB label and table list"""
        if self.db_manager.current_database:
            db_name = self.db_manager.databases[self.db_manager.current_database]['database'].name
            self.current_db_label.config(text=db_name, foreground=self.fg_white) 
            
            try:
                db = self.db_manager.get_current_database()
                tables = list(db.tables.keys())
                self.table_combo['values'] = tables
                self.table_combo.set('')
                self.current_table = None
                if hasattr(self, 'form_fields') and self.form_fields: self.clear_form()
                self.tree.delete(*self.tree.get_children())
            except Exception:
                 self.current_db_label.config(text="None", foreground='red') 
                 self.table_combo['values'] = []
                 self.table_combo.set('')
                 self.current_table = None
        else:
            self.current_db_label.config(text="None", foreground='red') 
            self.table_combo['values'] = []
            self.table_combo.set('')
            self.current_table = None
    
    def refresh_info(self):
        """Refresh the content of the Database Info tab"""
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', 'end')
        
        info = f"{'='*60}\n"
        info += f"StructDB - Database Information\n"
        info += f"{'='*60}\n\n"
        info += f"Current User: {self.db_manager.current_user}\n"
        info += f"User Role: {self.db_manager.users[self.db_manager.current_user]['role']}\n\n"
        databases = self.db_manager.list_databases()
        info += f"Total Databases ({self.db_manager.current_user}): {len(databases)}\n\n"
        
        if self.db_manager.current_database:
            try:
                db = self.db_manager.get_current_database()
                info += f"Current Database: {db.name}\n"
                info += f"Owner: {db.owner}\n"
                info += f"Created: {db.created_at}\n"
                info += f"Total Tables: {len(db.tables)}\n"
                for table_name, table in db.tables.items():
                    records_count = len(table['records'])
                    info += f"\n  Table: {table_name}\n"
                    col_info = [f"{c['name']} ({c['definition']})" for c in table['column_definitions']]
                    info += f"    Columns: {', '.join(col_info)}\n"
                    info += f"    Primary Key: {table['primary_key']}\n"
                    info += f"    Records: {records_count}\n"
                    info += f"    Created: {table['created_at']}\n"
            except Exception as e:
                info += f"\nError accessing current database info: {e}\n"
        else:
            info += "\nNo database selected.\n"
            info += "Use 'USE database_name' in Query Mode to select one.\n"
        
        info += f"\n{'='*60}\n"
        info += f"About StructDB\n"
        info += f"{'='*60}\n" 
        info += "A lightweight mini database engine with:\n"
        info += "- Multi-database support\n"
        info += "- SQL-like query language\n"
        info += "- Hash table indexing (O(1) lookup)\n"
        info += "- User authentication & authorization\n"
        info += "- GUI and Query modes\n"
        info += "- CRUD operations\n"
        info += "- Data persistence (JSON)\n"
        info += "- Export to CSV\n"
        
        self.info_text.insert('1.0', info)
        
        self.info_text.tag_add('all_text', '1.0', 'end')
        self.info_text.tag_config('all_text', foreground=self.fg_grey)
        
        title_lines = ['1.0', '2.0', '3.0']
        about_start = self.info_text.search("About StructDB", '1.0', 'end')
        if about_start:
            about_line = about_start.split('.')[0]
            title_lines.extend([f"{int(about_line)-1}.0", f"{about_line}.0", f"{int(about_line)+1}.0"])

        for line_start in title_lines:
             line_end = f"{line_start.split('.')[0]}.end"
             try:
                 self.info_text.tag_add('title', line_start, line_end)
             except tk.TclError:
                 pass 
        self.info_text.tag_config('title', foreground=self.fg_white, font=('Consolas', 11, 'bold'))
        
        self.info_text.config(state='disabled')

    def on_tab_change(self, event):
        """Handle tab change event to refresh relevant tab"""
        current_tab_index = self.notebook.index(self.notebook.select())
        if current_tab_index == 1:
            self.refresh_gui()
        elif current_tab_index == 2:
            self.refresh_info()
    
    def logout(self):
        """Logout current user and return to login screen"""
        if messagebox.askyesno("Confirm", "Are you sure you want to logout?"):
            self.db_manager.logout()
            self.show_login_screen()