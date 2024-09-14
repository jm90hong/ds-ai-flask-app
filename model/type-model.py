import joblib
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import pandas as pd
import mysql.connector
from datetime import datetime, time


#DB연결 및 데이터 조회
# MariaDB 연결 정보 설정
db_config = {
    'user': 'ds601',
    'password': 'dkgus0908',
    'host': '3.36.168.133',
    'database': 'a_link'
}


# 학습 데이터
# data = {
#     'member_id': [1, 1, 1, 2, 2, 3, 3, 3, 3,1,2],
#     'product_id': [101, 102, 103, 101, 104, 105, 106, 107, 108,111,111],
#     'purchase_date': [1609459200000, 1609545600000, 1609632000000, 1609718400000, 1609804800000,
#                        1609891200000, 1609977600000, 1610064000000, 1610150400000,1610150400000,1610150400000]
# }


type_dic={
     '전체':100, 
     '생활편의지원':101, 
     '주거환경':102, 
     '상담':103, 
     '교육':104, 
     '보건의료':105, 
     '농어촌':106, 
     '문화행사':107, 
     '환경보호':108, 
     '행정보조':109, 
     '안전·예방':110, 
     '공익·인권':111, 
     '재해·재난':112, 
     '국제협력·해외봉사':113, 
     '멘토링':114, 
     '기타':115
}




data = {
    'member_id': [],
    'product_id': [],
    'purchase_date': []
}

# 데이터베이스 연결 함수
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def convertDate(date_str):
    # 주어진 날짜 문자열
    print(date_str)
    #date_str = '2024-08-27 11:15:59'

    # 날짜 문자열의 형식 정의
    #date_format = '%Y-%m-%d %H:%M:%S'

    # 문자열을 datetime 객체로 변환
    #date_obj = datetime.strptime(date_str, date_format)

    # 시간을 오전 0시로 맞추기 위해 시간 부분을 새로 설정
    date_obj = datetime.combine(date_str.date(), time.min)

    # datetime 객체를 타임스탬프로 변환 (초 단위)
    timestamp = date_obj.timestamp()

    # 밀리초로 변환
    milliseconds = int(timestamp * 1000)
    return milliseconds



def get_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM `announcement`')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


orders = get_data()


for order in orders:
    
    user_id = order['member_idx']
    product_id=type_dic[order['type']]
    date = convertDate(order['reg_date'])
    data['member_id'].append(user_id)
    data['product_id'].append(product_id)
    data['purchase_date'].append(date)

print(data)



df = pd.DataFrame(data)
df['purchase_date'] = pd.to_datetime(df['purchase_date'], unit='ms')
df['rating'] = (df['purchase_date'] - df['purchase_date'].min()).dt.days
print(df['rating'])
# 데이터셋 준비
reader = Reader(rating_scale=(df['rating'].min(), df['rating'].max()))
dataset = Dataset.load_from_df(df[['member_id', 'product_id', 'rating']], reader)

trainset, _ = train_test_split(dataset, test_size=0.25,random_state=42)



# 모델 학습
model = SVD()
model.fit(trainset)

# 모델 저장
joblib.dump(model, 'type_model.pkl')
