-- ============================================
-- PROMO CODE SYSTEM - DATABASE SCHEMA
-- ============================================
-- 
-- This schema provides a complete promo code system with:
-- - Flexible discount types (free, percentage, fixed amount)
-- - Usage tracking and limits
-- - Expiration dates
-- - Analytics support
--
-- Compatible with: PostgreSQL, Supabase
-- ============================================

-- Main promo codes table
CREATE TABLE IF NOT EXISTS promo_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL,
  discount_type TEXT NOT NULL CHECK (discount_type IN ('percentage', 'amount', 'free')),
  discount_value INTEGER NOT NULL, -- 100 for 100% off, 10 for $10 off, etc.
  is_active BOOLEAN DEFAULT true,
  max_uses INTEGER, -- NULL = unlimited uses
  current_uses INTEGER DEFAULT 0,
  expires_at TIMESTAMPTZ, -- NULL = never expires
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_by TEXT, -- Optional: track who created it
  description TEXT -- Optional: internal note about the code
);

-- Index for fast code lookups (only active codes)
CREATE INDEX IF NOT EXISTS idx_promo_codes_code 
  ON promo_codes(code) 
  WHERE is_active = true;

-- Index for expiration cleanup queries
CREATE INDEX IF NOT EXISTS idx_promo_codes_expires_at 
  ON promo_codes(expires_at) 
  WHERE expires_at IS NOT NULL;

-- Index for usage tracking
CREATE INDEX IF NOT EXISTS idx_promo_codes_usage 
  ON promo_codes(current_uses, max_uses) 
  WHERE max_uses IS NOT NULL;

-- Usage tracking table (optional but recommended)
CREATE TABLE IF NOT EXISTS promo_code_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  promo_code_id UUID REFERENCES promo_codes(id) ON DELETE CASCADE,
  user_email TEXT,
  user_phone TEXT,
  user_name TEXT,
  used_at TIMESTAMPTZ DEFAULT NOW(),
  stripe_session_id TEXT, -- Link to payment session
  order_id TEXT, -- Link to order/transaction
  metadata JSONB -- Additional tracking data
);

-- Index for usage queries by code
CREATE INDEX IF NOT EXISTS idx_promo_code_usage_code_id 
  ON promo_code_usage(promo_code_id);

-- Index for usage queries by user
CREATE INDEX IF NOT EXISTS idx_promo_code_usage_email 
  ON promo_code_usage(user_email) 
  WHERE user_email IS NOT NULL;

-- Index for recent usage queries
CREATE INDEX IF NOT EXISTS idx_promo_code_usage_used_at 
  ON promo_code_usage(used_at DESC);

-- ============================================
-- EXAMPLE DATA
-- ============================================

-- Insert example promo codes
INSERT INTO promo_codes (code, discount_type, discount_value, description) VALUES
  ('SAVE10', 'amount', 10, 'Standard $10 discount'),
  ('FREE', 'free', 0, 'Free access code'),
  ('LAUNCH50', 'percentage', 50, 'Launch promotion - 50% off'),
  ('VIP', 'free', 0, 'VIP access code')
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- USEFUL QUERIES
-- ============================================

-- View all active codes with usage stats
-- SELECT 
--   code,
--   discount_type,
--   discount_value,
--   current_uses,
--   max_uses,
--   expires_at,
--   is_active
-- FROM promo_codes
-- WHERE is_active = true
-- ORDER BY created_at DESC;

-- View code usage history
-- SELECT 
--   pc.code,
--   pcu.user_email,
--   pcu.used_at
-- FROM promo_code_usage pcu
-- JOIN promo_codes pc ON pcu.promo_code_id = pc.id
-- ORDER BY pcu.used_at DESC
-- LIMIT 50;

-- Check code availability
-- SELECT 
--   code,
--   is_active,
--   current_uses,
--   max_uses,
--   expires_at,
--   CASE 
--     WHEN NOT is_active THEN 'Inactive'
--     WHEN expires_at IS NOT NULL AND expires_at < NOW() THEN 'Expired'
--     WHEN max_uses IS NOT NULL AND current_uses >= max_uses THEN 'Limit reached'
--     ELSE 'Available'
--   END as status
-- FROM promo_codes;

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Deactivate expired codes
-- UPDATE promo_codes
-- SET is_active = false
-- WHERE expires_at < NOW() AND is_active = true;

-- Reset usage count (use with caution!)
-- UPDATE promo_codes
-- SET current_uses = 0
-- WHERE code = 'YOUR_CODE';

-- Delete old usage records (older than 1 year)
-- DELETE FROM promo_code_usage
-- WHERE used_at < NOW() - INTERVAL '1 year';
