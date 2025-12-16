#!/bin/bash

# 1. Đi đến thư mục chứa file này
cd "$(dirname "$0")"

# 2. In thông báo
echo "🚀 Đang khởi động Market Research Tool cho Đức..."
echo "📂 Thư mục: $(pwd)"

# --- ĐOẠN MỚI THÊM VÀO ---
# Kiểm tra xem đã cài node_modules chưa, nếu chưa thì cài luôn
if [ ! -d "node_modules" ]; then
  echo "📦 Chưa thấy thư viện Node.js. Đang tự động cài đặt..."
  npm install
fi
# -------------------------

# 3. Kích hoạt môi trường ảo
source venv/bin/activate

# 4. Chạy Streamlit
echo "🌐 Đang mở Dashboard..."
python3 -m streamlit run app.py