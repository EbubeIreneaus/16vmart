<h1 align="center">
  <img src="docs/home-default.png" alt="16vMart — Marketplace for Everyday Life" width="100%"/>
</h1>

<h1 align="center">16vMart — Production Multi-Vendor E-Commerce Platform</h1>

<p align="center">
  A full-stack marketplace engineered from the ground up with async Python, Vue 3, distributed background processing, and Stripe-powered multi-vendor payments.
</p>

<p align="center">
  <a href="https://16vmart.name.ng" target="_blank"><strong>🌐 Live Demo → 16vmart.name.ng</strong></a>
</p>

<p align="center">
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.139+-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI"/></a>
  <a href="https://nuxt.com/"><img src="https://img.shields.io/badge/Nuxt-3.x-00DC82.svg?style=flat&logo=Nuxt.js&logoColor=white" alt="Nuxt 3"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.13+-3776AB.svg?style=flat&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white" alt="TypeScript"/></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-Async_ORM-4169E1.svg?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL"/></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/Redis-7-DC382D.svg?style=flat&logo=redis&logoColor=white" alt="Redis"/></a>
  <a href="https://stripe.com/"><img src="https://img.shields.io/badge/Stripe-SDK_v15-008CDD.svg?style=flat&logo=stripe&logoColor=white" alt="Stripe"/></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white" alt="Docker"/></a>
</p>

---

## Overview

**16vMart** is a production-deployed multi-vendor marketplace where any registered user can open a store, list products, and receive payments — all through a single unified checkout flow. Buyers can add items from multiple independent stores to one cart and pay once; the platform automatically handles splitting the transaction into per-vendor sub-orders in the background.

The project is built across two isolated services: a **FastAPI async backend** (Python 3.13) and a **Nuxt 3 / Vue 3 frontend** (TypeScript), orchestrated with Docker Compose and deployed live.

Key engineering decisions that differentiate this from a CRUD tutorial:

- **Webhook-driven order lifecycle**: Stripe webhooks trigger background jobs via Redis queues — the HTTP layer never blocks on payment processing.
- **Idempotent checkout**: Every order is guarded by a UUID idempotency key enforced at the database level, preventing duplicate charges even under network retries.
- **Redis-first session auth**: Authenticated request paths hit Redis first; the database is only queried on cache miss, with TTL-synced expiry.
- **Distributed ARQ worker**: A self-contained async worker process consumes job queues independently of the API server, enabling horizontal scalability.

---

## Screenshots

<table>
  <tr>
    <td align="center"><strong>Marketplace Homepage</strong></td>
    <td align="center"><strong>Product Catalog with Filters</strong></td>
  </tr>
  <tr>
    <td><img src="docs/home-default.png" alt="Marketplace Homepage"/></td>
    <td><img src="docs/product-list.png" alt="Product Catalog"/></td>
  </tr>
  <tr>
    <td align="center"><strong>Product Detail — Dynamic Attributes</strong></td>
    <td align="center"><strong>Seller Onboarding — Create Store</strong></td>
  </tr>
  <tr>
    <td><img src="docs/single-product.png" alt="Product Detail Page"/></td>
    <td><img src="docs/create-store.png" alt="Create a Store"/></td>
  </tr>
  <tr>
    <td align="center"><strong>Vendor Dashboard — Catalog Management</strong></td>
    <td align="center"><strong>Vendor Order & Payout Detail</strong></td>
  </tr>
  <tr>
    <td><img src="docs/store-manage-product.png" alt="Store Product Management"/></td>
    <td><img src="docs/store-vendor-order-slug.png" alt="Vendor Order Detail"/></td>
  </tr>
</table>

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                               │
│         Nuxt 3 / Vue 3 SPA  →  SSR / CSR hybrid rendering       │
│         Pinia state  │  Nuxt UI  │  TypeScript composables       │
└────────────────────────────┬─────────────────────────────────────┘
                             │ REST / JSON (HTTP)
┌────────────────────────────▼─────────────────────────────────────┐
│                     API GATEWAY LAYER                             │
│    FastAPI (ASGI / Uvicorn)  •  CORS  •  SlowAPI Rate Limiting   │
│    OAuth2PasswordBearer  •  JWT decode  •  RBAC middleware        │
└───────────┬────────────────────────────────────┬─────────────────┘
            │                                    │
  ┌─────────▼──────────┐              ┌──────────▼──────────────┐
  │   PostgreSQL DB     │              │    Redis 7               │
  │  AsyncPG + SQLAlch. │              │  Session cache           │
  │  Alembic migrations │              │  Store / cart cache      │
  │  Indexed slugs      │              │  ARQ job queue           │
  └─────────────────────┘              └──────────┬──────────────┘
                                                  │  dequeue
                                       ┌──────────▼──────────────┐
                                       │   ARQ Background Worker  │
                                       │  update_order task       │
                                       │  create_vendor_orders    │
                                       │  transactional email      │
                                       └─────────────────────────┘
            │ Stripe Checkout Session                │
  ┌─────────▼──────────┐              ┌─────────────▼────────────┐
  │   Stripe SDK v15    │              │  Cloudinary CDN           │
  │  Async client       │              │  Media upload & hosting  │
  │  Webhook validation │              └──────────────────────────┘
  └─────────────────────┘
```

---

## Engineering Deep-Dives

### 1. Stripe Checkout + Webhook-Driven Order Pipeline

Checkout is intentionally kept out of the synchronous HTTP cycle. When a user submits an order:

1. The API creates an `Order` row with `status=PENDING` and generates a Stripe Checkout Session, passing `client_reference_id=order_number` and an **idempotency key** derived from a UUID stored on the order.
2. The user pays on Stripe's hosted page. Stripe fires a `checkout.session.completed` webhook back to the API.
3. The webhook handler verifies the Stripe signature and immediately **enqueues an ARQ job** (`update_order`) to the Redis queue — returning `{"received": true}` in milliseconds.
4. The **background worker** picks up the job, marks the order `PROCESSING`, then enqueues a second job (`create_vendor_orders`) which fans out the purchase into one `VendorOrder` row per store involved, computing each store's subtotal.

This two-stage async fan-out means vendors see their orders appear automatically, with zero admin intervention.

```python
# routers/v1/order.py — webhook handler
match event["type"]:
    case "checkout.session.completed":
        await arq.enqueue_job(
            "update_order", ORDER_STATUS.PROCESSING, order_number,
            _queue_name="16vmart"
        )
    case "checkout.session.expired":
        await arq.enqueue_job(
            "update_order", ORDER_STATUS.CANCELLED, order_number,
            _queue_name="16vmart"
        )
```

```python
# bg_task/order.py — vendor order fan-out
vendor_totals = defaultdict(list)
for item in order.items:
    vendor_totals[item.product.store_id].append(item.unit_price * item.quantity)

vendor_orders = [
    VendorOrder(store_id=sid, order_id=order.id, subtotal=sum(prices))
    for sid, prices in vendor_totals.items()
]
db.add_all(vendor_orders)
```

### 2. Redis-First Session Authentication

Every authenticated endpoint calls `get_user()`, which checks Redis before touching Postgres:

```python
session_raw = await redis.get(f"16vmart:session:{session_id}")

if session_raw:
    session = SessionUserSchema.model_validate_json(session_raw)
else:
    # DB fallback — only on cold cache
    s = await db.scalar(
        select(Session)
        .options(selectinload(Session.user))
        .where(Session.id == session_id, Session.expired_at > now)
    )
    # Write-through: cache with remaining TTL from DB record
    await redis.set(f"16vmart:session:{session.id}", json_session, ex=seconds_left)
```

Session rows in Postgres track `ip_address`, `device`, `location`, `refresh_token_hash`, and `expired_at` — giving full per-session revocation capability without touching the JWT.

### 3. Dynamic Product Attribute System

Products have a flexible attribute schema tied to their category. Each `AttributeKey` defines a `form_type` (`text`, `number`, `boolean`, `date`, `json`) and optional enum `options`. `ProductAttribute` rows store values in typed columns (`text_value`, `number_value`, `json_value`, etc.) with a composite unique constraint:

```python
__table_args__ = (
    UniqueConstraint("product_id", "attribute_id", name="uq_product_attribute"),
)
```

Adding a new category with custom specs — RAM for electronics, Fabric for fashion — requires zero code changes. The schema is fully data-driven from the database.

### 4. RBAC with Four Privilege Tiers

| Role | Access |
|:---|:---|
| `USER` | Browse catalog, cart, wishlist, place orders |
| `SELLER` | All USER access + store dashboard, product & order management |
| `ADMIN` | All SELLER access + platform-wide moderation & payout management |
| `SUPERADMIN` | Unrestricted platform access |

Guards are implemented as FastAPI dependency functions (`get_user`, `get_store`, `get_admin`, `get_superadmin`) composable via `Depends()`, keeping route handlers free of auth boilerplate.

### 5. N+1 Query Elimination via Selective Eager Loading

SQLAlchemy async queries use `selectinload` chains for nested object graphs only where necessary — never globally. Example from the order detail endpoint:

```python
select(Order)
    .options(
        selectinload(Order.delivery_address),
        selectinload(Order.items).options(
            selectinload(OrderProduct.product).options(
                selectinload(Product.images),
                selectinload(Product.category)
            )
        ),
    )
    .where(Order.order_number == order_number, Order.user_id == user.id)
```

This resolves a full order with nested line items, product images, and categories in **two queries** — not N+1.

---

## Tech Stack

| Layer | Technologies |
|:---|:---|
| **Backend** | FastAPI 0.139+, Python 3.13, Uvicorn (ASGI) |
| **Frontend** | Nuxt 3, Vue 3, TypeScript, Pinia, Nuxt UI, TailwindCSS |
| **Database** | PostgreSQL, SQLAlchemy 2.0 (async), AsyncPG, Alembic |
| **Caching & Queue** | Redis 7 (hiredis), ARQ async worker |
| **Auth** | PyJWT, Argon2 (pwdlib), OAuth2PasswordBearer |
| **Payments** | Stripe SDK v15 (async client + webhook processing) |
| **Media** | Cloudinary (upload + CDN hosting) |
| **Rate Limiting** | SlowAPI |
| **Email** | FastAPI-Mail (transactional HTML templates) |
| **DevOps** | Docker, Docker Compose |
| **Testing** | Pytest, Pytest-Asyncio, Playwright (E2E) |
| **UA Parsing** | ua-parser, user-agents (device/session detection) |

---

## Project Structure

```
16vmart/
├── compose.yaml                   # Multi-service Docker Compose
├── api/                           # FastAPI application
│   ├── alembic/                   # Database migration history
│   ├── bg_task/
│   │   ├── config.py              # ARQ WorkerSettings & Redis pool
│   │   ├── auth.py                # Auth background tasks
│   │   └── order.py              # update_order / create_vendor_orders jobs
│   ├── email_templates/           # HTML transactional email templates
│   ├── libs/
│   │   ├── deps.py               # Dependency injectors: get_user, get_store, get_admin
│   │   ├── jwt.py                # JWT encode/decode
│   │   ├── redis.py              # Shared async Redis client
│   │   ├── limiter.py            # SlowAPI limiter instance
│   │   ├── cloudinary.py         # Cloudinary config
│   │   └── mail_config.py        # FastAPI-Mail connection config
│   ├── models/
│   │   ├── user.py               # User, Session, Address, Store
│   │   ├── product.py            # Product, Category, AttributeKey, ProductAttribute
│   │   └── shopping.py           # Order, OrderProduct, VendorOrder, Wishlist
│   ├── routers/v1/
│   │   ├── auth.py               # Register, login, refresh, logout, sessions
│   │   ├── order.py              # Checkout, Stripe webhook, order history
│   │   ├── product.py            # Catalog browsing & search
│   │   ├── cart.py               # Persistent Redis cart operations
│   │   ├── wishlist.py           # Wishlist management
│   │   ├── user.py               # Profile & address management
│   │   ├── cat.py                # Category tree
│   │   ├── store/                # Vendor store CRUD, products, orders
│   │   └── admin/                # Admin platform management
│   ├── schemas/                   # Pydantic v2 request/response schemas
│   ├── main.py                    # App factory, middleware, router registration
│   └── pyproject.toml
└── web/                           # Nuxt 3 frontend
    ├── app/
    │   ├── pages/
    │   │   ├── index.vue          # Marketplace homepage
    │   │   ├── products/          # Catalog & product detail
    │   │   ├── cart.vue           # Shopping cart
    │   │   ├── checkout/          # Checkout flow + success/cancel
    │   │   ├── vendor/            # Vendor dashboard (products, orders, profile)
    │   │   ├── admin/             # Admin dashboard
    │   │   └── account/           # Customer account & order history
    │   ├── components/            # Reusable Vue components
    │   ├── composables/           # API composables (useFetch wrappers)
    │   ├── stores/                # Pinia state (auth, cart, UI)
    │   ├── middleware/            # Nuxt route guards
    │   └── types/                 # TypeScript type definitions
    ├── tests/e2e/                 # Playwright end-to-end tests
    └── nuxt.config.ts
```

---

## Business Workflows

### 🛍️ Customer Journey
1. Register → session created with device/IP tracking stored in Postgres
2. Browse catalog with category, price, and condition filters
3. Add products from **any number of stores** into a single persistent Redis cart
4. Checkout: one Stripe payment covers all stores in the cart
5. Stripe webhook fires → background worker confirms payment, fans out vendor sub-orders

### 🏪 Vendor Journey
1. Open a store (submitted for admin review, moderated before going live)
2. List products with **category-specific dynamic attributes** and Cloudinary-hosted images
3. Monitor the vendor dashboard — sales, per-order breakdowns, payout status per `VendorOrder`

### 👑 Admin Journey
1. Review and approve or suspend store applications
2. Moderate the global product catalog
3. Track vendor payout statuses across all platform orders

---

## Getting Started

### Prerequisites
- [Docker Engine](https://docs.docker.com/get-docker/) & Docker Compose Plugin
- [Node.js 20+](https://nodejs.org/) (frontend only)
- [Python 3.13+](https://www.python.org/) (API local dev only)

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/16vmart.git
cd 16vmart
```

**`api/.env`** — backend secrets:
```env
APP_NAME=16vMart
APP_URL=http://localhost:3000
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vmart_db
REDIS_HOST=redis
REDIS_PORT=6379
SECRET_KEY=your-jwt-secret
STRIPE_SECRET=sk_test_...
STRIPE_HOOK_SECRET=whsec_...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
MAIL_USERNAME=...
MAIL_PASSWORD=...
MAIL_FROM=no-reply@16vmart.com
```

**`web/.env`** — frontend:
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

### 2. Run with Docker Compose (Recommended)

Starts the FastAPI API (with embedded ARQ worker) and Redis:

```bash
docker compose up --build
```

| Service | URL |
|:---|:---|
| FastAPI API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| Redis | `localhost:6379` |

Start the Nuxt frontend separately:

```bash
cd web && npm install && npm run dev
# → http://localhost:3000
```

### 3. Local Development (No Docker)

```bash
# Backend
cd api
pip install -r requirements.txt
alembic upgrade head
python seed_categories.py   # optional
python seed_products.py     # optional
uvicorn main:app --reload --port 8000

# Background worker (separate terminal)
arq bg_task.config.WorkerSettings

# Frontend (separate terminal)
cd web && npm install && npm run dev
```

---

## Testing

```bash
# Backend unit & integration tests
cd api && pytest

# Frontend end-to-end (Playwright)
cd web && npm run test:e2e
```

---

## Deployment Notes

- The API and ARQ worker are co-hosted in a single Docker container; the worker starts via `asyncio.create_task()` on FastAPI's `startup` event. This works for a single-node deployment — for horizontal scale-out, extract the worker into its own Docker service with a shared Redis connection.
- Configure your Stripe webhook URL in the Stripe dashboard pointing to `https://your-domain.com/api/v1/shopping/stripe-webhook`.
- PostgreSQL runs external to the Docker Compose setup, connected via `host.docker.internal` in the current `compose.yaml`.

---

## License

[MIT](LICENSE) — open-source and free to use.
