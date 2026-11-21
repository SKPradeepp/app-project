CREATE DATABASE IF NOT EXISTS movie_ott_db;
USE movie_ott_db;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(256) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

CREATE TABLE IF NOT EXISTS platforms (
  platform_id INT AUTO_INCREMENT PRIMARY KEY,
  platform_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS movie_platform (
  movie_id INT NOT NULL,
  platform_id INT NOT NULL,
  availability_note VARCHAR(150),
  PRIMARY KEY(movie_id, platform_id),
  FOREIGN KEY(movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
  FOREIGN KEY(platform_id) REFERENCES platforms(platform_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS watchlist (
  watchlist_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  movie_id INT NOT NULL,
  status ENUM('Plan to Watch','Watched') DEFAULT 'Plan to Watch',
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_user_movie(user_id,movie_id),
  FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);

INSERT IGNORE INTO platforms(platform_name) VALUES
('Netflix'),('Amazon Prime Video'),('JioHotstar'),('ZEE5'),('SonyLIV'),('Sun NXT');
