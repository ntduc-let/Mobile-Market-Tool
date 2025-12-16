#!/bin/bash

# 1. Đi đến thư mục chứa file này (Bất kể bạn để folder ở đâu)
cd "$(dirname "$0")"

# 2. In thông báo cho ngầu
echo "🚀 Đang khởi động Market Research Tool cho Đức..."
echo "📂 Thư mục: $(pwd)"

# 3. Kích hoạt môi trường ảo
source venv/bin/activate

# 4. Chạy Streamlit (Tự mở trình duyệt)
echo "🌐 Đang mở Dashboard..."
python3 -m streamlit run app.py
