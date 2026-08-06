import pandas as pd
import numpy as np
import re
import os

# 1. 파일 로드
script_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(script_dir, 'sofa_100_products.csv')

try:
    df = pd.read_csv(filepath)
    print("✅ 데이터 로드 성공!")
except FileNotFoundError:
    print(f"❌ 오류: {filepath} 파일을 찾을 수 없습니다. 경로와 파일명을 다시 확인해 주세요.")
    exit()

# ---------------------------------------------------------
# [기본 보정] 가격 결측치 처리 및 이케아 브랜드명 치환
# ---------------------------------------------------------
if 'price' in df.columns:
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['price'] = df['price'].replace(0, np.nan).ffill().bfill().astype(int)

def replace_brand(text):
    if pd.isna(text): return text
    return re.sub(r'(?i)IKEA|이케아', 'Mood Code', str(text))

df['product_name'] = df['product_name'].apply(replace_brand)
if 'description' in df.columns:
    df['description'] = df['description'].apply(replace_brand)

df['brand'] = 'Mood Code'
df['category_code'] = 'SOFA'

# ---------------------------------------------------------
# 💡 [핵심] 2인소파 분리 및 세부 분류 맵핑 로직
# ---------------------------------------------------------
def extract_sub_category(product_name):
    if pd.isna(product_name):
        return '기타'
    
    name = str(product_name)
    
    # 1. 암체어, 안락의자 분류
    if any(kw in name for kw in ['암체어', '안락의자', '암 체어']):
        return '암체어'
        
    # 2. 리클라이너 분류
    if any(kw in name for kw in ['리클라이너', '전동']):
        return '리클라이너'
        
    # 3. 4인소파 분류
    if any(kw in name for kw in ['4인', '4인용']):
        return '4인소파'
        
    # 4. 2인소파 분류 (2인용, 2인)
    if any(kw in name for kw in ['2인', '2인용']):
        return '2인소파'
        
    # 5. 긴의자, 3인소파, 코너/카우치/모듈 -> '3인 소파'
    if any(kw in name for kw in ['긴의자', '3인', '3인용', '코너', '카우치', '모듈']):
        return '3인 소파'
        
    # 6. 더 이상 분류되지 않는 나머지는 '기타'
    return '기타'

df['sub_category'] = df['product_name'].apply(extract_sub_category)

# ---------------------------------------------------------
# [핵심 1] 9가지 지정 컬러 매핑 로직
# ---------------------------------------------------------
color_keywords = {
    '블루': ['블루', '파랑', '네이비', '소라', '청색'],
    '옐로우': ['옐로우', '노랑', '머스타드', '레몬', '오렌지', '옐로'],
    '핑크': ['핑크', '분홍', '코랄', '피치'],
    '그린': ['그린', '초록', '민트', '카키', '올리브'],
    '블랙': ['블랙', '검정', '까망', '다크'],
    '그레이': ['그레이', '회색', '차콜', '실버', '트레순드'],
    '우드': ['우드', '원목', '나무', '브라운', '갈색', '오크', '월넛', '라탄'],
    '화이트': ['화이트', '흰색', '아이보리', '크림', '하얀'],
    '베이지': ['베이지', '오트밀', '샌드', '내추럴']
}

def extract_color(row):
    name = str(row['product_name']).strip()
    desc = str(row.get('description', '')).strip()
    full_text = name + " " + desc
    first_word = name.split()[0] if name else ''
    
    for std_color, keywords in color_keywords.items():
        if any(kw in first_word for kw in keywords):
            return std_color
            
    for std_color, keywords in color_keywords.items():
        if any(kw in full_text for kw in keywords):
            return std_color
            
    return '육안확인'

df['filter_color'] = df.apply(extract_color, axis=1)

# ---------------------------------------------------------
# [핵심 2] 컬러 기반 시즌(계절) 자동 매핑 (autumn -> fall 변경)
# ---------------------------------------------------------
def map_season(color):
    if color in ['블루', '옐로우']: return 'summer'
    if color in ['핑크', '그린']: return 'spring'
    if color in ['블랙', '그레이']: return 'winter'
    if color in ['우드']: return 'fall'
    if color in ['화이트', '베이지']: return 'all'
    return 'spring'

df['filter_style'] = df['filter_color'].apply(map_season)
df['mood_code'] = df['filter_style'] 

# ---------------------------------------------------------
# 💡 [핵심 3] 무드 코드 넘버 순차적 부여 (MC-SF-001 ~)
# ---------------------------------------------------------
df['mood_code_number'] = [f"MC-SF-{i:03d}" for i in range(1, len(df) + 1)]

# 기타 필터 및 할인율 세팅
df['filter_space'] = 'living'
df['discount_rate'] = 10       
if 'price' in df.columns:
    df['discount_price'] = (df['price'] * (1 - df['discount_rate'] / 100)).astype(int)

# ---------------------------------------------------------
# 💡 [핵심 4] MD 픽 컬럼들 공란(빈 값)으로 처리
# ---------------------------------------------------------
df['is_popular'] = np.nan
df['is_new'] = np.nan
df['is_best'] = np.nan

# ---------------------------------------------------------
# [최종 정리] 결과 저장
# ---------------------------------------------------------
required_columns = [
    'product_name', 'brand', 'price', 'category_code', 'sub_category',
    'description', 'mood_code_number', 'image_name', 'filter_color', 
    'filter_style', 'filter_space', 'mood_code',
    'discount_rate', 'discount_price', 'is_popular', 'is_new', 'is_best'
]

final_cols = [c for c in required_columns if c in df.columns]
df_final = df[final_cols]

df_final.to_csv(filepath, index=False, encoding='utf-8-sig')

print(f"✅ 작업 완료! '{filepath}' 파일에 fall 시즌 반영 및 모든 규칙이 적용되었습니다.")