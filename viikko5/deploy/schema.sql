CREATE DATABASE IF NOT EXISTS viikko5_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE viikko5_db;

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL,
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session (session_id)
);
