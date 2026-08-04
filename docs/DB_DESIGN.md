# DB 설계 — Mood Code

## ER 다이어그램

```mermaid
erDiagram
    users ||--o{ cart : "has"
    users ||--o{ orders : "places"
    categories ||--o{ products : "contains"
    categories ||--o{ categories : "parent"
    products ||--o{ cart : "in"
    products ||--o{ order_items : "referenced"
    orders ||--|{ order_items : "contains"

    users {
        int id PK
        string email UK
        string username UK
        string password_hash
        string phone
        string address
        bool is_admin
        bool is_active
        datetime created_at
        datetime updated_at
    }

    categories {
        int id PK
        string name UK
        string slug UK
        string description
        string icon
        int sort_order
        bool is_active
        int parent_id FK
        datetime created_at
    }

    products {
        int id PK
        int category_id FK
        string name
        string slug UK
        text description
        int price
        int discount_price
        int stock
        string image_url
        bool has_installation
        bool is_popular
        bool is_new
        bool is_best
        bool is_active
        datetime created_at
        datetime updated_at
    }

    cart {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
        datetime created_at
        datetime updated_at
    }

    orders {
        int id PK
        int user_id FK
        string order_number UK
        string status
        int total_amount
        string recipient_name
        string recipient_phone
        string shipping_address
        string shipping_memo
        datetime created_at
        datetime updated_at
    }

    order_items {
        int id PK
        int order_id FK
        int product_id FK
        string product_name
        int unit_price
        int quantity
        int subtotal
    }

    notices {
        int id PK
        string title
        text content
        bool is_pinned
        bool is_active
        datetime created_at
        datetime updated_at
    }

    faqs {
        int id PK
        string category
        string question
        text answer
        int sort_order
        bool is_active
        datetime created_at
    }
```

## 테이블 관계 요약

| 관계 | 타입 | 설명 |
|------|------|------|
| User → CartItem | 1:N | 회원당 여러 장바구니 항목 |
| User → Order | 1:N | 회원당 여러 주문 |
| Category → Product | 1:N | 카테고리별 상품 |
| Category → Category | 1:N | 상위/하위 카테고리 (self-ref) |
| Product → CartItem | 1:N | 상품이 여러 장바구니에 |
| Order → OrderItem | 1:N | 주문당 여러 상품 |
| Product → OrderItem | 1:N | 주문 시 상품 참조 |

## 주문 상태 (OrderStatus)

| 값 | 라벨 | 설명 |
|----|------|------|
| pending | 주문 접수 | 주문 생성 직후 |
| paid | 결제 완료 | 결제 확인 |
| preparing | 상품 준비 | 출고 준비 |
| shipping | 배송 중 | 운송장 등록 |
| delivered | 배송 완료 | 수령 확인 |
| cancelled | 취소 | 주문 취소 |

## 인덱스 전략

- `users.email`, `users.username` — 로그인 조회
- `products.category_id`, `products.slug` — 목록/상세
- `cart(user_id, product_id)` — UNIQUE, 중복 방지
- `orders.order_number` — 주문 조회

## MySQL 전환

```bash
set DATABASE_URL=mysql+pymysql://user:password@localhost/hspace_shop
pip install pymysql
```

`config.py`의 `SQLALCHEMY_DATABASE_URI`가 환경 변수를 자동 사용합니다.
