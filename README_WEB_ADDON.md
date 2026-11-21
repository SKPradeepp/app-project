# Web interface add-on

This folder adds a Flask + HTML/CSS/JavaScript web interface alongside the existing Tkinter desktop application. Both interfaces use the same `database.py`, `config.py`, MySQL database (`movie_ott_db`), and password hashing format.

## Run the existing desktop application

```bash
python main.py
```

## Run the web application

1. Open this project folder in VS Code.
2. Install the requirements (Flask is now included):

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure MySQL Server is running and `config.py` contains your local MySQL connection settings.
4. Start the web application:

   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.
6. Sign in using an account already registered in the Tkinter application, or create an account in the web app. Accounts and movie/watchlist data are shared.

Stop the web server with `Ctrl+C` in the terminal. Run `main.py` and `app.py` separately; do not start both in the same terminal process.

## Project architecture

- **Desktop frontend:** Tkinter (`main.py`)
- **Web frontend:** HTML templates, CSS and JavaScript (`templates/`, `static/`)
- **Web backend:** Flask (`app.py`)
- **Database layer:** MySQL Connector/Python (`database.py`)
- **Database:** MySQL (`movie_ott_db`)

The web app deliberately has no movie-delete feature. Removing a watchlist entry only removes that user's personal list entry, not the movie from the catalogue. OTT platform management remains outside the current feature scope.

For a public deployment, set a strong random `FLASK_SECRET_KEY` environment variable, use a dedicated MySQL user instead of root, and run with debug mode disabled behind a production WSGI server. This is intended for local academic demonstration.
