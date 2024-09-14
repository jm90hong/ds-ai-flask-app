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
model_for_type = joblib.load('type_model.pkl')



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
    all_product_ids=set(all_product_ids_list)
    purchased_product_ids = set()
    recommendations = []
    
    for product_id in all_product_ids - purchased_product_ids:
        pred = model.predict(member_id, product_id)
        recommendations.append((product_id, pred.est))
    
    # 점수에 따라 상품 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [product_id for product_id, _ in recommendations[:top_n]]


def recommend_types(member_id, top_n=5):
    # 회원의 구매 이력에서 구매한 상품을 포함
    all_product_ids=set([100,101,102,103,104,105,106,107,108,109,110,111,112,113,114])
    purchased_product_ids = set()
    recommendations = []
    
    for product_id in all_product_ids - purchased_product_ids:
        pred = model_for_type.predict(member_id, product_id)
        print(pred)
        recommendations.append((product_id, pred.est))
    
    # 점수에 따라 상품 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [product_id for product_id, _ in recommendations[:top_n]]

# 일반적인 라우트 방식입니다.
@app.route('/item-recommand')
def item_recommand():
    member_id = int(request.args.get('user_id'))
    recommendations = recommend_products(member_id)
    
    return jsonify({'recommendations': recommendations})

@app.route('/type-recommand')
def type_recommand():
    member_id = int(request.args.get('user_id'))
    recommendations = recommend_types(member_id)

    reversed_type_dic = {
        100: '전체', 
        101: '생활편의지원', 
        102: '주거환경', 
        103: '상담', 
        104: '교육', 
        105: '보건의료', 
        106: '농어촌', 
        107: '문화행사', 
        108: '환경보호', 
        109: '행정보조', 
        110: '안전·예방', 
        111: '공익·인권', 
        112: '재해·재난', 
        113: '국제협력·해외봉사', 
        114: '멘토링', 
        115: '기타'
    }


    for index, value in enumerate(recommendations):
        recommendations[index]=reversed_type_dic[value]



    
    return jsonify({'recommendations': recommendations})


app.run(host="0.0.0.0",port=6011)