"""
電商顧客價值評估與動態流失預警系統 (RFM-CAI Analysis)
"""
import numpy as np
import pandas as pd

# 1. 模擬交易紀錄（實務上可讀取真實 CSV/Excel）
def generate_sample_data(num_records=1000, num_customers=100):
    np.random.seed(42)
    customer_ids = [f"C{i:04d}" for i in range(1, num_customers + 1)]
    start_date = pd.to_datetime("2023-01-01")
    end_date = pd.to_datetime("2023-12-31")
    
    dates = start_date + pd.to_timedelta(np.random.randint(0, (end_date - start_date).days, num_records), unit='D')
    amounts = np.random.exponential(scale=1200, size=num_records) + 200
    
    df = pd.DataFrame({
        "CustomerID": np.random.choice(customer_ids, num_records),
        "TransactionDate": dates,
        "SalesAmount": np.round(amounts, 2)
    })
    return df

# 2. 資料清洗與日層級聚合
def preprocess_data(df):
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate'])
    daily_df = df.groupby(['CustomerID', 'TransactionDate'])['SalesAmount'].sum().reset_index()
    daily_df = daily_df.sort_values(['CustomerID', 'TransactionDate']).reset_index(drop=True)
    return daily_df

# 3. 計算 RFM 指標與五等分打分
def compute_rfm(df, ref_date=pd.to_datetime("2024-01-01")):
    rfm = df.groupby('CustomerID').agg(
        Recency=('TransactionDate', lambda d: (ref_date - d.max()).days),
        Frequency=('TransactionDate', 'count'),
        Monetary=('SalesAmount', 'sum')
    ).reset_index()
    
    rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return rfm

# 4. 計算 CAI 顧客活躍指數 (算術平均 MLE 與線性加權 WMLE)
def compute_cai_for_customer(dates):
    k = len(dates) - 1
    if k < 2:  # 消費至少需 3 次以上（2 個以上間隔天數）
        return pd.Series({'MLE': np.nan, 'WMLE': np.nan, 'CAI': np.nan, 'Status': 'Insufficient'})
    
    intervals = np.diff(dates.values).astype('timedelta64[D]').astype(int)
    mle = np.mean(intervals)
    weights = np.arange(1, k + 1)
    wmle = np.sum(weights * intervals) / np.sum(weights)
    
    cai = ((mle - wmle) / mle) * 100.0
    status = 'Active' if cai > 0 else ('Inactive' if cai < 0 else 'Stable')
    return pd.Series({'MLE': round(mle, 2), 'WMLE': round(wmle, 2), 'CAI': round(cai, 2), 'Status': status})

# 5. 輸出四象限分群
def generate_customer_segments(rfm, cai_df):
    merged = pd.merge(rfm, cai_df, on='CustomerID')
    mean_freq = merged['Frequency'].median()
    
    def assign_quadrant(row):
        if pd.isna(row['CAI']):
            return 'New / Insufficient Data'
        if row['CAI'] >= 0 and row['Frequency'] >= mean_freq:
            return 'Q1: Active-Loyal (高頻加速 VIP)'
        elif row['CAI'] >= 0 and row['Frequency'] < mean_freq:
            return 'Q2: Active-Potential (低頻潛力客)'
        elif row['CAI'] < 0 and row['Frequency'] >= mean_freq:
            return 'Q3: Inactive-Heavy (高貢獻流失警戒客)'
        else:
            return 'Q4: Inactive-Dormant (沉睡散客)'
            
    merged['Customer_Segment'] = merged.apply(assign_quadrant, axis=1)
    return merged

if __name__ == '__main__':
    raw_df = generate_sample_data()
    clean_df = preprocess_data(raw_df)
    rfm_df = compute_rfm(clean_df)
    cai_df = clean_df.groupby('CustomerID')['TransactionDate'].apply(compute_cai_for_customer).unstack().reset_index()
    results = generate_customer_segments(rfm_df, cai_df)
    results.to_csv('customer_segmentation_results.csv', index=False)
    print("分析完成，資料已輸出至 customer_segmentation_results.csv")
