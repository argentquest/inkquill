-- Coin Devaluation Migration Script
-- Multiplies all coin values by 100 (1 cent becomes 100 coins)
-- This script should be run AFTER updating the code to handle the new conversion rates

-- Start transaction to ensure all changes are atomic
BEGIN;

-- Update user account balances (multiply by 100)
UPDATE user_accounts 
SET 
    current_balance = current_balance * 100,
    total_spent = total_spent * 100,
    total_credits_added = total_credits_added * 100;

-- Update transaction amounts and balances (multiply by 100)
UPDATE user_transactions 
SET 
    amount = amount * 100,
    balance_after = balance_after * 100;

-- Update credit package amounts (multiply by 100)
UPDATE credit_packages 
SET 
    credit_amount = credit_amount * 100;

-- Update AI cost logs coin calculations (multiply by 100)
-- Note: calculated_cost_usd stays the same (still in USD)
-- Only update coin-related calculations if any exist in this table
-- (The coin conversion happens in the billing service, not stored here)

-- Verify the changes with some sample queries
-- (Uncomment to run verification queries)

-- SELECT 'user_accounts' as table_name, 
--        AVG(current_balance) as avg_balance,
--        MAX(current_balance) as max_balance,
--        MIN(current_balance) as min_balance
-- FROM user_accounts
-- WHERE current_balance > 0
-- UNION ALL
-- SELECT 'user_transactions' as table_name,
--        AVG(ABS(amount)) as avg_amount,
--        MAX(ABS(amount)) as max_amount,
--        MIN(ABS(amount)) as min_amount
-- FROM user_transactions
-- UNION ALL
-- SELECT 'credit_packages' as table_name,
--        AVG(credit_amount) as avg_amount,
--        MAX(credit_amount) as max_amount,
--        MIN(credit_amount) as min_amount
-- FROM credit_packages;

-- Commit all changes
COMMIT;

-- Post-migration notes:
-- 1. After running this script, 1 USD = 10,000 coins (was 100 coins)
-- 2. 1 cent = 100 coins (was 1 coin)
-- 3. All existing balances and transactions are now 100x larger
-- 4. Credit packages now offer 100x more coins for the same USD price
-- 5. The welcome bonus is now 1,000 coins (was 10 coins)
-- 6. Anonymous users start with 500 coins (was 5 coins)
-- 7. Balance thresholds are now 500 coins (danger) and 1,500 coins (warning)