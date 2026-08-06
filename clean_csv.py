import pandas as pd

# ==================================================
# 카테고리별 파일 설정
# ==================================================

CATEGORY_CONFIG = {

    "living_table": {
        "input": r"C:\flask-team-project-data-analysis\output_living_table\ikea_living_table_100_products.csv",
        "output": r"C:\flask-team-project-data-analysis\output_living_table\ikea_living_table_100_products.csv",
        "code": "LT"
    },


    "dining_table": {
        "input": r"C:\flask-team-project-data-analysis\output_dining_table\dining_table_100_products.csv",
        "output": r"C:\flask-team-project-data-analysis\output_dining_table\dining_table_100_products.csv",

        "code": "DT"
    }

}

# ==================================================
# 1. filter_color 정제
# ==================================================

color_map = {

    "블루": [
        "라이트블루",
        "다크블루",
        "블루"
    ],

    "옐로우": [
        "옐로그린",
        "다크옐로",
        "옐로"
    ],

    "핑크": [
        "핑크",
        "레드",
        "와인"
    ],

    "그린": [
        "그린"
    ],

    "블랙": [
        "블랙"
    ],

    "그레이": [
        "다크그레이",
        "라이트그레이",
        "그레이"
    ],

    "베이지": [
        "베이지"
    ],

    "화이트": [
        "화이트"
    ],

    "우드": [
        "브라운"
    ]

}


def extract_color(name):
    found = []

    for result_color, keywords in color_map.items():
        for keyword in keywords:
            index = name.find(keyword)

            if index != -1:
                found.append(
                    (index, result_color)
                )

    if found:
        found.sort(
            key=lambda x:x[0]
        )
        return found[0][1]
    return "우드"


# ==================================================
# 2. filter_style 생성
# ==================================================

style_map = {

    "블루": "summer",
    "옐로우": "summer",
    "핑크": "spring",
    "그린": "spring",
    "블랙": "winter",
    "그레이": "winter",
    "우드": "fall",
    "베이지": "all",
    "화이트": "all"

}

# ==================================================
# 카테고리별 실행
# ==================================================

for category, config in CATEGORY_CONFIG.items():


    print("==============================")
    print(category, "정제 시작")
    print("==============================")


    # CSV 불러오기
    df = pd.read_csv(
        config["input"]
    )


    # 1. filter_color 생성
    df["filter_color"] = df["product_name"].apply(
        extract_color
    )


    # 2. filter_style 생성
    df["filter_style"] = df["filter_color"].map(
        style_map
    )


    # 3. mood_code 생성
    df["mood_code"] = df["filter_style"]



    # 4. 카테고리별 상품 삭제
    if category == "living_table":

        # 의자패드 삭제
        df = df[
            ~df["product_name"].str.contains(
                "의자패드",
                na=False
            )
        ]


    elif category == "dining_table":

        # 펜던트, 식탁매트 삭제
        df = df[
            ~df["product_name"].str.contains(
                "펜던트|식탁매트",
                na=False
            )
        ]


    # 5. mood_code_number 생성
    df["mood_code_number"] = [
        f"MC-{config['code']}-{i:03d}"
        for i in range(1, len(df)+1)
    ]


    # 6. 상품 상태 초기화
    df["is_popular"] = None
    df["is_new"] = None
    df["is_best"] = None


    # --------------------------------
    # 저장
    # --------------------------------

    df.to_csv(
        config["output"],
        index=False,
        encoding="utf-8-sig"
    )


    print(
        category,
        "저장 완료"
    )

print("==============================")
print("Living Table + Dining Table 정제 완료")
print("==============================")