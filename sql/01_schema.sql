-- ============================================================
-- Vedas DBMS (CSBB 204) - 01_schema.sql
-- Database + 13 tables. MySQL 8, InnoDB (row locks), utf8mb4 (Devanagari).
-- Run as root:  mysql -u root -p < sql/01_schema.sql
-- ============================================================

DROP DATABASE IF EXISTS vedas_db;
CREATE DATABASE vedas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE vedas_db;

-- ---------- reference tables (no dependencies) ----------

CREATE TABLE Vedas (
    veda_id   INT AUTO_INCREMENT PRIMARY KEY,
    veda_name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Rishis (
    rishi_id   INT AUTO_INCREMENT PRIMARY KEY,
    rishi_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Deities (
    deity_id   INT AUTO_INCREMENT PRIMARY KEY,
    deity_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Themes (
    theme_id   INT AUTO_INCREMENT PRIMARY KEY,
    theme_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE App_Users (
    user_id  INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    role     ENUM('student','scholar','editor','admin') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- hierarchy: Veda -> Kanda -> Sukta ----------

CREATE TABLE Kandas (
    kanda_id     INT AUTO_INCREMENT PRIMARY KEY,
    veda_id      INT NOT NULL,
    kanda_number INT NOT NULL,
    UNIQUE (veda_id, kanda_number),
    CONSTRAINT fk_kanda_veda FOREIGN KEY (veda_id) REFERENCES Vedas (veda_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Suktas (
    sukta_id     INT AUTO_INCREMENT PRIMARY KEY,
    kanda_id     INT NOT NULL,
    sukta_number INT NOT NULL,
    UNIQUE (kanda_id, sukta_number),
    CONSTRAINT fk_sukta_kanda FOREIGN KEY (kanda_id) REFERENCES Kandas (kanda_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- core text table ----------

CREATE TABLE Mantras (
    mantra_id     INT AUTO_INCREMENT PRIMARY KEY,
    sukta_id      INT NOT NULL,
    rishi_id      INT NOT NULL,
    deity_id      INT NOT NULL,
    mantra_number INT NOT NULL,
    metre         VARCHAR(50),
    sanskrit_text TEXT,
    iast_text     TEXT,
    UNIQUE (sukta_id, mantra_number),
    CONSTRAINT fk_mantra_sukta FOREIGN KEY (sukta_id) REFERENCES Suktas (sukta_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_mantra_rishi FOREIGN KEY (rishi_id) REFERENCES Rishis (rishi_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_mantra_deity FOREIGN KEY (deity_id) REFERENCES Deities (deity_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- content added by users ----------

CREATE TABLE Translations (
    translation_id  INT AUTO_INCREMENT PRIMARY KEY,
    mantra_id       INT NOT NULL,
    translator_name VARCHAR(100) NOT NULL,
    text            TEXT,
    status          ENUM('pending','approved') NOT NULL DEFAULT 'pending',
    CONSTRAINT fk_trans_mantra FOREIGN KEY (mantra_id) REFERENCES Mantras (mantra_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Word_Meanings (
    mantra_id       INT NOT NULL,
    word_order      INT NOT NULL,
    sanskrit_word   VARCHAR(100),
    dhatu           VARCHAR(100),
    english_meaning VARCHAR(255),
    UNIQUE (mantra_id, word_order),
    CONSTRAINT fk_word_mantra FOREIGN KEY (mantra_id) REFERENCES Mantras (mantra_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Mantra_Themes (
    mantra_id INT NOT NULL,
    theme_id  INT NOT NULL,
    PRIMARY KEY (mantra_id, theme_id),
    CONSTRAINT fk_mt_mantra FOREIGN KEY (mantra_id) REFERENCES Mantras (mantra_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_mt_theme FOREIGN KEY (theme_id) REFERENCES Themes (theme_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Mantra_History (
    history_id       INT AUTO_INCREMENT PRIMARY KEY,
    mantra_id        INT NOT NULL,
    old_sanskrit_text TEXT,
    old_iast_text    TEXT,
    changed_by       VARCHAR(50),
    changed_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hist_mantra FOREIGN KEY (mantra_id) REFERENCES Mantras (mantra_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Bookmarks (
    user_id  INT NOT NULL,
    mantra_id INT NOT NULL,
    PRIMARY KEY (user_id, mantra_id),
    CONSTRAINT fk_bm_user FOREIGN KEY (user_id) REFERENCES App_Users (user_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_bm_mantra FOREIGN KEY (mantra_id) REFERENCES Mantras (mantra_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
