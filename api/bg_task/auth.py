from settings import setting
from models.db import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User, Session as AuthSession
from schemas.user import UserShema
from user_agents import parse
import httpx
from fastapi_mail import MessageSchema, MessageType, FastMail
from libs.mail_config import conf
from libs.logger import logger

async def update_session(ctx, session_id, user_agent_string):

    db: AsyncSession = AsyncSessionLocal()
    try:
        stmt = select(AuthSession).where(AuthSession.id == session_id)
        session = await db.scalar(stmt)
        if not session:
            return False
        
        user_agent = parse(user_agent_string)
        device_info = str(user_agent).replace("/", "")
        session.device = device_info

        ip = session.ip_address
        client = httpx.AsyncClient()
        res = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,zip")
        r = res.json()
        if r['status'] == "success":
            location = f"{r['city']}, {r['country']}. {r['zip']}"
            session.location = location
        await client.aclose()

        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.exception(f"Error updating session {session_id}: {e}")
        raise
    finally:
        await db.close()

async def send_welcome_email(ctx, email, fullname):
    try:
        message = MessageSchema(
            subject="Welcome to 16vmart - Your Trusted Marketplace",
            recipients=[email],
            template_body={"fullname": fullname, "url": f"https://{setting.APP_URL}/products"},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="welcome.html")
        logger.info(f"Welcome email sent successfully to {email}")
        return True
    except Exception as e:
        logger.exception(f"Error sending welcome email to {email}: {e}")
        raise