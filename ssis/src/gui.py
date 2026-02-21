import tkinter as tk
import pyglet
import os
import csv
from tkinter import ttk, messagebox, filedialog
import database as db

class SSIS_APP:
    def __init__(self, root):
        self.root = root
        self.root.after(200, lambda: self.switch_view("students"))
        self.root.title("Student Information System")
        self.root.state("zoomed")

        base_path = os.path.dirname(__file__)
        font_path = os.path.join(base_path, 'assets', 'Material_Icons.ttf')

        self.current_sort_col = None
        self.current_sort_reverse = False

        self.root.bind("<Button-1>", self.unfocus_widgets)
        self.root.bind("<Control-Right>", lambda e: self.next_page())
        self.root.bind("<Control-Left>", lambda e: self.prev_page())
        
        # 1. Initialize State Variables
        self.current_view = "students"
        self.current_page = 1
        self.rows_per_page = 10
        self.total_pages = 1
        self.all_data_cache = []

        # 2. Setup UI Components
        self.setup_styles()
        
        # Frames
        self.sidebar = tk.Frame(self.root, bg="#1a1a1a", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.main_window = tk.Frame(self.root, bg="#2b2b2b")
        self.main_window.pack(side="right", expand=True, fill="both")

        # Call setup methods in order
        self.setup_sidebar()
        self.setup_main_window()


        # 3. Load data
        self.switch_view("students")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview", 
            background="#101218", 
            foreground="#f1f5f9", 
            fieldbackground="#101218", 
            rowheight=60, 
            font=("Arial", 10)
        )
        style.configure("Treeview.Heading", 
            background="#334155", 
            foreground="#f1f5f9", 
            relief="flat",
            font=("Arial", 10, "bold")
        )
        style.map("Treeview", 
            background=[('selected', '#8c52ff')], 
            foreground=[('selected', '#f1f5f9')]
        )
        style.configure("Icon.Treeview",
                        font=("Material Icons", 14)
        )
        style.map("TCombobox", 
        fieldbackground=[("readonly", "#334155"), ("disabled", "#1a1a1a")],
        background=[("readonly", "#334155")],
        foreground=[("readonly", "#f1f5f9")]
        )
        style.configure("TCombobox", 
            relief="flat",
            borderwidth=0,
            padding=5
        )
        self.root.option_add("*TCombobox*Listbox.background", "#334155")
        self.root.option_add("*TCombobox*Listbox.foreground", "#f1f5f9")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#8c52ff")

    def setup_sidebar(self):
        tk.Label(self.sidebar, text="MENU", fg="#64748b", bg="#1a1a1a",
                 font=("Arial", 10, "bold")).pack(pady=(30, 10))
        
        self.nav_buttons = {}
        views = [("Students", "students"), ("Programs", "programs"), ("Colleges", "colleges")]

        for text, v_type in views:
            btn = tk.Button(
                self.sidebar, text=text,
                command=lambda v=v_type: self.switch_view(v),
                font=("Arial", 11), bg="#101218", fg="#64748b",
                activebackground="#334155", activeforeground="#8c52ff",
                relief="flat", bd=0, padx=20, pady=12, anchor="w", cursor="hand2"
            )
            btn.pack(fill="x", padx=10)
            self.nav_buttons[v_type] = btn

    def setup_main_window(self):
        self.main_window.configure(bg="#101218")

        self.top_bar = tk.Frame(self.main_window, bg="#101218")
        self.top_bar.pack(side="top", fill="x", padx=20, pady=10)

        self.placeholder_text = "Search..."
        search_frame = tk.Frame(self.top_bar, bg="#334155", bd=0)
        search_frame.pack(side="left", padx=10)
        
        self.search_entry = tk.Entry(search_frame, font=('Arial', 12), width=40, 
                                     bg="#334155", fg="#f1f5f9", 
                                     insertbackground="#8c52ff", relief="flat")
        self.search_entry.pack(side="left", padx=(10, 5), pady=8)
        self.search_entry.insert(0, self.placeholder_text)

        self.clear_btn = tk.Button(search_frame, text="✕", bg="#334155", fg="#64748b",
                                   activebackground="#334155", activeforeground="#8c52ff",
                                   relief="flat", bd=0, cursor="hand2", font=("Arial", 10, "bold"),
                                   command=self.clear_search_text)

        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_placeholder)
        self.search_entry.bind("<KeyRelease>", self.on_search_keypress)

        self.add_btn = tk.Button(self.top_bar, text="+ Add Record", bg="#8c52ff", fg="#f1f5f9", 
                                font=("Arial", 10, "bold"), relief="flat", padx=20, pady=8,
                                command=self.open_add_form, cursor="hand2")
        self.add_btn.pack(side="right", padx=5)

        self.import_btn = tk.Button(self.top_bar, text="Import CSV", bg="#334155", fg="#f1f5f9", 
                                   font=("Arial", 10, "bold"), relief="flat", padx=15, pady=8,
                                   command=self.import_csv, cursor="hand2")
        self.import_btn.pack(side="right", padx=5)
        
        self.setup_pagination_ui()

        self.tree_frame = tk.Frame(self.main_window, bg="#101218")
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=(10, 0))

        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.tag_configure('evenrow', background='#161b22')
        
        self.tree.pack(side="left", expand=True, fill="both")
        self.tree.bind("<ButtonRelease-1>", self.handle_table_click)


    def setup_pagination_ui(self):
        self.pagination_frame = tk.Frame(self.main_window, bg="#101218")
        self.pagination_frame.pack(side="bottom", fill="x", pady=10)

        self.next_btn = tk.Button(self.pagination_frame, text="Next >", bg="#334155", fg="#f1f5f9", 
                                  relief="flat", padx=15, command=self.next_page, cursor="hand2")
        self.next_btn.pack(side="right", padx=20)

        self.page_label = tk.Label(self.pagination_frame, text="Page 1 of 1", bg="#101218", fg="#64748b")
        self.page_label.pack(side="right", padx=10)

        self.jump_entry = tk.Entry(self.pagination_frame, width=5, bg="#334155", fg="#f1f5f9", 
                                   relief="flat", insertbackground="#8c52ff", justify="center")
        self.jump_entry.pack(side="right", padx=5)
        self.jump_entry.bind("<Return>", self.jump_to_page)

        tk.Label(self.pagination_frame, text="Go to:", bg="#101218", fg="#64748b", font=("Arial", 9)).pack(side="right")

        self.prev_btn = tk.Button(self.pagination_frame, text="< Prev", bg="#334155", fg="#f1f5f9", 
                                  relief="flat", padx=15, command=self.prev_page, cursor="hand2")
        self.prev_btn.pack(side="right", padx=2)

        self.info_label = tk.Label(self.pagination_frame, text="", bg="#101218", fg="#64748b", font=("Arial", 9))
        self.info_label.pack(side="left", padx=20)


    def load_table_data(self, view_type, refresh_cache=True):
        if refresh_cache:
            files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
            self.all_data_cache = db.read_data(files[view_type])
            self.current_page = 1 

        self.calculate_rows_per_page()
        
        rpp = self.rows_per_page if self.rows_per_page > 0 else 10
        
        total_rows = len(self.all_data_cache)
        
        self.total_pages = max(1, (total_rows + rpp - 1) // rpp)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * rpp
        end_idx = start_idx + rpp
        page_data = self.all_data_cache[start_idx:end_idx]

        default_cols = {
            "students": ["student_id", "first_name", "last_name", "year_level", "gender", "program_code"],
            "programs": ["program_code", "program_name", "college_code"],
            "colleges": ["college_code", "college_name"]
        }
        
        if self.all_data_cache and len(self.all_data_cache) > 0:
            cols = list(self.all_data_cache[0].keys())
        else:
            cols = default_cols[view_type]

        all_cols = cols + ["actions"]
        self.tree.configure(columns=all_cols)
        self.adjust_column_widths(cols)

        sort_col = getattr(self, 'current_sort_col', None)
        sort_rev = getattr(self, 'current_sort_reverse', False)

        for col in cols:
            base_name = col.replace("_", " ").upper()
            display_name = base_name
            if col == sort_col:
                display_name += "  ▼" if sort_rev else "  ▲"

            self.tree.heading(
                col, 
                text=display_name, 
                anchor="w",
                command=lambda c=col, r=sort_rev: self.sort_column(c, not r if c == sort_col else False)
            )
            self.tree.column(col, anchor="w")

        self.tree.heading("actions", text="ACTIONS", anchor="center")
        self.tree.column("actions", width=100, minwidth=100, anchor="center", stretch=False)

        for item in self.tree.get_children(): 
            self.tree.delete(item)
        
        for i, row in enumerate(page_data):
            tag = ('evenrow',) if i % 2 != 0 else ()
            
            wrapped_row_values = []
            for val in row.values():
                text = str(val)
                if len(text) > 35:
                    import textwrap
                    text = "\n".join(textwrap.wrap(text, width=35))
                wrapped_row_values.append(text)
            
            self.tree.insert("", "end", values=wrapped_row_values + [f"\ue3c9   \ue872"], tags=tag)

        total_rows = len(self.all_data_cache)
        calculated_total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
        self.total_pages = calculated_total_pages

        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
        
        start_num = start_idx + 1 if total_rows > 0 else 0
        end_num = min(end_idx, total_rows)
        self.info_label.config(text=f"Showing {start_num} to {end_num} of {total_rows} entries")

        if self.current_page <= 1:
            self.prev_btn.config(state="disabled", bg="#1a1a1a", fg="#4a4a4a")
        else:
            self.prev_btn.config(state="normal", bg="#334155", fg="#f1f5f9")

        if self.current_page >= self.total_pages:
            self.next_btn.config(state="disabled", bg="#1a1a1a", fg="#4a4a4a")
        else:
            self.next_btn.config(state="normal", bg="#334155", fg="#f1f5f9")

    def handle_table_click(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item: return

        cols = self.tree["columns"]
        if column == f"#{len(cols)}":
            row_vals = self.tree.item(item, "values")
            bbox = self.tree.bbox(item, column)
            if not bbox: return
            
            x_in_cell = event.x - bbox[0]
            
            if x_in_cell < 50: 
                self.open_add_form(edit_mode=True, item_id=row_vals[0], current_vals=row_vals)
            else:
                self.confirm_single_delete(item, row_vals[0])

    def confirm_single_delete(self, item, pk):
        if messagebox.askyesno("Confirm", f"Delete record {pk}?"):
            files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
            id_cols = {"students": "student_id", "programs": "program_code", "colleges": "college_code"}
            
            data = db.read_data(files[self.current_view])
            new_data = [row for row in data if str(row[id_cols[self.current_view]]) != str(pk)]
            
            db.save_data(files[self.current_view], list(data[0].keys()), new_data)
            self.tree.delete(item)

    def switch_view(self, view_type):
        self.current_view = view_type
        self.add_btn.config(text=f"+ Add {view_type[:-1].capitalize()}")
        
        for v, btn in self.nav_buttons.items():
            if v == view_type:
                btn.config(fg="#8c52ff", bg="#334155")
            else:
                btn.config(fg="#64748b", bg="#101218")
        
        self.load_table_data(view_type)


    def filter_search(self, event=None):
        query = self.search_entry.get().lower()
        
        if query == "" or query == self.placeholder_text.lower():
            self.load_table_data(self.current_view)
            return

        files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
        all_data = db.read_data(files[self.current_view])
        
        filtered = [row for row in all_data if query in " ".join(map(str, row.values())).lower()]
        
        self.all_data_cache = filtered
        self.current_page = 1
        
        self.load_table_data(self.current_view, refresh_cache=False)

    def clear_placeholder(self, event):
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="white")

    def restore_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg="gray")

    def adjust_column_widths(self, cols):
        min_width = 120
        max_col_width = 350 
        char_multiplier = 9 
        
        max_lengths = {col: len(col) for col in cols}

        for row in self.all_data_cache:
            for col in cols:
                val_len = len(str(row.get(col, "")))
                if val_len > max_lengths[col]:
                    max_lengths[col] = val_len

        for col in cols:
            calculated_width = (max_lengths[col] * char_multiplier) + 30
            final_width = min(max_col_width, max(min_width, calculated_width))
            self.tree.column(col, width=final_width, minwidth=min_width, stretch=True)

    def sort_column(self, col, reverse):
        if col == "actions" or not self.all_data_cache:
            return

        try:
            try:
                self.all_data_cache.sort(
                    key=lambda x: float(str(x.get(col, 0)).replace("\n", "").strip()), 
                    reverse=reverse
                )
            except ValueError:
                self.all_data_cache.sort(
                    key=lambda x: str(x.get(col, "")).lower().replace("\n", "").strip(), 
                    reverse=reverse
                )

            self.current_sort_col = col
            self.current_sort_reverse = reverse

            self.load_table_data(self.current_view, refresh_cache=False)

        except Exception as e:
            print(f"Sort Error: {e}")


    def open_add_form(self, edit_mode=False, item_id=None, current_vals=None):
        self.edit_target_id = item_id if edit_mode else None
        self.form_window = tk.Toplevel(self.root)
        self.form_window.title("Edit Record" if edit_mode else "Add New Record")
        self.form_window.geometry("500x650")
        self.form_window.configure(bg="#101218")
        self.form_window.grab_set()
        self.form_window.bind("<Escape>", lambda e: self.form_window.destroy())

        header_frame = tk.Frame(self.form_window, bg="#101218")
        header_frame.pack(fill="x", padx=40, pady=(30, 10))
        
        title_text = f"{'Edit' if edit_mode else 'Add New'} {self.current_view[:-1].capitalize()}"
        tk.Label(header_frame, text=title_text, fg="#f1f5f9", bg="#101218", 
                 font=("Arial", 16, "bold")).pack(side="left")

        self.inputs = {}
        field_configs = {
            "students": ["Student ID", "First Name", "Last Name", "Year Level", "Gender", "Program Code"],
            "programs": ["Program Code", "Program Name", "College Code"],
            "colleges": ["College Code", "College Name"]
        }
        
        fields = field_configs[self.current_view]

        for i, field in enumerate(fields):
            frame = tk.Frame(self.form_window, bg="#101218")
            frame.pack(fill="x", padx=40, pady=8)

            tk.Label(frame, text=field.upper(), fg="#64748b", bg="#101218", 
                     font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 5))

            if field in ["Gender", "Year Level"]:
                entry = ttk.Combobox(frame, values=["M", "F", "O"] if field == "Gender" else ["1", "2", "3", "4"], 
                                     state="readonly")
            else:
                entry = tk.Entry(frame, bg="#334155", fg="#f1f5f9", insertbackground="#8c52ff",
                                 relief="flat", font=("Arial", 11), bd=8)
            
            entry.pack(fill="x")
            
            if edit_mode and current_vals:
                if isinstance(entry, ttk.Combobox):
                    entry.set(current_vals[i])
                else:
                    entry.insert(0, current_vals[i])
                if i == 0: entry.config(state="disabled", readonlybackground="#1a1a1a")

            self.inputs[field] = entry

        footer = tk.Frame(self.form_window, bg="#101218")
        footer.pack(fill="x", padx=40, pady=30)

        tk.Button(footer, text="Cancel", bg="#101218", fg="#64748b", relief="flat",
                  font=("Arial", 10, "bold"), command=self.form_window.destroy,
                  cursor="hand2").pack(side="left")

        tk.Button(footer, text="Save Record", bg="#8c52ff", fg="#f1f5f9", relief="flat",
                  font=("Arial", 10, "bold"), padx=25, pady=8,
                  command=self.submit_data, cursor="hand2").pack(side="right")

    def import_csv(self):
        required_headers = {
            "students": ["student_id", "first_name", "last_name", "year_level", "gender", "program_code"],
            "programs": ["program_code", "program_name", "college_code"],
            "colleges": ["college_code", "college_name"]
        }
        target_headers = required_headers[self.current_view]

        file_path = filedialog.askopenfilename(
            title=f"Import {self.current_view.capitalize()} CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return
        try:
            with open(file_path, mode="r", newline='', encoding="utf-8") as f:
                reader = csv.DictReader(f)
                file_headers = reader.fieldnames

                if not file_headers:
                    messagebox.showerror("Error", "The selected file is empty or invald.")
                    return
                missing = [h for h in target_headers if h not in file_headers]
                different = [h for h in file_headers if not h in target_headers]

                if missing:
                    error_msg = f"Validation Failed!\n\nMissing Columns: {','.join(missing)}"
                    if different:
                        error_msg += f"\n\nUnknown columns found: {','.join(different)}"
                    error_msg += f"\n\nPlease ensure your CSV headers match: {','.join(target_headers)}"
                    messagebox.showerror("Header Mismatch", error_msg)
                    return
                new_records = list(reader)
                if not new_records:
                    messagebox.showwarning("Warning", "No data found in the CSV file.")
                    return
                if messagebox.askyesno("Confrim Import", f"Import {len(new_records)} records into {self.current_view}?"):
                    filename = f"{self.current_view}.csv"
                    db.save_data(filename, target_headers, new_records)
                    self.load_table_data(self.current_view)
                    messagebox.showinfo("Success", f"Successfully imported {len(new_records)} records.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occured: {str(e)}")

    def submit_data(self):
        raw_data = {field: widget.get() for field, widget in self.inputs.items()}

        if any(val == "" for val in raw_data.values()):
            messagebox.showwarning("Input Error", "All Fields Required")
            return
        
        mapping = {
            "students": {
                "Student ID": "student_id", "First Name": "first_name", "Last Name": "last_name",
                "Year Level": "year_level", "Gender": "gender", "Program Code": "program_code"
            },
            "programs": {"Program Code": "program_code", "Program Name": "program_name", "College Code": "college_code"},
            "colleges": {"College Code": "college_code", "College Name": "college_name"}
        }
        
        final_dict = {mapping[self.current_view][k]: v for k, v in raw_data.items()}
        filename = f"{self.current_view}.csv"
        primary_key_val = list(final_dict.values())[0]

        if hasattr(self, 'edit_target_id') and self.edit_target_id:
            success = True
            msg = ""
            db.update_row(filename, primary_key_val, final_dict)
        else:
            if self.current_view == "colleges":
                success, msg = db.validate_college(final_dict["college_code"])
            elif self.current_view == "programs":
                success, msg = db.validate_program(final_dict["program_code"], final_dict["college_code"])
            else:
                success, msg = db.validate_student(final_dict["student_id"], final_dict["gender"], final_dict["program_code"])

            if success:
                db.append_row(filename, list(final_dict.keys()), final_dict)

        if success:
            messagebox.showinfo("Success", f"{self.current_view[:-1].capitalize()} saved successfully")
            self.form_window.destroy()
            self.edit_target_id = None
            self.load_table_data(self.current_view)
        else:
            messagebox.showerror("Validation Error", msg)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_table_data(self.current_view, refresh_cache=False)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_table_data(self.current_view, refresh_cache=False)

    def unfocus_widgets(self, event):
        clicked_widget = event.widget
        
        if clicked_widget != self.search_entry and clicked_widget != self.jump_entry:
            self.root.focus_set()
            
        if hasattr(self, 'tree') and clicked_widget != self.tree:
            self.tree.selection_remove(self.tree.selection())

    def on_search_keypress(self, event=None):
        query = self.search_entry.get()
        
        if query and query != self.placeholder_text:
            if not self.clear_btn.winfo_ismapped():
                self.clear_btn.pack(side="right", padx=10)
        else:
            self.clear_btn.pack_forget()
            
        self.filter_search()

    def clear_search_text(self):
        self.search_entry.delete(0, tk.END)
        self.clear_btn.pack_forget()
        
        self.root.focus_set() 
        self.load_table_data(self.current_view)
    
    def jump_to_page(self, event=None):
        try:
            page = int(self.jump_entry.get())
            if 1 <= page <= self.total_pages:
                self.current_page = page
                self.load_table_data(self.current_view, refresh_cache=False)
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page between 1 and {self.total_pages}")
        except ValueError:
            pass
        self.jump_entry.delete(0, tk.END)

    def calculate_rows_per_page(self):
        self.root.update_idletasks()
        available_height = self.tree_frame.winfo_height()
        
        if available_height <= 1:
            self.rows_per_page = 10 
            return

        header_height = 45
        row_height = 60 
        
        usable_height = available_height - header_height
        self.rows_per_page = max(1, usable_height // row_height)