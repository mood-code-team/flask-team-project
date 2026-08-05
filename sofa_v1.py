import pandas as pd
import numpy as np
import os
import re

# 1. 데이터 로드
input_filepath = os.path.join('output_sofa', 'sofa_100_products.csv')
df = pd.read_csv(input_filepath)

# ---------------------------------------------------------
# [가격 보정] 0원 결측치 처리 및 정수(int) 변환
# ---------------------------------------------------------
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['price'] = df['price'].replace(0, np.nan)
df['price'] = df['price'].ffill().bfill()
df['price'] = df['price'].astype(int)

# ---------------------------------------------------------
# [1] 상세 카테고리(sub_category) 추출 
# ---------------------------------------------------------
def extract_sub_category(name):
    name = str(name)
    match = re.search(r'(\d+인용|소파베드|코너소파|모듈형|모듈식)', name)
    if match:
        return match.group(1)
    return '기타소파'

df['sub_category'] = df['product_name'].apply(extract_sub_category)

# ---------------------------------------------------------
# [2] 상품명에서 컬러 추출 및 불필요한 단어 제거
# ---------------------------------------------------------
def extract_color(name):
    name = str(name).strip() # 앞뒤 불필요한 여백 제거
    
    if ' ' in name:
        # 1. 오른쪽(뒤)에서부터 공백 ' '을 기준으로 마지막 단어만 추출
        color = name.rsplit(' ', 1)[-1]
        
        # 2. 제거하고 싶은 단어 목록 (필요시 여기에 계속 추가하시면 됩니다)
        remove_words = ['다크', '미디엄', '멀티컬러', '/', '골든', '메탈', '우드', '브라이트']
        
        # 3. 추출된 텍스트에서 해당 단어들을 찾아 모두 지우기 ('')
        for word in remove_words:
            color = color.replace(word, '')
            
        # 단어를 지우고 남은 텍스트의 앞뒤 공백을 한 번 더 깔끔하게 정리하여 반환
        return color.strip() 
        
    return ''

df['filter_color'] = df['product_name'].apply(extract_color)

# ---------------------------------------------------------
# [3] 상품설명(description)에서 상품명 텍스트 제외하기
# ---------------------------------------------------------
def clean_description(row):
    desc = str(row['description'])
    p_name = str(row['product_name'])
    
    if p_name in desc:
        desc = desc.replace(p_name, '')
        desc = desc.lstrip(' .,-')
        
    return desc.strip()

df['description'] = df.apply(clean_description, axis=1)

# ---------------------------------------------------------
# 💡 [신규 추가] 상품명/상세설명 내 '이케아' 및 'IKEA' 텍스트 치환
# ---------------------------------------------------------
def replace_brand_name(text):
    if pd.isna(text):
        return text
    # (?i) 옵션으로 영문 대소문자(IKEA, ikea 등) 무시하고, 한글 '이케아'까지 잡아냄
    return re.sub(r'(?i)IKEA|이케아', 'Mood Code', str(text))

df['product_name'] = df['product_name'].apply(replace_brand_name)
df['description'] = df['description'].apply(replace_brand_name)

# ---------------------------------------------------------
# [4] 이미지 경로 제외하고 파일명만 남기기 (image_name 생성)
# ---------------------------------------------------------
if 'local_image_path' in df.columns:
    df['image_name'] = df['local_image_path'].apply(
        lambda x: str(x).replace('\\', '/').split('/')[-1] if pd.notnull(x) else ''
    )
    df = df.drop(columns=['local_image_path'])

# ---------------------------------------------------------
# [5] 브랜드명 및 기본 필터 세팅
# ---------------------------------------------------------
df['brand'] = 'Mood Code'

target_mood = 'spring' 
df['mood_code'] = target_mood
df['filter_style'] = target_mood

# 무드코드 넘버는 나중에 일괄 부여하기 위해 빈칸 처리
df['mood_code_number'] = ''

df['filter_space'] = 'living'  # 쇼파는 전부 리빙
df['discount_rate'] = 10       # 일괄 10% 할인
# 💡 할인율을 적용하여 할인가 계산 (원가 - (원가 * 할인율/100)) 후 소수점 제거(int)
df['discount_price'] = (df['price'] * (1 - df['discount_rate'] / 100)).astype(int)
df['is_popular'] = False
df['is_new'] = False
df['is_best'] = False

drop_cols = ['external_source', 'external_id', 'currency', 'stock_status', 'image_preview', 'source_url', 'use_product']
df = df.drop(columns=[c for c in drop_cols if c in df.columns])

# ---------------------------------------------------------
# 최종 컬럼 순서 재배치 (thumbnail_url 제거)
# ---------------------------------------------------------
final_columns = [
    'product_name', 'brand', 'price', 'category_code', 'sub_category', 
    'description', 'mood_code_number', 'image_name',
    'filter_color', 'filter_style', 'filter_space', 'mood_code',
    'discount_rate', 'discount_price', 'is_popular', 'is_new', 'is_best'
]
df_final = df[[c for c in final_columns if c in df.columns]].copy()

# ---------------------------------------------------------
# 폴더 생성 및 파일 저장 (CSV + Excel 추가)
# ---------------------------------------------------------
folder_name = '1차소트'

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# 1. CSV 저장
output_filepath_csv = os.path.join(folder_name, 'sofa_v1.csv')
df_final.to_csv(output_filepath_csv, index=False, encoding='utf-8-sig')

# 2. Excel 저장
output_filepath_excel = os.path.join(folder_name, 'sofa_v1.xlsx')
df_final.to_excel(output_filepath_excel, index=False)

print(f"브랜드명 치환 및 모든 정제 작업 완료! '{output_filepath_csv}' 및 '{output_filepath_excel}' 파일이 생성되었습니다. 🚀")