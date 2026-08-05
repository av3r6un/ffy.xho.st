import asyncio
import logging
from datetime import datetime as dt, timedelta as delta

from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.exceptions import JSRError
from src.models import Metadata, VideoSession
from src.models.base import Status

from .metadata import MetadataService
from .playback import PlaybackTokenService


PREPARATION_TASKS = web.AppKey('video_preparation_tasks', set)


class SessionService:
  TTL = 6

  @staticmethod
  async def task_context(app: web.Application):
    app[PREPARATION_TASKS] = set()
    yield
    tasks = app[PREPARATION_TASKS]
    for task in tasks:
      task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

  @classmethod
  def setup(cls, app: web.Application) -> None:
    app.cleanup_ctx.append(cls.task_context)

  @classmethod
  async def create_pending(
    cls,
    session: AsyncSession,
    user_uid: str,
    video_id: str,
  ) -> VideoSession:
    uid = await VideoSession.create_uid(session)
    expires_at = dt.now() + delta(hours=cls.TTL)
    video_session = VideoSession(uid, user_uid, video_id, expires_at)
    await video_session.save(session)
    return video_session

  @classmethod
  async def create_ready(
    cls,
    session: AsyncSession,
    user_uid: str,
    video_id: str,
    metadata_uid: str,
  ) -> VideoSession:
    uid = await VideoSession.create_uid(session)
    expires_at = dt.now() + delta(hours=cls.TTL)
    video_session = VideoSession(uid, user_uid, video_id, expires_at, metadata_uid)
    await video_session.save(session)
    return video_session

  @staticmethod
  async def mark(
    session: AsyncSession,
    uid: str,
    status: Status | str,
    message: str | None = None,
  ) -> VideoSession:
    video_session = await VideoSession.first(session, uid=uid)
    if not video_session:
      raise JSRError('not_found', message=f'Session[{uid}] not found!')
    video_session.status = status
    video_session.error_message = message
    return video_session

  @classmethod
  async def mark_ready(
    cls,
    session: AsyncSession,
    uid: str,
    metadata_uid: str,
  ) -> VideoSession:
    video_session = await cls.mark(session, uid, Status.READY)
    video_session.metadata_uid = metadata_uid
    return video_session

  @classmethod
  async def mark_failed(
    cls,
    session: AsyncSession,
    uid: str,
    message: str,
  ) -> VideoSession:
    return await cls.mark(session, uid, Status.FAILED, message)

  @classmethod
  async def get_for_user(
    cls,
    session: AsyncSession,
    uid: str,
    user_uid: str,
  ) -> VideoSession:
    video_session = await VideoSession.first(
      session,
      uid=uid,
      user_uid=user_uid,
      expires_at__gt=dt.now(),
    )
    if not video_session:
      raise JSRError('not_found', message=f'Session[{uid}] is unavailable!')
    return video_session

  @classmethod
  async def get_payload(
    cls,
    session: AsyncSession,
    uid: str,
    user_uid: str,
  ) -> dict:
    video_session = await cls.get_for_user(session, uid, user_uid)
    payload = video_session.json
    if video_session.status is Status.FAILED:
      payload['error_message'] = video_session.error_message
      return payload
    if video_session.status is Status.PENDING:
      return payload

    metadata = await Metadata.first(session, uid=video_session.metadata_uid)
    if not metadata:
      raise JSRError('not_found', message='Prepared metadata is unavailable.')
    payload['metadata'] = metadata.raw
    payload['playback_token'] = PlaybackTokenService.issue(
      video_session.uid,
      video_session.video_id,
    )
    return payload

  @classmethod
  async def find_active_for_video(
    cls,
    session: AsyncSession,
    user_uid: str,
    video_id: str,
  ) -> VideoSession | None:
    return await VideoSession.first(
      session,
      user_uid=user_uid,
      video_id=video_id,
      expires_at__gt=dt.now(),
      order_by='-created_at',
    )

  @classmethod
  async def prepare(
    cls,
    app: web.Application,
    session: AsyncSession,
    user_uid: str,
    video_id: str | None,
  ) -> dict:
    if not video_id:
      raise JSRError('invalid_payload', message='A valid YouTube URL is required.')

    active = await cls.find_active_for_video(session, user_uid, video_id)
    if active and active.status in {Status.PENDING, Status.READY}:
      return active.json

    metadata = await MetadataService.get_fresh(session, video_id)
    if metadata:
      ready = await cls.create_ready(session, user_uid, video_id, metadata.uid)
      return ready.json

    pending = await cls.create_pending(session, user_uid, video_id)
    await session.commit()
    cls._schedule_preparation(app, pending.uid, video_id)
    return pending.json

  @classmethod
  def _schedule_preparation(
    cls,
    app: web.Application,
    session_uid: str,
    video_id: str,
  ) -> None:
    session_factory = app['db_sessionmaker']
    task = asyncio.create_task(
      cls._prepare_metadata(session_factory, session_uid, video_id),
    )
    tasks = app[PREPARATION_TASKS]
    tasks.add(task)
    task.add_done_callback(tasks.discard)

  @classmethod
  async def _prepare_metadata(
    cls,
    session_factory: async_sessionmaker[AsyncSession],
    session_uid: str,
    video_id: str,
  ) -> None:
    async with session_factory() as session:
      try:
        from src import youtube

        media = await asyncio.to_thread(youtube.find, video_id)
        api_response = dict(**media.json, formats=media.formats.json)
        metadata_uid = await MetadataService.upsert(session, api_response)
        await cls.mark_ready(session, session_uid, metadata_uid)
        await session.commit()
      except asyncio.CancelledError:
        await session.rollback()
        raise
      except Exception:
        await session.rollback()
        logging.exception('Unable to prepare video %s', video_id)
        await cls.mark_failed(session, session_uid, 'Unable to prepare video.')
        await session.commit()
