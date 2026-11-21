"""
Database helper for Tamil Movie & OTT Discovery Management System.
Configure MySQL credentials in config.py before running the application.
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        raise RuntimeError(
            "Could not connect to MySQL. Check that MySQL Server is running "
            "and verify DB_CONFIG in config.py. Original error: " + str(exc)
        ) from exc

def initialize_database():
    """Create the required tables."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(256) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(180) NOT NULL,
            language VARCHAR(60) DEFAULT 'Tamil',
            genre VARCHAR(100),
            director VARCHAR(120),
            cast_members VARCHAR(500),
            release_year INT,
            duration_minutes INT,
            synopsis TEXT,
            rating DECIMAL(3,1) DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS platforms (
            platform_id INT AUTO_INCREMENT PRIMARY KEY,
            platform_name VARCHAR(100) NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movie_platform (
            movie_id INT NOT NULL,
            platform_id INT NOT NULL,
            availability_note VARCHAR(150),
            PRIMARY KEY (movie_id, platform_id),
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            movie_id INT NOT NULL,
            status ENUM('Plan to Watch','Watched') DEFAULT 'Plan to Watch',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_movie (user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
        )
    """)

    for name in ("Netflix", "Amazon Prime Video", "JioHotstar", "ZEE5", "SonyLIV", "Sun NXT"):
        cur.execute(
            "INSERT IGNORE INTO platforms(platform_name) VALUES (%s)",
            (name,)
        )

    conn.commit()
    cur.close()
    conn.close()
    
def fetch_all(query, params=()):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id
