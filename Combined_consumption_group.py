import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

# Hàm tạo dữ liệu giao dịch cho một nhóm bất kỳ
def generate_data(mean_genuine, var_genuine, mean_fraudulent, var_fraudulent, rate_normal_fraud, 
                  lambda_g, lambda_f, N, card_id_range):
    # Số lượng giao dịch genuine và giao dịch gian lận
    N_genuine = int(N * (1 - rate_normal_fraud))
    N_fraud = N - N_genuine

    # Tạo dữ liệu giao dịch genuine
    genuine_transactions = np.round(np.random.normal(mean_genuine, np.sqrt(var_genuine), N_genuine))

    # Thiết lập mốc thời gian hiện tại
    now = datetime.now()

    # Tạo thời gian giao dịch genuine ngẫu nhiên trong vòng 30 ngày gần nhất
    genuine_times = []
    for lam in lambda_g:
        num = int(N_genuine * lam / sum(lambda_g))
        genuine_times.extend([now - timedelta(days=random.uniform(0, 30)) for _ in range(num)])

    if len(genuine_times) < N_genuine:
        genuine_times.extend([now - timedelta(days=random.uniform(0, 30)) for _ in range(N_genuine - len(genuine_times))])
    genuine_times = genuine_times[:N_genuine]

    # Tạo dữ liệu giao dịch gian lận
    fraud_transactions = np.round(np.random.normal(mean_fraudulent, np.sqrt(var_fraudulent), N_fraud))

    # Tạo thời gian giao dịch gian lận ngẫu nhiên trong vòng 30 ngày gần nhất
    fraud_times = []
    for lam in lambda_f:
        num = int(N_fraud * lam / sum(lambda_f))
        fraud_times.extend([now - timedelta(days=random.uniform(0, 30)) for _ in range(num)])

    if len(fraud_times) < N_fraud:
        fraud_times.extend([now - timedelta(days=random.uniform(0, 30)) for _ in range(N_fraud - len(fraud_times))])
    fraud_times = fraud_times[:N_fraud]

    # Tạo DataFrame
    data = pd.DataFrame({
        'Amount': np.concatenate([genuine_transactions, fraud_transactions]),
        'Label': ['Genuine'] * N_genuine + ['Fraud'] * N_fraud,
        'Time': np.concatenate([genuine_times, fraud_times])
    })

    # Chuyển đổi cột Time để chỉ giữ lại ngày tháng năm
    data['Time'] = pd.to_datetime(data['Time']).dt.date

    # Tạo cột CardID với các giá trị trong khoảng cho trước, sau đó lặp lại để có đủ số lượng
    card_ids = np.random.choice(np.arange(card_id_range[0], card_id_range[1] + 1), N, replace=True)
    data['CardID'] = card_ids

    return data

# Tạo dữ liệu cho nhóm Low
low_data = generate_data(
    mean_genuine=1170,
    var_genuine=234,
    mean_fraudulent=1110,
    var_fraudulent=220,
    rate_normal_fraud=0.1,
    lambda_g=[0.6, 0.2, 0.15, 0.05],
    lambda_f=[0.25, 0.25, 0.25, 0.25],
    N=5000,
    card_id_range=(1, 100)
)

# Tạo dữ liệu cho nhóm Medium
medium_data = generate_data(
    mean_genuine=5000,
    var_genuine=1200,
    mean_fraudulent=6000,
    var_fraudulent=1000,
    rate_normal_fraud=0.1,
    lambda_g=[0.05, 0.4, 0.5, 0.05],
    lambda_f=[0.25, 0.25, 0.25, 0.25],
    N=3000,
    card_id_range=(1, 151)
)

# Tạo dữ liệu cho nhóm High
high_data = generate_data(
    mean_genuine=10000,
    var_genuine=2000,
    mean_fraudulent=11200,
    var_fraudulent=2240,
    rate_normal_fraud=0.1,
    lambda_g=[0.05, 0.15, 0.2, 0.6],
    lambda_f=[0.25, 0.25, 0.25, 0.25],
    N=7000,
    card_id_range=(1, 201)
)

# Gộp dữ liệu từ ba nhóm lại với nhau
combined_data = pd.concat([low_data, medium_data, high_data], ignore_index=True)

# Sắp xếp dữ liệu theo thời gian từ xa nhất đến gần nhất
combined_data = combined_data.sort_values(by='Time', ascending=True).reset_index(drop=True)

# Bổ sung cột TranID từ 1 đến 15000 sau khi sắp xếp
combined_data['TranID'] = range(1, len(combined_data) + 1)

# Sắp xếp lại thứ tự cột theo yêu cầu: TranID, CardID, Time, Amount, Label
combined_data = combined_data[['TranID', 'CardID', 'Time', 'Amount', 'Label']]

# Lưu dữ liệu vào file Excel mà không tạo cột chỉ mục
file_path = 'Combined_consumption_group_data.xlsx'
combined_data.to_excel(file_path, index=False, engine='openpyxl')

# Kiểm tra xem file đã được tạo thành công chưa
if os.path.exists(file_path):
    print(f"File has been successfully created at: {file_path}")
else:
    print("An error occurred while creating the file.")

# Hiển thị 10 dòng đầu tiên và 10 dòng cuối cùng
print("10 first rows:")
print(combined_data.head(10))

print("\n10 last rows:")
print(combined_data.tail(10))
