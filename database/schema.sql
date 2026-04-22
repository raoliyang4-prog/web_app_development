-- database/schema.sql
-- SQLite 資料庫建表語法：活動報名系統
-- 說明：使用 CREATE TABLE IF NOT EXISTS，可重複執行不會報錯

-- 使用者資料表
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    role            TEXT    NOT NULL CHECK (role IN ('student', 'admin')),
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    email           TEXT    NOT NULL UNIQUE,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 活動資料表
CREATE TABLE IF NOT EXISTS events (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             TEXT    NOT NULL,
    description       TEXT,
    max_capacity      INTEGER NOT NULL,
    current_capacity  INTEGER NOT NULL DEFAULT 0,
    start_time        TEXT    NOT NULL,
    end_time          TEXT    NOT NULL,
    created_by        INTEGER NOT NULL,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- 報名記錄資料表
CREATE TABLE IF NOT EXISTS registrations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'success'
                    CHECK (status IN ('success', 'cancelled')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    UNIQUE (user_id, event_id)  -- 每位學生對同一活動只能報名一次
);
