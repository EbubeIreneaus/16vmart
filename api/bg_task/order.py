from collections import defaultdict

from models.db import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from models.user import User, Session as AuthSession
from models.shopping import Order, OrderProduct, VendorOrder
from schemas.user import UserShema
from schemas.shopping import ORDER_STATUS
from user_agents import parse
import httpx
from fastapi_mail import MessageSchema, MessageType, FastMail
from libs.mail_config import conf
from sqlalchemy.orm import selectinload

async def update_order(ctx, status: ORDER_STATUS, order_number: str):
    from .config import get_arq_pool

    async with AsyncSessionLocal() as db:
        try:
            order = await db.scalar(
                select(Order)
                .options(
                    selectinload(Order.user),
                    selectinload(Order.items).options(
                        selectinload(OrderProduct.product)
                    ),
                    selectinload(Order.vendors)
                )
                .where(Order.order_number == order_number)
            )
            if not order:
                print("No order")
                return {"success": False}

            now = datetime.now(timezone.utc)

            order.status = ORDER_STATUS.PROCESSING
            order.paid = True
            order.paid_at = now

            # send payment recieve email here
            arq = await get_arq_pool()
            if status == ORDER_STATUS.PROCESSING and len(order.vendors) < 1:
                await arq.enqueue_job("create_vendor_orders", order_number)
            await db.commit()
            return {"success": True}
        except Exception as e:
            print(f"Failed to update order for {order_number}: {e}")
            await db.rollback()
            return {"success": "failed"}
        finally:
            await db.close()


async def create_vendor_orders(ctx, order_number: str):
    async with AsyncSessionLocal() as db:
        try:
            order = await db.scalar(
                select(Order)
                .options(
                    selectinload(Order.items).options(
                        selectinload(OrderProduct.product)
                    ),
                )
                .where(Order.order_number == order_number)
            )
            if not order:
                return {"success": False, "reason": "order_not_found"}

            existing = await db.scalar(
                select(VendorOrder).where(VendorOrder.order_id == order.id)
            )
            if existing:
                return {"success": True, "reason": "already_created"}  # idempotent no-op

            vendor_totals = defaultdict(list)
            for item in order.items:
                vendor_totals[item.product.store_id].append(item.unit_price * item.quantity)

            vendor_orders = [
                VendorOrder(
                    store_id=store_id,
                    order_id=order.id,
                    subtotal=sum(prices),
                    status="unpaid",
                )
                for store_id, prices in vendor_totals.items()
            ]

            db.add_all(vendor_orders)
            await db.commit()
            return {"success": True}

        except Exception as e:
            await db.rollback()
            print(f"Failed creating vendor orders for {order_number}: {e}")
            return {"success": False, "reason": "internal_error"}
        
