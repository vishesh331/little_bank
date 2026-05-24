-- Supabase Schema for Banking System
-- Run this in Supabase SQL Editor to set up the database

-- ========================================
-- Accounts Table
-- ========================================
CREATE TABLE IF NOT EXISTS accounts (
    account_number TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    balance NUMERIC(15, 2) NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_accounts_username ON accounts(username);

-- ========================================
-- Transactions Table
-- ========================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    from_account TEXT,
    to_account TEXT,
    amount NUMERIC(15, 2) NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX idx_transactions_from_account ON transactions(from_account);
CREATE INDEX idx_transactions_to_account ON transactions(to_account);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);

-- ========================================
-- Sessions Table (for session management)
-- ========================================
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    account_number TEXT NOT NULL,
    username TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_account_number ON sessions(account_number);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- ========================================
-- Optional: Enable Row Level Security (RLS)
-- Uncomment if you want to restrict access:
-- ========================================
-- ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- For development/testing without RLS:
-- ALTER TABLE accounts DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE transactions DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE sessions DISABLE ROW LEVEL SECURITY;
