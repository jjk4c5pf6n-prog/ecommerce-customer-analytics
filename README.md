# ecommerce-customer-analytics
E-commerce Customer Value Segmentation and Dynamic Churn Warning System based on RFM and CAI models.

# 🛍️ 電商顧客價值評估與動態流失預警系統 (RFM-CAI Analysis)

## 📌 專案背景與商業問題
傳統 RFM 分析僅能評估顧客過去的靜態貢獻，無法即時捕捉近期消費頻率放緩的流失警訊。本專案整合 RFM 評分模型與 CAI（顧客活躍指數），建立動態預警系統與閉環行銷方案。

## 🛠️ 技術與分析架構
- **資料處理**：Python (Pandas, NumPy) 進行日層級訂單聚合與時間間隔計算
- **模型維度**：
  - **RFM 五等分評分法**：將 R、F、M 三項維度劃分為 1 至 5 分
  - **CAI 計算**：比較歷史算術平均間隔（MLE）與近期加權平均間隔（WMLE）
  - **動態四象限分群**：劃分 Active-Loyal、Active-Potential、Inactive-Heavy、Inactive-Dormant 客群

## 📊 專案產出
- `ecommerce_analytics.py`：端到端數據清洗與特徵工程腳本
- `presentation.pdf`（或專案簡報）：針對行銷與營運決策的商業企劃與策略建議
