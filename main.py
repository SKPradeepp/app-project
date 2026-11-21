"""
Tamil Movie & OTT Discovery Management System
Python + Tkinter + MySQL
Run: python main.py
"""
import hashlib
import hmac
import tkinter as tk
from tkinter import ttk, messagebox
from database import initialize_database, fetch_all, execute

BG = "#101827"
PANEL = "#182437"
ACCENT = "#e5a93d"
TEXT = "#f4f6f8"
MUTED = "#aab6c5"

def hash_password(password, salt=None):
    salt = salt or __import__("secrets").token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${digest}"

def verify_password(password, stored):
    try:
        salt, digest = stored.split("$", 1)
        return hmac.compare_digest(hash_password(password, salt).split("$", 1)[1], digest)
    except ValueError:
        return False

class MovieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tamil Movie & OTT Discovery")
        self.geometry("1120x720")
        self.minsize(960, 620)
        self.configure(bg=BG)
        self.user = None
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview", background=PANEL, foreground=TEXT,
                             fieldbackground=PANEL, rowheight=29, borderwidth=0)
        self.style.configure("Treeview.Heading", background="#26364d",
                             foreground=TEXT, font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", "#38577a")])
        self.style.configure("TCombobox", fieldbackground=PANEL, background=PANEL)
        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def heading(self, parent, title, subtitle=""):
        tk.Label(parent, text=title, bg=parent["bg"], fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=24, pady=(20, 3))
        if subtitle:
            tk.Label(parent, text=subtitle, bg=parent["bg"], fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=26, pady=(0, 14))

    def entry(self, parent, label, show=None):
        tk.Label(parent, text=label, bg=parent["bg"], fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(8, 3))
        item = tk.Entry(parent, font=("Segoe UI", 11), bg="#26364d", fg=TEXT,
                        insertbackground=TEXT, relief="flat", show=show)
        item.pack(fill="x", ipady=9)
        return item

    def button(self, parent, text, command, secondary=False):
        return tk.Button(parent, text=text, command=command, cursor="hand2",
                         bg="#31445e" if secondary else ACCENT,
                         fg=TEXT if secondary else "#17202d",
                         activebackground="#f2bd58", activeforeground="#17202d",
                         font=("Segoe UI", 10, "bold"), relief="flat",
                         padx=15, pady=9)

    def show_login(self):
        self.clear()
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=.5, rely=.5, anchor="center", width=430)
        tk.Label(wrap, text="CINEMA / FINDER", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(0, 8))
        tk.Label(wrap, text="Tamil Movie & OTT", bg=BG, fg=TEXT,
                 font=("Segoe UI", 27, "bold")).pack()
        tk.Label(wrap, text="Discover • Organise • Watch", bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(pady=(4, 20))
        card = tk.Frame(wrap, bg=PANEL, padx=28, pady=24)
        card.pack(fill="x")
        email = self.entry(card, "Email address")
        password = self.entry(card, "Password", "•")
        def login():
            try:
                rows = fetch_all("SELECT * FROM users WHERE email=%s", (email.get().strip(),))
                if rows and verify_password(password.get(), rows[0]["password_hash"]):
                    self.user = rows[0]
                    self.show_home()
                else:
                    messagebox.showerror("Login failed", "Invalid email or password.")
            except Exception as exc:
                messagebox.showerror("Database error", str(exc))
        self.button(card, "Sign in", login).pack(fill="x", pady=(18, 8))
        self.button(card, "Create a new account", self.show_register, True).pack(fill="x")
        tk.Label(wrap, text="Academic demonstration project • Verify streaming availability independently",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=400).pack(pady=15)

    def show_register(self):
        self.clear()
        wrap = tk.Frame(self, bg=BG)
        wrap.place(relx=.5, rely=.5, anchor="center", width=450)
        tk.Label(wrap, text="Create your account", bg=BG, fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(pady=15)
        card = tk.Frame(wrap, bg=PANEL, padx=28, pady=22)
        card.pack(fill="x")
        name = self.entry(card, "Full name")
        email = self.entry(card, "Email address")
        pw = self.entry(card, "Password (minimum 6 characters)", "•")
        def register():
            if not name.get().strip() or not email.get().strip() or len(pw.get()) < 6:
                messagebox.showwarning("Check details", "Enter all fields and a password of at least 6 characters.")
                return
            try:
                execute("INSERT INTO users(full_name,email,password_hash) VALUES(%s,%s,%s)",
                        (name.get().strip(), email.get().strip().lower(), hash_password(pw.get())))
                messagebox.showinfo("Account created", "Your account is ready. Please sign in.")
                self.show_login()
            except Exception as exc:
                messagebox.showerror("Registration failed", str(exc))
        self.button(card, "Register", register).pack(fill="x", pady=(18, 8))
        self.button(card, "Back to sign in", self.show_login, True).pack(fill="x")

    def show_home(self):
        self.clear()
        top = tk.Frame(self, bg="#0c1420", height=64)
        top.pack(fill="x")
        tk.Label(top, text="CINEMA / FINDER", bg="#0c1420", fg=ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=24, pady=18)
        tk.Label(top, text=f"Welcome, {self.user['full_name']}", bg="#0c1420",
                 fg=TEXT, font=("Segoe UI", 10)).pack(side="right", padx=18)
        self.button(top, "Sign out", self.show_login, True).pack(side="right", padx=8, pady=10)
        nav = tk.Frame(self, bg=PANEL, width=190)
        nav.pack(side="left", fill="y")
        content = tk.Frame(self, bg=BG)
        content.pack(side="right", fill="both", expand=True)
        self.content = content
        for label, fn in [
            ("Dashboard", self.show_dashboard),
            ("Discover Movies", self.show_movies),
            ("Add Movie", self.show_add_movie),
            ("My Watchlist", self.show_watchlist),
        ]:
            self.button(nav, label, fn, True).pack(fill="x", padx=13, pady=(18 if label=="Dashboard" else 3, 3))
        tk.Label(nav, text="DATA NOTE\nStreaming catalogues\nchange by region and date.\nConfirm on the provider.",
                 bg=PANEL, fg=MUTED, justify="left", font=("Segoe UI", 8)).pack(side="bottom", padx=14, pady=20)
        self.show_dashboard()

    def show_dashboard(self):
        for w in self.content.winfo_children():
            w.destroy()

        self.heading(
            self.content,
            "Your movie dashboard",
            "A quick overview of the catalogue and your watch activity."
        )

        try:
            movies = fetch_all(
                "SELECT COUNT(*) AS n FROM movies"
            )[0]["n"]

            users = fetch_all(
                "SELECT COUNT(*) AS n FROM users"
            )[0]["n"]

            watch = fetch_all(
                "SELECT COUNT(*) AS n FROM watchlist WHERE user_id=%s",
                (self.user["user_id"],)
            )[0]["n"]

            watched = fetch_all(
                "SELECT COUNT(*) AS n FROM watchlist WHERE user_id=%s AND status='Watched'",
                (self.user["user_id"],)
            )[0]["n"]

            plan = fetch_all(
            "SELECT COUNT(*) AS n FROM watchlist WHERE user_id=%s AND status='Plan to Watch'",
            (self.user["user_id"],)
            )[0]["n"]

        # Dashboard statistics
            stats = [
            ("MOVIES IN CATALOGUE", movies),
            ("REGISTERED USERS", users),
            ("MY WATCHLIST", watch),
            ("MARKED WATCHED", watched),
            ("PLAN TO WATCH", plan)
            ]

            row = tk.Frame(self.content, bg=BG)
            row.pack(fill="x", padx=15, pady=20)

            for title, value in stats:
                box = tk.Frame(row, bg=PANEL, padx=12, pady=20)
                box.pack(
                side="left",
                fill="both",
                expand=True,
                padx=4
            )

                tk.Label(
                box,
                text=title,
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 8, "bold"),
                wraplength=130
                ).pack(anchor="w")

                tk.Label(
                box,
                text=str(value),
                bg=PANEL,
                fg=ACCENT,
                font=("Segoe UI", 25, "bold")
                ).pack(anchor="w", pady=8)

        # Recently added movies
            tk.Label(
            self.content,
            text="Recently added",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(anchor="w", padx=25, pady=(12, 8))

            rows = fetch_all("""
            SELECT movie_id, title, genre, release_year
            FROM movies
            ORDER BY movie_id DESC
            LIMIT 6
        """)

            self.make_tree(
            self.content,
            ("ID", "Title", "Genre", "Year"),
            rows,
            ("movie_id", "title", "genre", "release_year")
        )

        except Exception as exc:
            messagebox.showerror("Dashboard error", str(exc))

    def make_tree(self, parent, headings, rows, keys):
        frame = tk.Frame(parent, bg=BG); frame.pack(fill="both", expand=True, padx=24, pady=8)
        tree = ttk.Treeview(frame, columns=headings, show="headings")
        for h in headings:
            tree.heading(h, text=h); tree.column(h, width=150, anchor="w")
        for row in rows:
            tree.insert("", "end", values=tuple(row.get(k, "") if row.get(k) is not None else "" for k in keys))
        tree.pack(fill="both", expand=True)
        return tree

    def show_movies(self):
        for w in self.content.winfo_children(): w.destroy()
        self.heading(self.content, "Discover movies", "Search the catalogue by title, genre, language or year.")
        bar = tk.Frame(self.content, bg=BG); bar.pack(fill="x", padx=24)
        search = tk.Entry(bar, bg=PANEL, fg=TEXT, insertbackground=TEXT, relief="flat", font=("Segoe UI", 11))
        search.pack(side="left", fill="x", expand=True, ipady=9)
        genre = ttk.Combobox(bar, values=["All genres","Action","Comedy","Drama","Thriller","Science Fiction","Romance"], state="readonly", width=18)
        genre.set("All genres"); genre.pack(side="left", padx=8, ipady=5)
        holder = tk.Frame(self.content, bg=BG); holder.pack(fill="both", expand=True)
        def load():
            term = f"%{search.get().strip()}%"
            sql = """SELECT movie_id,title,language,genre,director,release_year,rating
                     FROM movies WHERE (title LIKE %s OR genre LIKE %s OR director LIKE %s OR language LIKE %s)"""
            params = [term,term,term,term]
            if genre.get() != "All genres":
                sql += " AND genre=%s"; params.append(genre.get())
            sql += " ORDER BY title"
            try:
                rows = fetch_all(sql, tuple(params))
                for w in holder.winfo_children(): w.destroy()
                tree = self.make_tree(
                    holder,
                    ("ID", "Title", "Language", "Genre", "Director", "Year", "Rating"),
                    rows,
                    ("movie_id", "title", "language", "genre", "director", "release_year", "rating")
                )

                def open_details(event):
                    selected = tree.selection()

                    if selected:
                        movie_id = tree.item(selected[0], "values")[0]
                        self.show_movie_details(int(movie_id))

                tree.bind("<Double-1>", open_details)
            except Exception as exc: messagebox.showerror("Search error", str(exc))
        self.button(bar, "Search", load).pack(side="left", padx=5)
        self.button(bar, "Refresh", lambda: (search.delete(0,"end"), genre.set("All genres"), load()), True).pack(side="left")
        actions = tk.Frame(self.content, bg=BG); actions.pack(fill="x", padx=24, pady=10)
        movie_id = tk.Entry(actions, width=10, bg=PANEL, fg=TEXT, relief="flat")
        movie_id.pack(side="left", ipady=7)
        tk.Label(actions, text="Movie ID", bg=BG, fg=MUTED).pack(side="left", padx=6)
        def add_watch():
            try:
                execute("INSERT INTO watchlist(user_id,movie_id) VALUES(%s,%s)",
                        (self.user["user_id"], int(movie_id.get())))
                messagebox.showinfo("Watchlist", "Movie added to your watchlist.")
            except Exception as exc: messagebox.showerror("Could not add", str(exc))
        self.button(actions, "Add ID to watchlist", add_watch).pack(side="left", padx=8)
        self.edit_id = tk.Entry(actions, width=10, bg=PANEL, fg=TEXT, relief="flat")
        self.edit_id.pack(side="left", padx=5, ipady=7)

        self.button(actions, "Edit Movie", self.edit_movie).pack(side="left", padx=5)
        load()

    def show_movie_details(self, movie_id):
        try:
            rows = fetch_all(
            "SELECT * FROM movies WHERE movie_id=%s",
            (movie_id,)
        )

            if not rows:
                messagebox.showerror("Error", "Movie not found.")
                return

            movie = rows[0]

            window = tk.Toplevel(self)
            window.title("Movie Details")
            window.geometry("550x600")
            window.configure(bg=BG)

            tk.Label(
            window,
            text=movie["title"],
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 24, "bold")
            ).pack(pady=20)

            details = [
            ("Language", movie["language"]),
            ("Genre", movie["genre"]),
            ("Director", movie["director"]),
            ("Cast", movie["cast_members"]),
            ("Release Year", movie["release_year"]),
            ("Duration", str(movie["duration_minutes"]) + " minutes"
             if movie["duration_minutes"] else ""),
            ("Rating", str(movie["rating"]) + "/10")
        ]

            for label, value in details:
                frame = tk.Frame(window, bg=PANEL, padx=15, pady=10)
                frame.pack(fill="x", padx=25, pady=4)

                tk.Label(
                frame,
                text=label,
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 10, "bold")
                ).pack(anchor="w")

                tk.Label(
                frame,
                text=str(value or "Not available"),
                bg=PANEL,
                fg=TEXT,
                font=("Segoe UI", 11),
                wraplength=470,
                justify="left"
            ).pack(anchor="w")

            tk.Label(
            window,
            text="Synopsis",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 13, "bold")
            ).pack(anchor="w", padx=25, pady=(15, 5))

            synopsis = tk.Label(
            window,
            text=movie["synopsis"] or "No synopsis available.",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 11),
            wraplength=480,
            justify="left",
            padx=15,
            pady=15
            )
            synopsis.pack(fill="x", padx=25)

        except Exception as exc:
            messagebox.showerror("Movie Details Error", str(exc))

    def edit_movie(self):
        movie_id = self.edit_id.get().strip()

        if not movie_id.isdigit():
            messagebox.showerror("Error", "Enter a valid Movie ID.")
            return

        try:
            rows = fetch_all(
                "SELECT * FROM movies WHERE movie_id=%s",
                (int(movie_id),)
            )

            if not rows:
                messagebox.showerror("Error", "Movie not found.")
                return

            movie = rows[0]

            window = tk.Toplevel(self)
            window.title("Edit Movie")
            window.geometry("500x650")
            window.configure(bg=BG)

            tk.Label(
            window, text="Edit Movie Details",
            bg=BG, fg=ACCENT,
            font=("Segoe UI", 20, "bold")
            ).pack(pady=15)

            fields = [
            ("Title", "title"),
            ("Language", "language"),
            ("Genre", "genre"),
            ("Director", "director"),
            ("Cast", "cast_members"),
            ("Release Year", "release_year"),
            ("Duration (minutes)", "duration_minutes"),
            ("Rating", "rating")
            ]

            entries = {}

            for label, key in fields:
                tk.Label(
                window, text=label,
                bg=BG, fg=TEXT
                ).pack(anchor="w", padx=30)

                entry = tk.Entry(
                window, bg=PANEL, fg=TEXT,
                insertbackground=TEXT,
                relief="flat"
                )
                entry.pack(fill="x", padx=30, pady=5, ipady=6)

                entry.insert(0, str(movie[key] or ""))
                entries[key] = entry

            def update_movie():
                try:
                    execute(
                        """UPDATE movies SET
                        title=%s, language=%s, genre=%s,
                        director=%s, cast_members=%s,
                        release_year=%s, duration_minutes=%s,
                        rating=%s
                        WHERE movie_id=%s""",
                        (
                            entries["title"].get(),
                            entries["language"].get(),
                            entries["genre"].get(),
                            entries["director"].get(),
                            entries["cast_members"].get(),
                            int(entries["release_year"].get()),
                            int(entries["duration_minutes"].get()),
                            float(entries["rating"].get()),
                            int(movie_id)
                        )
                    )

                    messagebox.showinfo("Success", "Movie updated successfully.")
                    window.destroy()
                    self.show_movies()

                except ValueError:
                    messagebox.showerror("Error", "Enter valid numbers for year, duration and rating.")

                except Exception as exc:
                    messagebox.showerror("Update Error", str(exc))

            self.button(window, "Update Movie", update_movie).pack(pady=20)

        except Exception as exc:
            messagebox.showerror("Edit Error", str(exc))

    def show_add_movie(self):
        for w in self.content.winfo_children(): w.destroy()
        self.heading(self.content, "Add a movie", "Enter catalogue details. All fields except title are optional.")
        form = tk.Frame(self.content, bg=PANEL, padx=24, pady=18)
        form.pack(fill="x", padx=28, pady=8)
        fields = {}
        specs = [("Title","title"),("Language","language"),("Genre","genre"),("Director","director"),
                 ("Cast members","cast_members"),("Release year","release_year"),
                 ("Duration in minutes","duration_minutes"),("Rating (0–10)","rating")]
        for i,(label,key) in enumerate(specs):
            r,c = divmod(i,2)
            cell = tk.Frame(form, bg=PANEL); cell.grid(row=r, column=c, sticky="ew", padx=10, pady=6)
            tk.Label(cell, text=label, bg=PANEL, fg=MUTED).pack(anchor="w")
            ent = tk.Entry(cell, bg="#26364d", fg=TEXT, insertbackground=TEXT, relief="flat")
            ent.pack(fill="x", ipady=7); fields[key]=ent
        form.columnconfigure(0, weight=1); form.columnconfigure(1, weight=1)
        tk.Label(form, text="Synopsis", bg=PANEL, fg=MUTED).grid(row=4,column=0,sticky="w",padx=10,pady=(8,2))
        synopsis = tk.Text(form, height=4, bg="#26364d", fg=TEXT, insertbackground=TEXT, relief="flat")
        synopsis.grid(row=5,column=0,columnspan=2,sticky="ew",padx=10)
        def save():
            if not fields["title"].get().strip():
                messagebox.showwarning("Missing title", "Movie title is required."); return
            try:
                year = int(fields["release_year"].get()) if fields["release_year"].get().strip() else None
                duration = int(fields["duration_minutes"].get()) if fields["duration_minutes"].get().strip() else None
                rating = float(fields["rating"].get()) if fields["rating"].get().strip() else 0.0
                if not 0 <= rating <= 10: raise ValueError("Rating must be between 0 and 10.")
                execute("""INSERT INTO movies(title,language,genre,director,cast_members,release_year,
                           duration_minutes,rating,synopsis) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (fields["title"].get().strip(), fields["language"].get().strip() or "Tamil",
                         fields["genre"].get().strip(), fields["director"].get().strip(),
                         fields["cast_members"].get().strip(), year, duration, rating, synopsis.get("1.0","end").strip()))
                messagebox.showinfo("Saved", "Movie added to the catalogue.")
                self.show_movies()
            except Exception as exc: messagebox.showerror("Invalid details", str(exc))
        self.button(self.content, "Save movie", save).pack(anchor="e", padx=30, pady=15)

    def show_watchlist(self):
        for w in self.content.winfo_children(): w.destroy()
        self.heading(self.content, "My watchlist", "Keep track of movies you plan to watch and have watched.")
        rows = fetch_all("""SELECT w.watchlist_id,m.title,m.genre,m.release_year,w.status
                            FROM watchlist w JOIN movies m ON w.movie_id=m.movie_id
                            WHERE w.user_id=%s ORDER BY w.added_at DESC""", (self.user["user_id"],))
        tree = self.make_tree(self.content, ("List ID","Title","Genre","Year","Status"),
                              rows, ("watchlist_id","title","genre","release_year","status"))
        bar = tk.Frame(self.content, bg=BG); bar.pack(fill="x", padx=24, pady=12)
        item = tk.Entry(bar, width=12, bg=PANEL, fg=TEXT, relief="flat")
        item.pack(side="left", ipady=7)
        tk.Label(bar, text="Watchlist ID", bg=BG, fg=MUTED).pack(side="left", padx=6)
        def mark():
            try:
                execute("UPDATE watchlist SET status='Watched' WHERE watchlist_id=%s AND user_id=%s",
                        (int(item.get()), self.user["user_id"]))
                self.show_watchlist()
            except Exception as exc: messagebox.showerror("Update failed", str(exc))
        def remove():
            try:
                execute("DELETE FROM watchlist WHERE watchlist_id=%s AND user_id=%s",
                        (int(item.get()), self.user["user_id"]))
                self.show_watchlist()
            except Exception as exc: messagebox.showerror("Remove failed", str(exc))
        self.button(bar, "Mark watched", mark).pack(side="left", padx=7)
        self.button(bar, "Remove", remove, True).pack(side="left")

if __name__ == "__main__":
    try:
        initialize_database()
        MovieApp().mainloop()
    except Exception as error:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Startup error", str(error))
