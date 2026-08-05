import asyncio
import logging
from datetime import datetime as dt, timedelta as delta

from aiohttp import web
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.models import VideoSession
from src.models.base import Status


class StartupService:
  LAGGED_AFTER = delta(minutes=15)
  DELETE_AFTER = delta(days=1)

  @classmethod
  async def context(cls, app: web.Application):
    task = asyncio.create_task(cls.run(app['db_sessionmaker']))
    yield
    if not task.done():
      task.cancel()
    await asyncio.gather(task, return_exceptions=True)

  @classmethod
  def setup(cls, app: web.Application) -> None:
    app.cleanup_ctx.append(cls.context)

  @classmethod
  async def run(
    cls,
    session_factory: async_sessionmaker[AsyncSession],
  ) -> None:
    async with session_factory() as session:
      try:
        now = dt.now()
        lagged = await session.execute(
          update(VideoSession)
          .where(
            VideoSession.status == Status.PENDING,
            VideoSession.created_at < now - cls.LAGGED_AFTER,
          )
          .values(
            status=Status.FAILED,
            error_message='Preparation interrupted.',
          ),
        )
        expired = await session.execute(
          delete(VideoSession)
          .where(VideoSession.expires_at < now - cls.DELETE_AFTER),
        )
        await session.commit()
        logging.info(
          'Startup cleanup marked %s sessions failed and deleted %s sessions',
          lagged.rowcount,
          expired.rowcount,
        )
      except asyncio.CancelledError:
        await session.rollback()
        raise
      except Exception:
        await session.rollback()
        logging.exception('Startup cleanup failed')
