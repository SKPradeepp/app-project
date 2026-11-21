# Tamil Movie & OTT Discovery Management System

A desktop catalogue and personal watchlist application built using Python, Tkinter and MySQL.

## Features
- User registration and login (PBKDF2-HMAC password hashing)
- Movie catalogue with search by title, genre, director and language
- Add movie records
- Personal watchlist and watched status
- Dashboard summary
- MySQL relational schema with foreign keys

## Requirements
- Python 3.10 or later
- MySQL Server 8.x
- MySQL Workbench (recommended)
- VS Code or another Python editor

## Setup
1. Install and start MySQL Server.
2. Open `config.py` and replace `YOUR_MYSQL_PASSWORD` with your local MySQL password.
3. Open a terminal in this project folder.
4. Install dependencies:
   `python -m pip install -r requirements.txt`
5. Run:
   `python main.py`

The application creates `movie_ott_db` and its tables automatically on first launch.

## First use
1. Choose **Create a new account**.
2. Register with a name, email and password.
3. Sign in.
4. Add sample movies using **Add Movie**.
5. Discover movies and add a movie ID to your watchlist.
6. In **My Watchlist**, enter the List ID to mark a title as watched or remove it.

## Important notes
- The platform table is prepared for OTT catalogue information. Streaming rights vary by country and date; confirm availability directly with each provider.
- This is an academic prototype. It does not scrape OTT services, stream copyrighted movies, or process payments.
- For a production deployment, add role-based permissions, password reset, stronger input validation, backups, audit logs and secure secret management.
