# 🛒 16vMart — Enterprise Multi-Vendor E-Commerce Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.15+-00DC82.svg?style=flat&logo=Nuxt.js&logoColor=white)](https://nuxt.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![Stripe](https://img.shields.io/badge/Stripe-SDK-008CDD.svg?style=flat&logo=stripe&logoColor=white)](https://stripe.com/)

**16vMart** is a production-grade multi-vendor e-commerce platform designed with scalable system architecture, robust security, distributed task execution, and asynchronous payment processing.

Built to handle complex marketplace dynamics, 16vMart enables customers to register, browse independent vendor stores, manage shopping carts, and place orders via a **unified single-checkout payment system**. Background processing handles order aggregation, sub-order splitting per seller, and vendor payout tracking through a dedicated management dashboard.

---

## 🏗 System Design & Engineering Highlights

This project demonstrates production-ready engineering patterns focused on scalability, idempotency, caching, rate limiting, and clean separation of concerns.

### 1. 💳 Unified Single-Payment & Vendor Payout Architecture
- **Multi-Vendor Single Checkout**: Customers purchase products from multiple independent vendors in a single transaction.
- **Asynchronous Payment Integration**: Integrates asynchronous payment processing with metadata-driven order tracking and strict idempotency keys to prevent duplicate charges.
- **Asynchronous Webhook Processing**: Listens for payment webhook events to verify and process transactions out of the synchronous HTTP request-response cycle.
- **Vendor Payout Management**: Automatically decomposes unified customer checkout orders into itemized vendor sub-orders, giving administrators and store owners real-time visibility into order fulfillments and pending payouts.

### 2. ⚡ Asynchronous Background Processing
- **Distributed Job Queue**: Utilizes an asynchronous Redis-backed background worker running as an isolated service to handle heavy background tasks without blocking HTTP API endpoints.
- **Idempotent Order Splitting**: Background workers calculate sub-totals per store, allocate line items, and generate vendor order breakdowns safely and asynchronously.
- **Async Notification Pipeline**: Dispatches transactional customer and vendor notifications asynchronously based on queue events.

### 3. 🚀 High-Performance Caching & Session Management
- **Session Caching**: Eliminates database query overhead on authenticated requests by caching serialized user session state in Redis with automatic TTL expiry.
- **Store & Product Caching**: Caches store metadata and catalog configurations in Redis to accelerate store routing and page rendering.
- **Persistent Shopping Carts**: Stores active user shopping carts in Redis for high-speed read/write operations during customer browsing.

### 4. 🗄️ Database Architecture & Query Optimization
- **Asynchronous ORM**: Powered by asynchronous database access for non-blocking database queries.
- **Strategic Database Indexing**: Optimized database indexes on frequently queried fields, including product and store slugs, lookup identifiers, order numbers, and seller references.
- **N+1 Query Elimination**: Implements optimized eager-loading strategies across multi-tiered object graphs (Users, Orders, Items, Products, Categories, and Media).
- **Data Integrity**: Enforces database-level constraints including composite unique indexes, foreign key relationships, and cascading rules.

### 5. 🔐 Authentication, Session Security & Access Control
- **Session-Based Authentication**: Secure authentication backed by server-tracked active sessions storing IP address, location, device type, browser user-agent info, and token revocation mechanisms.
- **Modern Password Hashing**: Enforces high-security password hashing using Argon2.
- **Role-Based Access Control (RBAC)**: Tiered authorization guards protecting endpoint access by user privilege level:
  - **Customer**: Standard authenticated shopping and order access.
  - **Store Owner**: Store dashboard, product catalog, and order fulfillment permissions.
  - **Admin / Superadmin**: Platform-wide catalog management, store moderation, and payout oversight.

### 6. 🛡️ API Protection & Resilience
- **Rate Limiting Policy**: Rate limiting protects critical endpoints (such as checkout and authentication) against abuse and brute-force attempts.
- **Graceful Error Handling**: Unified exception handling for rate limits, payment gateway errors, and domain validation failures.

### 7. 🐳 Containerized Architecture
- **Multi-Service Orchestration**: Fully containerized environment comprising separate services for the API backend, asynchronous background worker, and Redis caching/queuing service.
- **Isolated Environments**: Standardized container builds with volume isolation for seamless development and deployment.

---

## 📐 System Architecture

```mermaid
flowchart TD
    subgraph Client Layer
        Web[Nuxt 3 Frontend / Vue 3]
    end

    subgraph API Gateway & Service Layer
        API[FastAPI Service - Async ASGI]
        Limiter[Rate Limiter]
        RBAC[RBAC & Auth Middleware]
    end

    subgraph Storage & Infrastructure Layer
        Redis[(Redis 7 - Session / Cache / Queue)]
        DB[(PostgreSQL Database)]
    end

    subgraph Background Processing Layer
        Worker[Background Job Worker]
        Mail[Mail Notification Service]
    end

    subgraph External Services
        Stripe[Stripe Payment Gateway]
        Cloudinary[Cloudinary Media CDN]
    end

    Web -->|HTTP / REST| API
    API --> Limiter
    API --> RBAC
    API -->|Session & Cart Cache| Redis
    API -->|Async Queries| DB
    API -->|Media Uploads| Cloudinary
    API -->|Create Payment Session| Stripe
    
    Stripe -->|Webhooks| API
    API -->|Enqueue Tasks| Redis
    Redis -->|Dequeue Tasks| Worker
    Worker -->|Split Orders & Payouts| DB
    Worker -->|Send Notifications| Mail
```

---

## 🔄 Business Workflows

### 🛍️ Customer Journey
1. **Account Registration**: User registers and authenticates securely via session-backed credentials.
2. **Catalog Browsing**: Search and filter products across categories, stores, and custom attributes.
3. **Unified Cart**: Add items from multiple independent stores into a single persistent shopping cart.
4. **Single Checkout**: Complete purchase via a unified payment checkout session.
5. **Order Processing**: Payment webhooks confirm transactions, update order status, and trigger background vendor order generation.

### 🏪 Store Owner Journey
1. **Store Setup**: Registered customers apply to open a custom seller store.
2. **Catalog Management**: Add and manage products with rich text descriptions, custom attributes, and CDN media assets.
3. **Store Fulfillment**: Track store sales, process itemized sub-orders, and monitor payment payout status.

### 👑 Platform Admin Journey
1. **Platform Overview**: Monitor platform metrics, global listings, and active stores.
2. **Store & Product Moderation**: Review, approve, or manage vendor store applications and listings.
3. **Payout Management**: Review aggregate vendor orders, inspect pending balances, and manage store payouts.

---

## 🧰 Tech Stack Reference

| Layer | Technologies & Tools |
| :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/), Python 3.13+, Uvicorn |
| **Frontend Framework** | [Nuxt 3](https://nuxt.com/), Vue 3, TypeScript, Pinia |
| **UI & Styling** | Nuxt UI, Tailwind CSS, VueUse, ECharts, Tiptap |
| **Database & ORM** | PostgreSQL, [SQLAlchemy 2.0 Async](https://www.sqlalchemy.org/), Asyncpg, Alembic |
| **Caching & In-Memory DB** | [Redis 7](https://redis.io/) |
| **Background Tasks** | ARQ Async Worker Queue |
| **Payment Gateway** | Stripe SDK & Webhook Processing |
| **Authentication** | PyJWT, Argon2, OAuth2 Scheme |
| **Rate Limiting** | SlowAPI |
| **Media Hosting** | Cloudinary |
| **DevOps & Containers** | Docker, Docker Compose |
| **Testing** | Pytest, Pytest-Asyncio, Playwright E2E |

---

## 📂 Project Structure

```
16vmart/
├── compose.yaml                # Multi-container Docker Compose configuration
├── api/                        # FastAPI Backend Application
│   ├── alembic/                # Database migration scripts
│   ├── bg_task/                # Background worker tasks & queue configuration
│   ├── email_templates/        # HTML transactional email templates
│   ├── libs/                   # Core security, caching, and rate limiting utilities
│   ├── models/                 # Database models (User, Store, Product, Order, etc.)
│   ├── routers/                # REST API endpoints (Auth, Catalog, Store, Admin, Orders)
│   ├── schemas/                # Pydantic data validation schemas
│   ├── seed_data/              # Database seeding scripts
│   ├── Dockerfile              # API container build setup
│   ├── main.py                 # Application entrypoint & middleware setup
│   └── pyproject.toml          # Python project specification & dependencies
└── web/                        # Nuxt 3 Frontend Application
    ├── app/                    # Vue components, pages, layouts, and store state
    ├── tests/e2e/              # End-to-end testing suite
    ├── nuxt.config.ts          # Framework configuration
    └── package.json            # Frontend dependencies & scripts
```

---

## 🚀 Getting Started

### Prerequisites
- [Docker Engine](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/)
- [Python 3.13+](https://www.python.org/) (for local API development)
- [Node.js 20+](https://nodejs.org/) (for local web development)

### 1. Environment Setup

Configure environment variables for backend and frontend services:

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

Start all services (API, Background Worker, Redis) with Docker Compose:

```bash
docker compose up --build
```

Access services at:
- **FastAPI API**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Redis Server**: `localhost:6379`

---

### 3. Local Development (Without Docker)

#### Backend (FastAPI):
```bash
cd api

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial database categories and sample products (optional)
python seed_categories.py
python seed_products.py

# Start FastAPI application
uvicorn main:app --reload --port 8000

# In a separate terminal, start the background worker:
arq bg_task.config.WorkerSettings
```

#### Frontend (Nuxt 3):
```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev
```
Navigate to `http://localhost:3000` in your browser.

---

## 🧪 Testing & Quality Assurance

### Backend Unit & Integration Tests
```bash
cd api
pytest
```

### Frontend End-to-End Tests
```bash
cd web
npm run test:e2e
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
