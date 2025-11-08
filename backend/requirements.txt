-- E-Commerce Fraud Detector Database Schema
-- PostgreSQL 14+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id TEXT,
    review_text TEXT NOT NULL,
    rating NUMERIC CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    device_fingerprint TEXT,
    
    -- Fraud detection metadata
    is_fake_pred BOOLEAN,
    fake_score NUMERIC CHECK (fake_score >= 0 AND fake_score <= 1),
    decision_json JSONB,
    
    -- Audit
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_reviews_created_at ON reviews(created_at);
CREATE INDEX idx_reviews_is_fake ON reviews(is_fake_pred);
CREATE INDEX idx_reviews_ip ON reviews(ip_address);
CREATE INDEX idx_reviews_device ON reviews(device_fingerprint);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC NOT NULL CHECK (amount >= 0),
    currency TEXT DEFAULT 'INR',
    device_fingerprint TEXT,
    ip_address INET,
    channel TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Fraud detection metadata
    is_fraud_pred BOOLEAN,
    fraud_score NUMERIC CHECK (fraud_score >= 0 AND fraud_score <= 1),
    decision_json JSONB,
    
    -- Audit
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tx_user_id ON transactions(user_id);
CREATE INDEX idx_tx_created_at ON transactions(created_at);
CREATE INDEX idx_tx_is_fraud ON transactions(is_fraud_pred);
CREATE INDEX idx_tx_ip ON transactions(ip_address);
CREATE INDEX idx_tx_device ON transactions(device_fingerprint);
CREATE INDEX idx_tx_amount ON transactions(amount);

-- Human labels for feedback loop
CREATE TABLE IF NOT EXISTS labels (
    id BIGSERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('review', 'transaction')),
    entity_id BIGINT NOT NULL,
    is_fraud BOOLEAN NOT NULL,
    notes TEXT,
    labeled_by TEXT,
    labeled_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_labels_entity ON labels(entity_type, entity_id);
CREATE INDEX idx_labels_labeled_at ON labels(labeled_at);

-- Materialized view for analytics (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS fraud_stats AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_reviews,
    SUM(CASE WHEN is_fake_pred THEN 1 ELSE 0 END) as fake_reviews,
    AVG(fake_score) as avg_fake_score
FROM reviews
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at)
UNION ALL
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_transactions,
    SUM(CASE WHEN is_fraud_pred THEN 1 ELSE 0 END) as fraud_transactions,
    AVG(fraud_score) as avg_fraud_score
FROM transactions
WHERE created_at >= NOW() - INTERVAL '90 days'
GROUP BY DATE(created_at);

CREATE INDEX idx_fraud_stats_date ON fraud_stats(date);