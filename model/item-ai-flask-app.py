from flask import Flask, request, jsonify
import joblib
import pandas as pd
import mysql.connector

db_config = {
    'user': 'ds601',
    'password': '1124db!',
    'host': '43.200.222.46',
    'database': 'my_busan_log'
}


app = Flask(__name__)

all_product_ids_list=[]

# 모델 파일 로드
model = joblib.load('item_model.pkl')




#초기화 함수
def init_app():
    print("애플리케이션 시작 시 호출됩니다.")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM `store`')
    stores = cursor.fetchall()
    for item in stores:
        all_product_ids_list.append(item['s_idx'])
    cursor.close()
    conn.close()
    # 초기화 작업이나 설정을 여기에 수행합니다.

init_app()



def recommend_products(member_id, top_n=5):
    # 회원의 구매 이력에서 구매한 상품을 포함
    print(all_product_ids_list)
    all_product_ids=set(all_product_ids_list)
    purchased_product_ids = set()
    recommendations = []
    
    for product_id in all_product_ids - purchased_product_ids:
        pred = model.predict(member_id, product_id)
        recommendations.append((product_id, pred.est))
    
    # 점수에 따라 상품 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [product_id for product_id, _ in recommendations[:top_n]]

# 일반적인 라우트 방식입니다.
@app.route('/item-recommand')
def item_recommand():
    member_id = int(request.args.get('user_id'))
    recommendations = recommend_products(member_id)
    print(recommendations)
    return jsonify({'recommendations': recommendations})
    

app.run(host="43.201.102.226",port=6011)