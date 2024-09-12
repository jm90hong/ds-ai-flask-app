from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import pandas as pd



# 데이터 예시: 데이터프레임 생성
data = {
    'member_id': [1, 1, 1, 2, 2, 3, 3, 3, 3,1,1],
    'product_id': ['1011', '1011', '1011', '101', '104', '105', '106', '107', '1081','1081','1081'],
    'purchase_date': [1609459200000, 1609545600000, 1609632000000, 1609718400000, 1609804800000,
                       1609891200000, 1609977600000, 1610064000000, 1610150400000,1610150400000,1610150400000]
}
df = pd.DataFrame(data)

# 데이터프레임의 purchase_date를 최근 구매일자를 기준으로 변환
df['purchase_date'] = pd.to_datetime(df['purchase_date'], unit='ms')
df['rating'] = (df['purchase_date'] - df['purchase_date'].min()).dt.days  # 최근 날짜를 기준으로 점수화

# surprise의 Reader 객체 생성
reader = Reader(rating_scale=(df['rating'].min(), df['rating'].max()))
data = Dataset.load_from_df(df[['member_id', 'product_id', 'rating']], reader)

# 학습 및 테스트 데이터 분할
trainset, testset = train_test_split(data, test_size=0.25)

# SVD 모델 학습
model = SVD()
model.fit(trainset)

# 추천 함수
def recommend_products(member_id, top_n=5):
    # 전체 상품 리스트
    all_product_ids = set(df['product_id'].unique())
    # 사용자가 구매한 상품 제외
    purchased_product_ids = set()
    # 추천할 상품을 위한 점수 계산
    recommendations = []
    for product_id in all_product_ids - purchased_product_ids:
        pred = model.predict(member_id, product_id)
        recommendations.append((product_id, pred.est))
    # 점수에 따라 상품 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [product_id for product_id, _ in recommendations[:top_n]]

# 회원 ID 1의 추천 상품
print("회원 ID 1의 추천 상품:", recommend_products(1))
