from datetime import datetime as dt

from sqlalchemy import select

from src.models import PushSubscription


class PushSubscriptionService:
  @classmethod
  async def active_for_user(cls, session, user_uid: str):
    result = await session.execute(
      select(PushSubscription).where(
        PushSubscription.user_uid == user_uid,
        PushSubscription.revoked_at.is_(None),
      ),
    )
    return result.scalars().all()

  @classmethod
  async def get_active(cls, session, user_uid: str, endpoint: str):
    result = await session.execute(
      select(PushSubscription).where(
        PushSubscription.user_uid == user_uid,
        PushSubscription.endpoint == endpoint,
        PushSubscription.revoked_at.is_(None),
      ),
    )
    return result.scalar_one_or_none()

  @classmethod
  async def upsert(
    cls,
    session,
    user_uid: str,
    endpoint: str,
    p256dh: str,
    auth: str,
    user_agent: str | None = None,
  ) -> PushSubscription:
    result = await session.execute(
      select(PushSubscription).where(PushSubscription.endpoint == endpoint),
    )
    subscription = result.scalar_one_or_none()

    if subscription is None:
      subscription = PushSubscription(
        user_uid=user_uid,
        endpoint=endpoint,
        p256dh=p256dh,
        auth=auth,
        user_agent=user_agent,
      )
      session.add(subscription)
    else:
      subscription.user_uid = user_uid
      subscription.p256dh = p256dh
      subscription.auth = auth
      subscription.user_agent = user_agent
      subscription.revoked_at = None

    await session.flush()
    return subscription

  @classmethod
  async def revoke(cls, session, user_uid: str, endpoint: str) -> bool:
    subscription = await cls.get_active(session, user_uid, endpoint)
    if subscription is None:
      return False

    subscription.revoked_at = dt.now()
    await session.flush()
    return True
