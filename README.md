# 🛒 16vMart — Enterprise Multi-Vendor E-Commerce Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.15+-00DC82.svg?style=flat&logo=Nuxt.js&logoColor=white)](https://nuxt.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Stripe](https://img.shields.io/badge/Stripe-Async_SDK-008CDD.svg?style=flat&logo=stripe&logoColor=white)](https://stripe.com/)

**16vMart** is a production-grade, high-performance multi-vendor e-commerce platform designed with scalable system architecture, robust security, distributed task execution, and asynchronous payment processing. 

Built to handle complex marketplace dynamics, 16vMart enables users to register, open custom vendor stores, manage catalog inventory, and process orders via a **unified single-checkout Stripe payment system**. Background worker queues handle order aggregation, splitting sub-orders per store, and tracking vendor pending payouts through a dedicated administrative dashboard.

---

## 🏗 System Design & Engineering Highlights

This project demonstrates production-ready engineering patterns focused on scalability, idempotency, caching, rate limiting, and clean separation of concerns.

### 1. 💳 Unified Single-Payment & Vendor Payout Architecture
- **Multi-Vendor Single Checkout**: Customers purchase products from multiple independent vendors in a single transaction. 
- **Stripe Async Payment Integration**: Uses `stripe[async]` to initiate Checkout Sessions with metadata-driven order numbers and strict idempotency keys (`idempotency_key` header & UUID tracking) to prevent duplicate charges.
- **Asynchronous Webhook Engine**: Listens for `checkout.session.completed` and `checkout.session.expired` webhook events, offloading payment verification out of the synchronous request-response cycle.
- **Pending Payment & Vendor Payout Dashboard**: Automatically breaks down a unified order into individual `VendorOrder` records per seller (`paid` / `unpaid` states), providing administrators and vendors real-time visibility into pending payouts.

### 2. ⚡ Asynchronous Task Processing (ARQ Background Worker)
- **Distributed Job Queue**: Utilizes **ARQ** (Redis-backed async worker) running as a dedicated Docker service (`bg_worker`) to execute heavy or transactional background tasks without blocking HTTP handlers.
- **Idempotent Order Splitting**: `update_order` and `create_vendor_orders` workers safely calculate sub-totals per store and generate vendor order breakdowns asynchronously.
- **Async Mail Pipeline**: Delivers transactional emails asynchronously using `fastapi-mail` triggered by background events.

### 3. 🚀 High-Performance Caching & Session Store (Redis 7)
- **Session Caching**: Eliminates database load on authenticated requests by caching serialized user session objects in Redis (`16vmart:session:{session_id}`) with automatic TTL expiry matching session duration.
- **Store Configuration Caching**: Store details and vendor metadata are cached (`16vmart:store:{user_id}:{slug}`) to accelerate vendor router lookups.
- **Cart Persistence**: Active shopping carts are stored in Redis (`16vmart:cart:{user_id}`) for high-speed read/write operations during browsing.

### 4. 🗄️ Database Indexing & Query Optimization
- **SQLAlchemy 2.0 Async Engine**: Powered by `asyncpg` for non-blocking asynchronous PostgreSQL database access.
- **B-Tree Database Indexing**: Strategic database indexes on query-intensive columns:
  - Unique index on product & store slugs (`products.slug`, `stores.slug`, `categories.slug`)
  - Indexed lookup fields (`orders.order_number`, `orders.idompotent_key`, `vendor_orders.vid`, `addresses.address_id`)
- **N+1 Query Elimination**: Custom eager-loading strategies using `selectinload` across deep object graphs (User -> Orders -> Items -> Product -> Images & Category).
- **Data Integrity**: Enforces database-level constraints such as composite unique constraints (`uq_product_attribute`) and cascading deletions.

### 5. 🔐 Authentication, Session Security & Role-Based Access Control (RBAC)
- **JWT & Session Security**: Hybrid JWT authentication with server-tracked sessions (`Session` model) storing client IP address, user-agent details, and refresh token hashes for instant session revocation.
- **Password Hashing**: Uses modern `Argon2` password hashing via `pwdlib[argon2]`.
- **Granular RBAC Guards**: Tiered access enforcement via FastAPI dependency injection guards:
  - `get_user`: Standard authenticated customer access
  - `get_store`: Seller / Store ownership access guard
  - `get_admin`: Admin dashboard access
  - `get_superadmin`: System-wide admin access

### 6. 🛡️ API Rate Limiting & Resilience
- **SlowAPI Integration**: Rate limiting policy protecting critical endpoints against abuse and brute-force attacks (e.g., Checkout limited to `10/minute`, general API reads capped at `60/minute`).
- **Graceful Error Handling**: Custom exception handlers for rate limits, Stripe errors, and domain validation.

### 7. 🐳 Multi-Container Orchestration (Docker & Docker Compose)
- **Dockerized Services**: Fully containerized environment comprising separate containers for `api` (FastAPI ASGI application), `bg_worker` (ARQ job worker), and `redis` (Cache & Queue broker).
- **Environment Isolation**: Configured volume mounts and isolated python virtual environments inside containers.

---

## 📐 System Architecture

```mermaid
flowchart TD
    subgraph Client Layer
        Web[Nuxt 3 Frontend / Vue 3 + Tailwind]
    end

    subgraph API Gateway & Service Layer
        API[FastAPI Router - Async Uvicorn]
        Limiter[SlowAPI Rate Limiter]
        RBAC[RBAC & JWT Auth Deps]
    end

    subgraph Storage & Infrastructure Layer
        Redis[(Redis 7 - Session / Cart / Cache / Queue)]
        DB[(PostgreSQL / SQLite - SQLAlchemy 2.0 Async)]
    end

    subgraph Background Processing Layer
        ARQ[ARQ Background Worker]
        Mail[FastAPI Mail Service]
    end

    subgraph External Services
        Stripe[Stripe API & Webhook Service]
        Cloudinary[Cloudinary CDN Image Storage]
    end

    Web -->|HTTP / REST| API
    API --> Limiter
    API --> RBAC
    API -->|Cache Session / Cart| Redis
    API -->|Async Queries| DB
    API -->|Upload Media| Cloudinary
    API -->|Create Checkout Session| Stripe
    
    Stripe -->|Stripe Webhooks| API
    API -->|Enqueue Jobs| Redis
    Redis -->|Dequeue Jobs| ARQ
    ARQ -->|Update Orders / Split Payouts| DB
    ARQ -->|Send Notification Emails| Mail
```

---

## 🔄 End-to-End Business Workflows

### 🛍️ Customer Journey
1. **User Registration & Auth**: User registers and authenticates via OAuth2 / JWT with Argon2 encrypted credentials.
2. **Catalog Browsing & Filtering**: Browse products by category hierarchy, text search, and dynamic product attributes.
3. **Cart & Wishlist**: Add products from multiple different stores into a unified persistent cart stored in Redis.
4. **Single Checkout**: Proceed to checkout with address creation or selection. Initiates a single Stripe payment session.
5. **Fulfillment**: Webhooks confirm payment, update order status to `PROCESSING`, and trigger vendor order creation.

### 🏪 Vendor (Store) Journey
1. **Store Onboarding**: Registered users apply to create a seller store (`User` role escalates to `SELLER`).
2. **Product & Inventory Management**: Upload products with rich description editing (Tiptap), dynamic category attribute key-value pairs, and Cloudinary media uploads.
3. **Vendor Orders Dashboard**: Track store sales, inspect itemized sub-orders, and monitor payment status (`paid` vs `unpaid`).

### 👑 Admin Journey
1. **System Administration**: Oversee global users, stores, product listings, and platform metrics via ECharts analytics.
2. **Store & Product Moderation**: Approve, verify, or suspend vendor stores and product listings.
3. **Pending Payment Payout Management**: Inspect global `VendorOrder` listings, review pending payouts per store, and transition payout states.

---

## 🧰 Tech Stack Reference

| Layer | Technologies & Tools |
| :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/), Python 3.13+, Uvicorn ASGI |
| **Frontend Framework** | [Nuxt 3](https://nuxt.com/), Vue 3, TypeScript, Pinia State Management |
| **UI Components & Styling**| Nuxt UI, Tailwind CSS v4, VueUse, ECharts (`nuxt-echarts`), Tiptap Editor |
| **Database & ORM** | PostgreSQL, [SQLAlchemy 2.0 Async](https://www.sqlalchemy.org/), Asyncpg, Alembic Migrations |
| **Caching & In-Memory DB** | [Redis 7](https://redis.io/), `redis-py` (Hiredis parser) |
| **Background Tasks** | [ARQ](https://github.com/samuelcolvin/arq) Async Worker Queue |
| **Payment Gateway** | [Stripe Async SDK](https://stripe.com/), Webhook Event Listeners |
| **Authentication** | PyJWT, Argon2 (`pwdlib[argon2]`), OAuth2 Security Scheme |
| **Rate Limiting** | SlowAPI |
| **Media Hosting** | Cloudinary Python SDK |
| **DevOps & Containers** | Docker, Docker Compose |
| **Testing Frameworks** | Pytest, Pytest-Asyncio (Backend), Playwright E2E (Frontend) |

---

## 📂 Project Structure

```
16vmart/
├── compose.yaml                # Multi-container Docker Compose configuration
├── api/                        # FastAPI Backend Application
│   ├── alembic/                # Database migration scripts
│   ├── bg_task/                # ARQ background worker tasks & configuration
│   │   ├── auth.py             # Auth background tasks
│   │   ├── config.py           # ARQ worker settings & Redis pool
│   │   └── order.py            # Order update & vendor order creation jobs
│   ├── email_templates/        # HTML email templates
│   ├── libs/                   # Core utility libraries & dependencies
│   │   ├── deps.py             # FastAPI RBAC & authentication dependencies
│   │   ├── jwt.py              # JWT token encoding/decoding
│   │   ├── limiter.py          # SlowAPI rate limiter setup
│   │   └── redis.py            # Redis client singleton
│   ├── models/                 # SQLAlchemy database models
│   │   ├── db.py               # Async DB engine & sessionmaker
│   │   ├── product.py          # Product, Category, & Attribute models
│   │   ├── shopping.py         # Order, OrderProduct, VendorOrder, Wishlist
│   │   └── user.py             # User, Session, Address, Store models
│   ├── routers/                # REST API Endpoint Version 1
│   │   └── v1/
│   │       ├── admin/          # Administrative & pending payout routes
│   │       ├── store/          # Vendor management routes
│   │       ├── auth.py         # Registration, login, session routes
│   │       ├── order.py        # Checkout & Stripe webhook handlers
│   │       └── product.py      # Product catalog routes
│   ├── schemas/                # Pydantic validation schemas
│   ├── seed_data/              # Database seeding utilities
│   ├── Dockerfile              # API container configuration
│   ├── main.py                 # FastAPI application entrypoint & middleware
│   └── pyproject.toml          # Python dependencies & tools
└── web/                        # Nuxt 3 Frontend Application
    ├── app/                    # Vue 3 pages, components, layouts, stores
    ├── tests/e2e/              # Playwright end-to-end test suite
    ├── nuxt.config.ts          # Nuxt framework configuration
    └── package.json            # Frontend npm dependencies
```

---

## 🚀 Getting Started

### Prerequisites
- [Docker Engine](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.13+](https://www.python.org/) (for local API development)
- [Node.js 20+](https://nodejs.org/) (for local web development)

### 1. Environment Setup

Create environment files for both backend and frontend.

**Backend Configuration (`api/.env`):**
```env
APP_NAME=16vMart
APP_URL=http://localhost:3000
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vmart_db
REDIS_HOST=redis
SECRET_KEY=your_super_secret_jwt_key
STRIPE_SECRET=sk_test_...
STRIPE_HOOK_SECRET=whsec_...
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**Frontend Configuration (`web/.env`):**
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

---

### 2. Running with Docker Compose (Recommended)

Start all services (FastAPI, ARQ Worker, Redis) with a single command:

```bash
docker compose up --build
```

The services will be accessible at:
- **FastAPI API**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Redis Server**: `localhost:6379`

---

### 3. Local Development (Without Docker)

#### Backend (FastAPI):
```bash
cd api

# Install dependencies (using uv or pip)
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial categories and sample products (optional)
python seed_categories.py
python seed_products.py

# Start FastAPI server
uvicorn main:app --reload --port 8000

# In a separate terminal, start the ARQ worker:
arq bg_task.config.WorkerSettings
```

#### Frontend (Nuxt 3):
```bash
cd web

# Install npm packages
npm install

# Start development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Testing & Quality Assurance

### Backend Unit & Integration Tests (Pytest)
```bash
cd api
pytest
```

### Frontend End-to-End Tests (Playwright)
```bash
cd web
npm run test:e2e
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
