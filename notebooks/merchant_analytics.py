# ================================================================
# Merchant Transaction Analytics Dashboard — Fintech Domain
# Author  : Avanit Singh
# Stack   : Python (Pandas) | SQL | Power BI
# Purpose : Analyse PG performance, settlement TAT, MDR metrics
# ================================================================

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ── 1. Load & Prepare Data ───────────────────────────────────
df = pd.read_csv('data/merchant_transactions.csv')
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
df['settlement_date']  = pd.to_datetime(df['settlement_date'])

print(f"✅ Data loaded: {len(df)} transactions")
print(f"\n📋 Dataset Preview:")
print(df.head())

# ── 2. Transaction Success Rate ──────────────────────────────
status   = df['status'].value_counts()
success  = status.get('SUCCESS', 0)
failed   = status.get('FAILED',  0)
pending  = status.get('PENDING', 0)
total    = len(df)
succ_pct = (success / total * 100)

print(f"\n{'='*50}")
print(f"📊 TRANSACTION SUCCESS METRICS")
print(f"{'='*50}")
print(f"Total Transactions : {total}")
print(f"Successful         : {success}  ({succ_pct:.1f}%)")
print(f"Failed             : {failed}   ({failed/total*100:.1f}%)")
print(f"Pending            : {pending}  ({pending/total*100:.1f}%)")

# ── 3. Settlement TAT Analysis ───────────────────────────────
settled = df[df['settlement_date'].notna()].copy()
settled['tat_days'] = (
    settled['settlement_date'] - settled['transaction_date']
).dt.days

print(f"\n{'='*50}")
print(f"📊 SETTLEMENT TAT METRICS")
print(f"{'='*50}")
print(f"Average Settlement TAT : {settled['tat_days'].mean():.1f} days")
print(f"Minimum TAT            : {settled['tat_days'].min()} day")
print(f"Maximum TAT            : {settled['tat_days'].max()} days")

# ── 4. Revenue & MDR Performance ─────────────────────────────
successful = df[df['status'] == 'SUCCESS'].copy()
successful['mdr_earned'] = successful['amount'] * successful['mdr_rate'] / 100

total_volume = successful['amount'].sum()
total_mdr    = successful['mdr_earned'].sum()

print(f"\n{'='*50}")
print(f"📊 REVENUE & MDR METRICS")
print(f"{'='*50}")
print(f"Total Payment Volume  : INR {total_volume:>12,.2f}")
print(f"Total MDR Earned      : INR {total_mdr:>12,.2f}")
print(f"Average MDR Rate      : {successful['mdr_rate'].mean():.2f}%")

# ── 5. Merchant Performance ──────────────────────────────────
merch = df.groupby(['merchant_id', 'merchant_name']).agg(
    Total_Txns=('transaction_id', 'count'),
    Success=('status', lambda x: (x == 'SUCCESS').sum()),
    Failed=('status', lambda x: (x == 'FAILED').sum()),
    Volume=('amount', 'sum')
).reset_index()
merch['Success Rate %'] = (merch['Success'] / merch['Total_Txns'] * 100).round(1)
merch['MDR Earned']     = (merch['Volume'] * 0.012).round(2)  # approx

print(f"\n📊 MERCHANT PERFORMANCE:")
print(merch.sort_values('Volume', ascending=False).to_string(index=False))

# ── 6. Payment Failure Patterns ──────────────────────────────
failures = df[df['status'] == 'FAILED']
print(f"\n{'='*50}")
print(f"📊 PAYMENT FAILURE PATTERNS")
print(f"{'='*50}")
print(f"Failed Transactions by Category:")
print(failures.groupby('merchant_category')['transaction_id'].count()
      .sort_values(ascending=False).to_string())
print(f"\nFailed Transactions by Merchant:")
print(failures.groupby('merchant_name')['transaction_id'].count()
      .sort_values(ascending=False).to_string())

# ── 7. Category Performance ──────────────────────────────────
cat = df.groupby('merchant_category').agg(
    Transactions=('transaction_id', 'count'),
    Volume=('amount', 'sum'),
    Success_Rate=('status', lambda x: (x=='SUCCESS').sum()/len(x)*100)
).reset_index()
cat['Success_Rate'] = cat['Success_Rate'].round(1)
cat['Volume']       = cat['Volume'].round(2)

print(f"\n📊 CATEGORY PERFORMANCE:")
print(cat.sort_values('Volume', ascending=False).to_string(index=False))

# ── 8. Active Merchant Ratio ─────────────────────────────────
active_merchants = df[df['status']=='SUCCESS']['merchant_id'].nunique()
total_merchants  = df['merchant_id'].nunique()
active_ratio     = (active_merchants / total_merchants * 100)

print(f"\n{'='*50}")
print(f"📊 MERCHANT ACTIVITY")
print(f"{'='*50}")
print(f"Total Merchants        : {total_merchants}")
print(f"Active Merchants       : {active_merchants}")
print(f"Active Merchant Ratio  : {active_ratio:.1f}%")

print(f"\n✅ Merchant Analytics completed successfully.")
print(f"🔑 Key Finding: {succ_pct:.1f}% success rate | "
      f"Settlement TAT avg {settled['tat_days'].mean():.1f} days | "
      f"MDR earned INR {total_mdr:,.2f}")
