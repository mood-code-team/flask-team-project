import os
import glob
import pandas as pd

# 1. 현재 파이썬 파일이 위치한 폴더 경로 및 이름 자동 인식
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_NAME = os.path.basename(CURRENT_DIR)

# 2. 현재 폴더 내 CSV 파일 탐색
csv_files = glob.glob(os.path.join(CURRENT_DIR, '*.csv'))

if not csv_files:
    print(f"❌ [{FOLDER_NAME}] 폴더 내에 CSV 파일이 존재하지 않습니다.")
    exit()

csv_path = csv_files[0]
excel_path = os.path.splitext(csv_path)[0] + '.xlsx'

print(f"📂 [{FOLDER_NAME}] 작업 시작 -> 대상 파일: {os.path.basename(csv_path)}")

# 3. CSV 파일 읽기
df = pd.read_csv(csv_path)

# 4. 대상 컬럼 지정: 'product_name' 컬럼 최우선 지정
target_col = None
if 'product_name' in df.columns:
    target_col = 'product_name'
else:
    for col in df.columns:
        if any(k in col.lower() for k in ['product', '상품', 'title', 'name']):
            target_col = col
            break

if not target_col:
    target_col = df.columns[0]

print(f"🎯 색상 분석 대상 컬럼: [{target_col}]")

# 5. product_name을 분석하여 지정된 표준 색상명으로 정제 추출하는 함수
def extract_primary_color(text):
    if pd.isna(text):
        return '화이트'  # 기본값
    
    text_str = str(text).lower().strip()
    
    # 표준 색상 키워드 사전
    color_map = {
        '베이지': ['베이지', '라이트베이지', '라이트 베이지', '화이트베이지', '오프화이트', '크림', 'beige', 'cream'],
        '그레이': ['그레이', '다크그레이', '다크 그레이', '라이트그레이', '회색', '차콜', 'gray', 'grey'],
        '우드': ['우드', '원목', '목재', '브라운', '갈색', '내추럴', '내츄럴', 'wood', 'brown', 'natural'],
        '화이트': ['화이트', '아이보리', 'white', 'ivory'],
        '블랙': ['블랙', '검정', 'black'],
        '핑크': ['핑크', '분홍', 'pink'],
        '옐로우': ['옐로우', '노랑', '멜로우', 'yellow'],
        '그린': ['그린', '초록', 'green'],
        '블루': ['블루', '파랑', '네이비', 'blue', 'navy']
    }
    
    for standard_color, keywords in color_map.items():
        if any(keyword in text_str for keyword in keywords):
            return standard_color
            
    return '화이트'

# 6. 계절 컬러 범주화 함수 (영문: spring, summer, autumn, winter)
def map_season_style(color_text):
    color = str(color_text).strip()
    
    if color in ['화이트']:
        return 'etc'
    elif color in ['핑크', '그린']:
        return 'spring'
    elif color in ['블루', '옐로우']:
        return 'summer'
    elif color in ['블랙', '그레이']:
        return 'winter'
    elif color in ['우드', '베이지', '브라운']:
        return 'autumn'
    else:
        return 'etc'

# 7. filter_color 및 filter_style (계절) 컬럼에 직접 결과 반영
extracted_colors = df[target_col].apply(extract_primary_color)
mapped_seasons = extracted_colors.apply(map_season_style)

# filter_color 컬럼 업데이트
df['filter_color'] = extracted_colors

# filter_style 및 mood_code 컬럼에 계절값(spring/summer/autumn/winter) 업데이트
if 'filter_style' in df.columns:
    df['filter_style'] = mapped_seasons
else:
    df['filter_style'] = mapped_seasons

if 'mood_code' in df.columns:
    df['mood_code'] = mapped_seasons

# 불필요한 별도 추출 컬럼이 기존에 존재했다면 정리 (선택 사항)
if '추출컬러' in df.columns:
    df.drop(columns=['추출컬러'], inplace=True)
if '계절컬러' in df.columns:
    df.drop(columns=['계절컬러'], inplace=True)

# is_popular, is_new, is_best 컬럼 빈칸 처리
blank_cols = ['is_popular', 'is_new', 'is_best']
for col in blank_cols:
    if col in df.columns:
        df[col] = ''

# 8. CSV 덮어쓰기 및 XLSX 파일 변환
df.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"✅ 1단계: CSV 덮어쓰기 완료 -> {os.path.basename(csv_path)}")

df.to_excel(excel_path, index=False)
print(f"✅ 2단계: XLSX 덮어쓰기 완료 -> {os.path.basename(excel_path)}")

# 9. 터미널 결과 출력
print("\n📊 [실시간 filter_color / filter_style 업데이트 결과]")
print(df[[target_col, 'filter_color', 'filter_style']].head(10))