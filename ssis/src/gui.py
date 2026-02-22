import tkinter as tk
import os
import csv
import textwrap
from tkinter import ttk, messagebox, filedialog
import database as db

# ----------------------------------------------------------------------
# Constants / Configuration
# ----------------------------------------------------------------------
class Config:
    # Colors
    BG_DARK = "#101218"
    BG_SIDEBAR = "#1a1a1a"
    BG_INPUT = "#334155"
    FG_LIGHT = "#f1f5f9"
    FG_MUTED = "#64748b"
    ACCENT = "#8c52ff"
    SELECT_BG = "#8c52ff"

    # Font sizes
    FONT_FAMILY = "Arial"
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 11
    FONT_SIZE_SMALL = 8
    TREE_ROW_HEIGHT = 55
    TREE_HEADER_HEIGHT = 45
    TREE_CHAR_WIDTH = 9
    MAX_COL_WIDTH = 350
    MIN_COL_WIDTH = 120

    # Pagination
    DEFAULT_ROWS_PER_PAGE = 10

    # Window constraints
    MIN_ROWS_VISIBLE = 5
    MIN_TOTAL_WIDTH = 700  # sidebar(220) + enough for the narrowest table

    # File names
    CSV_FILES = {
        "students": "students.csv",
        "programs": "programs.csv",
        "colleges": "colleges.csv"
    }

    # Primary key column for each view
    PK_COLUMN = {
        "students": "student_id",
        "programs": "program_code",
        "colleges": "college_code"
    }

    # Default columns for each view
    DEFAULT_COLUMNS = {
        "students": ["student_id", "first_name", "last_name", "year_level", "gender", "program_code"],
        "programs": ["program_code", "program_name", "college_code"],
        "colleges": ["college_code", "college_name"]
    }

    # Form field labels
    FORM_FIELDS = {
        "students": ["Student ID", "First Name", "Last Name", "Year Level", "Gender", "Program Code"],
        "programs": ["Program Code", "Program Name", "College Code"],
        "colleges": ["College Code", "College Name"]
    }

    # Mapping from form label to database column
    FIELD_TO_COLUMN = {
        "students": {
            "Student ID": "student_id",
            "First Name": "first_name",
            "Last Name": "last_name",
            "Year Level": "year_level",
            "Gender": "gender",
            "Program Code": "program_code"
        },
        "programs": {
            "Program Code": "program_code",
            "Program Name": "program_name",
            "College Code": "college_code"
        },
        "colleges": {
            "College Code": "college_code",
            "College Name": "college_name"
        }
    }

    # Combobox options
    GENDER_OPTIONS = ["M", "F", "O"]
    YEAR_OPTIONS = ["1", "2", "3", "4"]


# ----------------------------------------------------------------------
# Pagination Widget
# ----------------------------------------------------------------------
class PaginationBar(tk.Frame):
    def __init__(self, parent, on_prev, on_next, on_jump, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg=Config.BG_DARK)

        self.on_prev = on_prev
        self.on_next = on_next
        self.on_jump = on_jump

        self.current_page = 1
        self.total_pages = 1
        self.total_rows = 0
        self.rows_per_page = Config.DEFAULT_ROWS_PER_PAGE

        # Create widgets
        self.next_btn = tk.Button(
            self, text="Next >", bg=Config.BG_INPUT, fg=Config.FG_LIGHT,
            relief="flat", padx=15, command=self._next, cursor="hand2"
        )
        self.next_btn.pack(side="right", padx=20)

        self.prev_btn = tk.Button(
            self, text="< Prev", bg=Config.BG_INPUT, fg=Config.FG_LIGHT,
            relief="flat", padx=15, command=self._prev, cursor="hand2"
        )
        self.prev_btn.pack(side="right", padx=2)

        self.page_label = tk.Label(
            self, text="Page 1 of 1", bg=Config.BG_DARK, fg=Config.FG_MUTED
        )
        self.page_label.pack(side="right", padx=10)

        self.jump_entry = tk.Entry(
            self, width=5, bg=Config.BG_INPUT, fg=Config.FG_LIGHT,
            relief="flat", insertbackground=Config.ACCENT, justify="center"
        )
        self.jump_entry.pack(side="right", padx=5)
        self.jump_entry.bind("<Return>", self._jump)

        tk.Label(
            self, text="Go to:", bg=Config.BG_DARK, fg=Config.FG_MUTED,
            font=(Config.FONT_FAMILY, 9)
        ).pack(side="right")

        self.info_label = tk.Label(
            self, text="", bg=Config.BG_DARK, fg=Config.FG_MUTED,
            font=(Config.FONT_FAMILY, 9)
        )
        self.info_label.pack(side="left", padx=20)

        self._update_buttons_state()

    def _prev(self):
        if self.current_page > 1:
            self.on_prev()

    def _next(self):
        if self.current_page < self.total_pages:
            self.on_next()

    def _jump(self, event):
        try:
            page = int(self.jump_entry.get())
            if 1 <= page <= self.total_pages:
                self.on_jump(page)
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page between 1 and {self.total_pages}")
        except ValueError:
            pass
        self.jump_entry.delete(0, tk.END)

    def update(self, current_page, total_pages, total_rows, start_idx, end_idx, rows_per_page):
        self.current_page = current_page
        self.total_pages = total_pages
        self.total_rows = total_rows
        self.rows_per_page = rows_per_page

        self.page_label.config(text=f"Page {current_page} of {total_pages}")
        start_num = start_idx + 1 if total_rows > 0 else 0
        end_num = min(end_idx, total_rows)
        self.info_label.config(text=f"Showing {start_num} to {end_num} of {total_rows} entries")
        self._update_buttons_state()

    def _update_buttons_state(self):
        if self.current_page <= 1:
            self.prev_btn.config(state="disabled", bg="#1a1a1a", fg="#4a4a4a")
        else:
            self.prev_btn.config(state="normal", bg=Config.BG_INPUT, fg=Config.FG_LIGHT)

        if self.current_page >= self.total_pages:
            self.next_btn.config(state="disabled", bg="#1a1a1a", fg="#4a4a4a")
        else:
            self.next_btn.config(state="normal", bg=Config.BG_INPUT, fg=Config.FG_LIGHT)


# ----------------------------------------------------------------------
# Main Application Class
# ----------------------------------------------------------------------
class SSIS_APP:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Information System")
        self.root.state("zoomed")

        # State variables
        self.current_view = "students"
        self.all_data_cache = []
        self.unfiltered_cache = []
        self.current_page = 1
        self.rows_per_page = Config.DEFAULT_ROWS_PER_PAGE
        self.total_pages = 1

        # Sorting
        self.current_sort_col = None
        self.current_sort_reverse = False

        # For debouncing search
        self._search_after_id = None

        # For debouncing window resize
        self._resize_after_id = None

        # Re-entrancy guard for tree Configure events
        self._configuring = False

        # Hover tracking
        self.current_hover_column = None

        # Bind global events
        self.root.bind("<Button-1>", self.unfocus_widgets)
        self.root.bind("<Control-Right>", lambda e: self.next_page())
        self.root.bind("<Control-Left>", lambda e: self.prev_page())

        # Setup UI
        self.setup_styles()
        self.create_widgets()
        
        # Delay initial load to let UI render properly
        self.root.after(100, lambda: self.switch_view("students"))

        # Set minimum window size once UI has rendered
        self.root.after(200, self._update_min_size)

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
            background=Config.BG_DARK,
            foreground=Config.FG_LIGHT,
            fieldbackground=Config.BG_DARK,
            rowheight=Config.TREE_ROW_HEIGHT,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL)
        )
        style.configure("Treeview.Heading",
            background=Config.BG_INPUT,
            foreground=Config.FG_LIGHT,
            relief="flat",
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold")
        )
        style.map("Treeview",
            background=[('selected', Config.SELECT_BG)],
            foreground=[('selected', Config.FG_LIGHT)]
        )
        style.map("TCombobox",
            fieldbackground=[("readonly", Config.BG_INPUT), ("disabled", "#1a1a1a")],
            background=[("readonly", Config.BG_INPUT)],
            foreground=[("readonly", Config.FG_LIGHT)]
        )
        style.configure("TCombobox",
            relief="flat",
            borderwidth=0,
            padding=5
        )
        self.root.option_add("*TCombobox*Listbox.background", Config.BG_INPUT)
        self.root.option_add("*TCombobox*Listbox.foreground", Config.FG_LIGHT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", Config.SELECT_BG)

    def create_widgets(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=Config.BG_SIDEBAR, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.create_sidebar()

        # Main area
        self.main_window = tk.Frame(self.root, bg=Config.BG_DARK)
        self.main_window.pack(side="right", expand=True, fill="both")

        # Top bar
        self.top_bar = tk.Frame(self.main_window, bg=Config.BG_DARK)
        self.top_bar.pack(side="top", fill="x", padx=20, pady=10)
        self.create_top_bar()

        # Pagination bar – pack at bottom FIRST
        self.pagination = PaginationBar(
            self.main_window,
            on_prev=self.prev_page,
            on_next=self.next_page,
            on_jump=self.jump_to_page,
            bg=Config.BG_DARK
        )
        self.pagination.pack(side="bottom", fill="x", pady=10)

        # Outer frame — what pack sees, fills remaining space
        self.tree_frame = tk.Frame(self.main_window, bg=Config.BG_DARK)
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=(10, 0))

        # Grid layout inside tree_frame: tree row expands, scrollbar row is fixed
        self.tree_frame.grid_rowconfigure(0, weight=1)   # tree — takes all space
        self.tree_frame.grid_rowconfigure(1, weight=0)   # scrollbar — fixed height
        self.tree_frame.grid_columnconfigure(0, weight=1)

        # Treeview in row 0
        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.tag_configure('evenrow', background='#161b22')
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar in row 1 — hidden until needed via grid_remove/grid
        self.h_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal",
                                      command=self.tree.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.h_scroll.grid_remove()   # hidden by default
        self.tree.configure(xscrollcommand=self.h_scroll.set)

        # Single Configure bind handles both resize recalc and scrollbar visibility
        self.tree.bind("<Configure>", self._on_tree_configure)

        # Bindings
        self.tree.bind("<ButtonRelease-1>", self.handle_table_click)
        self.tree.bind("<Motion>", self.on_tree_motion)
        self.tree.bind("<Leave>", self.on_tree_leave)

    def create_sidebar(self):
        tk.Label(
            self.sidebar, text="MENU", fg=Config.FG_MUTED, bg=Config.BG_SIDEBAR,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold")
        ).pack(pady=(30, 10))

        self.nav_buttons = {}
        views = [("Students", "students"), ("Programs", "programs"), ("Colleges", "colleges")]

        for text, v_type in views:
            btn = tk.Button(
                self.sidebar, text=text,
                command=lambda v=v_type: self.switch_view(v),
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE),
                bg=Config.BG_DARK, fg=Config.FG_MUTED,
                activebackground=Config.BG_INPUT, activeforeground=Config.ACCENT,
                relief="flat", bd=0, padx=20, pady=12, anchor="w", cursor="hand2"
            )
            btn.pack(fill="x", padx=10)
            self.nav_buttons[v_type] = btn

    def create_top_bar(self):
        # Search
        search_frame = tk.Frame(self.top_bar, bg=Config.BG_INPUT, bd=0)
        search_frame.pack(side="left", padx=10)

        self.placeholder_text = "Search..."
        self.search_entry = tk.Entry(
            search_frame, font=(Config.FONT_FAMILY, 12), width=40,
            bg=Config.BG_INPUT, fg=Config.FG_LIGHT,
            insertbackground=Config.ACCENT, relief="flat"
        )
        self.search_entry.pack(side="left", padx=(10, 5), pady=8)
        self.search_entry.insert(0, self.placeholder_text)

        self.clear_btn = tk.Button(
            search_frame, text="✕", bg=Config.BG_INPUT, fg=Config.FG_MUTED,
            activebackground=Config.BG_INPUT, activeforeground=Config.ACCENT,
            relief="flat", bd=0, cursor="hand2", font=(Config.FONT_FAMILY, 10, "bold"),
            command=self.clear_search_text
        )

        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_placeholder)
        self.search_entry.bind("<KeyRelease>", self.on_search_keypress)

        # Buttons
        self.add_btn = tk.Button(
            self.top_bar, text="+ Add Record", bg=Config.ACCENT, fg=Config.FG_LIGHT,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            relief="flat", padx=20, pady=8, command=self.open_add_form, cursor="hand2"
        )
        self.add_btn.pack(side="right", padx=5)

        self.import_btn = tk.Button(
            self.top_bar, text="Import CSV", bg=Config.BG_INPUT, fg=Config.FG_LIGHT,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            relief="flat", padx=15, pady=8, command=self.import_csv, cursor="hand2"
        )
        self.import_btn.pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # Data Loading & Pagination
    # ------------------------------------------------------------------
    def load_table_data(self, view_type, refresh_cache=True):
        if refresh_cache:
            self.all_data_cache = db.read_data(Config.CSV_FILES[view_type])
            self.unfiltered_cache = self.all_data_cache[:]
            self._apply_sort()
            self.current_page = 1

        rpp = self.rows_per_page if self.rows_per_page > 0 else Config.DEFAULT_ROWS_PER_PAGE
        total_rows = len(self.all_data_cache)
        self.total_pages = max(1, (total_rows + rpp - 1) // rpp)

        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * rpp
        end_idx = start_idx + rpp
        page_data = self.all_data_cache[start_idx:end_idx]

        # Determine columns
        if self.all_data_cache:
            cols = list(self.all_data_cache[0].keys())
        else:
            cols = Config.DEFAULT_COLUMNS[view_type]

        self.configure_tree_columns(cols)

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert page data
        for i, row in enumerate(page_data):
            tag = ('evenrow',) if i % 2 != 0 else ()
            # Wrap long text
            wrapped_vals = []
            for val in row.values():
                text = str(val)
                if len(text) > 35:
                    text = "\n".join(textwrap.wrap(text, width=35))
                wrapped_vals.append(text)

            self.tree.insert("", "end", values=wrapped_vals + ["Edit", "Delete"],
                             tags=tag)

        # Update pagination bar
        self.pagination.update(
            current_page=self.current_page,
            total_pages=self.total_pages,
            total_rows=total_rows,
            start_idx=start_idx,
            end_idx=end_idx,
            rows_per_page=rpp
        )

    def configure_tree_columns(self, cols):
        all_cols = cols + ["edit", "delete"]
        self.tree.configure(columns=all_cols)
        overflow_active = self.h_scroll.winfo_ismapped()

        # Calculate optimal widths for data columns
        max_lengths = {col: len(col) for col in cols}
        for row in self.all_data_cache:
            for col in cols:
                val_len = len(str(row.get(col, "")))
                if val_len > max_lengths[col]:
                    max_lengths[col] = val_len

        # Set data column headings with sort indicators
        sort_col = self.current_sort_col
        sort_rev = self.current_sort_reverse

        for col in cols:
            display = col.replace("_", " ").upper()
            if col == sort_col:
                display += "  ▼" if sort_rev else "  ▲"
            self.tree.heading(
                col, text=display, anchor="w",
                command=lambda c=col: self.sort_column(c)
            )
            width = min(Config.MAX_COL_WIDTH,
                        max(Config.MIN_COL_WIDTH,
                            max_lengths[col] * Config.TREE_CHAR_WIDTH + 30))
            self.tree.column(col, width=width, minwidth=Config.MIN_COL_WIDTH,
                             anchor="w", stretch=not overflow_active)

        # Edit column – header "Actions"
        self.tree.heading("edit", text="Actions", anchor="center")
        self.tree.column("edit", width=70, minwidth=70, anchor="center", stretch=False)

        # Delete column – header empty
        self.tree.heading("delete", text="", anchor="center")
        self.tree.column("delete", width=70, minwidth=70, anchor="center", stretch=False)

    def calculate_rows_per_page(self):
        self.root.update_idletasks()
        # Read the tree widget's own height — the scrollbar lives in a separate
        # grid row so it never affects this measurement
        available_height = self.tree.winfo_height()
        if available_height <= 1:
            self.rows_per_page = Config.DEFAULT_ROWS_PER_PAGE
            return
        usable_height = available_height - Config.TREE_HEADER_HEIGHT
        self.rows_per_page = max(1, usable_height // Config.TREE_ROW_HEIGHT)

    def on_resize(self, event=None):
        """Debounced handler for tree_frame resize — recalculates rows per page."""
        if self._resize_after_id:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(150, self._apply_resize)

    def _apply_resize(self):
        """Called after resize debounce settles — redraws the current page if rpp changed."""
        old_rpp = self.rows_per_page
        self.calculate_rows_per_page()
        if self.rows_per_page != old_rpp and self.all_data_cache:
            # Clamp current page so it stays valid under the new rpp
            total_rows = len(self.all_data_cache)
            self.total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            self.load_table_data(self.current_view, refresh_cache=False)
        self._update_min_size()

    def _on_tree_configure(self, event=None):
        """Single handler for tree <Configure>.
        Guard prevents re-entrancy: changing column stretch fires Configure
        again, which would cause an infinite loop without this check."""
        if self._configuring:
            return
        self._configuring = True
        try:
            self._update_h_scroll()
            self.on_resize()
        finally:
            self._configuring = False

    def _update_h_scroll(self, event=None):
        """Show/hide the horizontal scrollbar based on whether columns overflow.
        Only toggles stretch and scrollbar visibility — never calls load_table_data,
        which would cause a Configure feedback loop."""
        self.root.update_idletasks()
        tree_width = self.tree.winfo_width()
        if tree_width <= 1 or not self.tree["columns"]:
            return

        total_col_width = sum(
            self.tree.column(col, "width")
            for col in self.tree["columns"]
        )

        overflowing = total_col_width > tree_width
        scroll_visible = self.h_scroll.winfo_ismapped()

        if overflowing and not scroll_visible:
            for col in self.tree["columns"]:
                self.tree.column(col, stretch=False)
            self.h_scroll.grid()

        elif not overflowing and scroll_visible:
            for col in (c for c in self.tree["columns"] if c not in ("edit", "delete")):
                self.tree.column(col, stretch=True)
            self.h_scroll.grid_remove()

    def _update_min_size(self):
        """Enforce a minimum window size: no narrower than MIN_TOTAL_WIDTH,
        no shorter than what's needed to show MIN_ROWS_VISIBLE table rows."""
        self.root.update_idletasks()

        top_bar_h = self.top_bar.winfo_height()
        pagination_h = self.pagination.winfo_height()
        scroll_h = self.h_scroll.winfo_height() if self.h_scroll.winfo_ismapped() else 0
        chrome_h = top_bar_h + pagination_h + scroll_h + 40  # 40px padding buffer
        min_h = chrome_h + Config.TREE_HEADER_HEIGHT + (Config.MIN_ROWS_VISIBLE * Config.TREE_ROW_HEIGHT)

        self.root.minsize(Config.MIN_TOTAL_WIDTH, min_h)

    def _apply_sort(self):
        """Sort the current cache based on self.current_sort_col and self.current_sort_reverse."""
        if not self.all_data_cache or not self.current_sort_col:
            return
        col = self.current_sort_col
        reverse = self.current_sort_reverse
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

    # ------------------------------------------------------------------
    # Pagination Actions
    # ------------------------------------------------------------------
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_table_data(self.current_view, refresh_cache=False)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_table_data(self.current_view, refresh_cache=False)

    def jump_to_page(self, page):
        self.current_page = page
        self.load_table_data(self.current_view, refresh_cache=False)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------
    def sort_column(self, col):
        if col == "actions" or not self.all_data_cache:
            return

        if col == self.current_sort_col:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_col = col
            self.current_sort_reverse = False

        self._apply_sort()
        self.load_table_data(self.current_view, refresh_cache=False)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def on_search_keypress(self, event=None):
        query = self.search_entry.get()
        if query and query != self.placeholder_text:
            if not self.clear_btn.winfo_ismapped():
                self.clear_btn.pack(side="right", padx=10)
        else:
            self.clear_btn.pack_forget()

        if self._search_after_id:
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(300, self.filter_search)

    def filter_search(self):
        query = self.search_entry.get().strip().lower()
        if not query or query == self.placeholder_text.lower():
            self.all_data_cache = self.unfiltered_cache[:]
        else:
            self.all_data_cache = [
                row for row in self.unfiltered_cache
                if query in " ".join(map(str, row.values())).lower()
            ]
        self._apply_sort()
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

    def clear_search_text(self):
        self.search_entry.delete(0, tk.END)
        self.clear_btn.pack_forget()
        self.root.focus_set()
        self.load_table_data(self.current_view, refresh_cache=True)

    # ------------------------------------------------------------------
    # View Switching
    # ------------------------------------------------------------------
    def switch_view(self, view_type):
        self.current_view = view_type
        self.add_btn.config(text=f"+ Add {view_type[:-1].capitalize()}")

        for v, btn in self.nav_buttons.items():
            if v == view_type:
                btn.config(fg=Config.ACCENT, bg=Config.BG_INPUT)
            else:
                btn.config(fg=Config.FG_MUTED, bg=Config.BG_DARK)

        self.calculate_rows_per_page()
        self.load_table_data(view_type)

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------
    def open_add_form(self, edit_mode=False, item_id=None, current_vals=None):
        edit_id = item_id.strip() if edit_mode and item_id else None

        self.form_window = tk.Toplevel(self.root)
        self.form_window.title("Edit Record" if edit_mode else "Add New Record")
        self.form_window.geometry("500x650")
        self.form_window.configure(bg=Config.BG_DARK)
        self.form_window.grab_set()
        self.form_window.bind("<Escape>", lambda e: self.form_window.destroy())

        # Header
        header_frame = tk.Frame(self.form_window, bg=Config.BG_DARK)
        header_frame.pack(fill="x", padx=40, pady=(30, 10))
        title_text = f"{'Edit' if edit_mode else 'Add New'} {self.current_view[:-1].capitalize()}"
        tk.Label(
            header_frame, text=title_text, fg=Config.FG_LIGHT, bg=Config.BG_DARK,
            font=(Config.FONT_FAMILY, 16, "bold")
        ).pack(side="left")

        # Input fields
        self.inputs = {}
        fields = Config.FORM_FIELDS[self.current_view]

        for i, field in enumerate(fields):
            frame = tk.Frame(self.form_window, bg=Config.BG_DARK)
            frame.pack(fill="x", padx=40, pady=8)

            tk.Label(
                frame, text=field.upper(), fg=Config.FG_MUTED, bg=Config.BG_DARK,
                font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL, "bold")
            ).pack(anchor="w", pady=(0, 5))

            if field in ["Gender", "Year Level"]:
                values = Config.GENDER_OPTIONS if field == "Gender" else Config.YEAR_OPTIONS
                entry = ttk.Combobox(frame, values=values, state="readonly")
            else:
                entry = tk.Entry(
                    frame, bg=Config.BG_INPUT, fg=Config.FG_LIGHT,
                    insertbackground=Config.ACCENT, relief="flat",
                    font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE), bd=8
                )

            entry.pack(fill="x")

            if edit_mode and current_vals:
                if isinstance(entry, ttk.Combobox):
                    entry.set(current_vals[i])
                else:
                    entry.insert(0, current_vals[i])

            self.inputs[field] = entry

        # Footer buttons
        footer = tk.Frame(self.form_window, bg=Config.BG_DARK)
        footer.pack(fill="x", padx=40, pady=30)

        tk.Button(
            footer, text="Cancel", bg=Config.BG_DARK, fg=Config.FG_MUTED,
            relief="flat", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            command=self.form_window.destroy, cursor="hand2"
        ).pack(side="left")

        tk.Button(
            footer, text="Save Record", bg=Config.ACCENT, fg=Config.FG_LIGHT,
            relief="flat", font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
            padx=25, pady=8, command=lambda: self.submit_data(edit_id), cursor="hand2"
        ).pack(side="right")

    def submit_data(self, edit_target_id=None):
        try:
            raw_data = {field: widget.get().strip() for field, widget in self.inputs.items()}

            if any(val == "" for val in raw_data.values()):
                messagebox.showwarning("Input Error", "All fields are required.")
                return

            mapping = Config.FIELD_TO_COLUMN[self.current_view]
            final_dict = {mapping[k]: v for k, v in raw_data.items()}
            filename = Config.CSV_FILES[self.current_view]

            if edit_target_id:
                # ----------------------------------------------------------
                # EDIT MODE — validate first, then write
                # ----------------------------------------------------------
                old_pk = edit_target_id
                new_pk = list(final_dict.values())[0]
                pk_col = Config.PK_COLUMN[self.current_view]

                # If PK changed, ensure the new one isn't already taken
                if old_pk != new_pk:
                    if not db.is_unique_excluding(filename, pk_col, new_pk, old_pk):
                        messagebox.showerror("Validation Error",
                            f"{pk_col.replace('_', ' ').title()} '{new_pk}' already exists.")
                        return

                # Validate FK relationships before touching the file
                if self.current_view == "programs":
                    college_code = final_dict.get("college_code")
                    if not db.parent_exists("colleges.csv", "college_code", college_code):
                        messagebox.showerror("Validation Error",
                            f"College '{college_code}' does not exist.")
                        return

                elif self.current_view == "students":
                    import re
                    sid = final_dict.get("student_id", "")
                    if not re.match(r"^\d{4}-\d{4}$", sid):
                        messagebox.showerror("Validation Error",
                            "Student ID must be in YYYY-NNNN format.")
                        return
                    if final_dict.get("gender") not in db.GENDER_OPTIONS:
                        messagebox.showerror("Validation Error", "Gender must be M, F, or O.")
                        return
                    prog = final_dict.get("program_code")
                    if not db.parent_exists("programs.csv", "program_code", prog):
                        messagebox.showerror("Validation Error",
                            f"Program '{prog}' does not exist.")
                        return

                # All checks passed — write to disk
                if self.current_view == "colleges":
                    db.update_college_cascade(old_pk, final_dict)
                elif self.current_view == "programs":
                    db.update_program_cascade(old_pk, final_dict)
                else:
                    db.update_row(filename, old_pk, final_dict)

            else:
                # ----------------------------------------------------------
                # ADD MODE — validate first, then append
                # ----------------------------------------------------------
                if self.current_view == "colleges":
                    success, msg = db.validate_college(final_dict["college_code"])
                elif self.current_view == "programs":
                    success, msg = db.validate_program(
                        final_dict["program_code"], final_dict["college_code"])
                else:
                    success, msg = db.validate_student(
                        final_dict["student_id"], final_dict["gender"], final_dict["program_code"])

                if not success:
                    messagebox.showerror("Validation Error", msg)
                    return

                db.append_row(filename, list(final_dict.keys()), final_dict)

            # Shared success path
            messagebox.showinfo("Success",
                f"{self.current_view[:-1].capitalize()} saved successfully.")
            self.form_window.destroy()
            self.load_table_data(self.current_view, refresh_cache=True)

        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An error occurred:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def handle_table_click(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item:
            return

        cols = self.tree["columns"]
        col_index = int(column.replace("#", "")) - 1
        row_vals = self.tree.item(item, "values")
        data_cols_count = len(cols) - 2

        if col_index == data_cols_count:
            # Look up raw record from cache by PK to avoid wrapped display values
            pk = str(row_vals[0]).strip()
            pk_col = Config.PK_COLUMN[self.current_view]
            raw_record = next(
                (r for r in self.all_data_cache
                 if str(r.get(pk_col, "")).strip() == pk),
                None
            )
            if raw_record:
                self.open_add_form(
                    edit_mode=True,
                    item_id=pk,
                    current_vals=list(raw_record.values())
                )
        elif col_index == data_cols_count + 1:
            self.confirm_single_delete(item, row_vals[0])

    def confirm_single_delete(self, item, pk):
        pk = str(pk).strip()
        if not messagebox.askyesno("Confirm Delete", f"Delete record '{pk}'?"):
            return

        if self.current_view == "colleges":
            db.delete_college_cascade(pk)
        elif self.current_view == "programs":
            db.delete_program_cascade(pk)
        else:
            db.delete_record(
                Config.CSV_FILES[self.current_view],
                Config.PK_COLUMN[self.current_view],
                pk
            )

        self.load_table_data(self.current_view, refresh_cache=True)

    # ------------------------------------------------------------------
    # Import CSV
    # ------------------------------------------------------------------
    def import_csv(self):
        required_headers = Config.DEFAULT_COLUMNS[self.current_view]
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
                    messagebox.showerror("Error", "The selected file is empty or invalid.")
                    return

                missing = [h for h in required_headers if h not in file_headers]
                extra = [h for h in file_headers if h not in required_headers]

                if missing:
                    error_msg = f"Validation Failed!\n\nMissing Columns: {', '.join(missing)}"
                    if extra:
                        error_msg += f"\n\nUnknown columns found: {', '.join(extra)}"
                    error_msg += f"\n\nPlease ensure your CSV headers match: {', '.join(required_headers)}"
                    messagebox.showerror("Header Mismatch", error_msg)
                    return

                new_records = list(reader)
                if not new_records:
                    messagebox.showwarning("Warning", "No data found in the CSV file.")
                    return

                if messagebox.askyesno("Confirm Import", f"Import {len(new_records)} records into {self.current_view}?"):
                    filename = Config.CSV_FILES[self.current_view]
                    db.save_data(filename, required_headers, new_records)
                    self.load_table_data(self.current_view, refresh_cache=True)
                    messagebox.showinfo("Success", f"Successfully imported {len(new_records)} records.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred: {str(e)}")

    # ------------------------------------------------------------------
    # Hover Effects 
    # ------------------------------------------------------------------
    def on_tree_motion(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            self.on_tree_leave()
            return

        col_index = int(column.replace("#", "")) - 1
        cols = self.tree["columns"]
        data_cols_count = len(cols) - 2

        # Change cursor if over action columns
        if col_index in (data_cols_count, data_cols_count + 1):
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")

    def on_tree_leave(self, event=None):
        self.tree.config(cursor="")

    # ------------------------------------------------------------------
    # Utility / Event Handlers
    # ------------------------------------------------------------------
    def unfocus_widgets(self, event):
        clicked = event.widget
        if clicked not in (self.search_entry, self.pagination.jump_entry if self.pagination else None):
            self.root.focus_set()
        if hasattr(self, 'tree') and clicked != self.tree:
            self.tree.selection_remove(self.tree.selection())