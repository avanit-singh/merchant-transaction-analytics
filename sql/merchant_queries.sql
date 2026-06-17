-- ============================================================
-- Merchant Transaction Analytics — SQL Queries
-- Author: Avanit Singh
-- ============================================================

-- 1. Overall Transaction Success Rate
SELECT
    COUNT(*)                                                            AS total_transactions,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END)                AS successful,
    SUM(CASE WHEN status = 'FAILED'  THEN 1 ELSE 0 END)                AS failed,
    SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END)                AS pending,
    ROUND(SUM(CASE WHEN status='SUCCESS' THEN 1.0 ELSE 0 END)
          / COUNT(*) * 100, 1)                                          AS success_rate_pct
FROM merchant_transactions;

-- 2. Merchant Revenue & MDR Performance
SELECT
    merchant_name,
    COUNT(*)                                                            AS total_txns,
    SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END)                  AS successful,
    ROUND(SUM(CASE WHEN status='SUCCESS' THEN amount      ELSE 0 END), 2) AS total_volume,
    ROUND(SUM(CASE WHEN status='SUCCESS' THEN amount*mdr_rate/100 ELSE 0 END), 2) AS mdr_earned,
    ROUND(SUM(CASE WHEN status='SUCCESS' THEN 1.0 ELSE 0 END)
          / COUNT(*) * 100, 1)                                          AS success_rate_pct
FROM merchant_transactions
GROUP BY merchant_id, merchant_name
ORDER BY total_volume DESC;

-- 3. Settlement TAT Analysis
SELECT
    merchant_name,
    COUNT(*)                                                            AS settled_txns,
    ROUND(AVG(JULIANDAY(settlement_date) - JULIANDAY(transaction_date)), 1) AS avg_tat_days,
    MIN(JULIANDAY(settlement_date) - JULIANDAY(transaction_date))          AS min_tat_days,
    MAX(JULIANDAY(settlement_date) - JULIANDAY(transaction_date))          AS max_tat_days
FROM merchant_transactions
WHERE settlement_date IS NOT NULL
GROUP BY merchant_id, merchant_name
ORDER BY avg_tat_days DESC;

-- 4. Payment Failure Pattern by Category
SELECT
    merchant_category,
    COUNT(*)                                                            AS failed_txns,
    ROUND(AVG(amount), 2)                                               AS avg_failed_amount,
    ROUND(SUM(CASE WHEN status='FAILED' THEN 1.0 ELSE 0 END)
          / COUNT(*) * 100, 1)                                          AS failure_rate_pct
FROM merchant_transactions
GROUP BY merchant_category
ORDER BY failed_txns DESC;

-- 5. Active Merchant Ratio
SELECT
    COUNT(DISTINCT merchant_id)                                         AS total_merchants,
    COUNT(DISTINCT CASE WHEN status='SUCCESS' THEN merchant_id END)     AS active_merchants,
    ROUND(COUNT(DISTINCT CASE WHEN status='SUCCESS' THEN merchant_id END)
          * 100.0 / COUNT(DISTINCT merchant_id), 1)                     AS active_ratio_pct
FROM merchant_transactions;
