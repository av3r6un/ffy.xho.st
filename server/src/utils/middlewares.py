from aiohttp.web import json_response, middleware, StreamResponse, HTTPException, Request
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from aiohttp.web_exceptions import HTTPNotFound
from jwt import ExpiredSignatureError, InvalidTokenError
from src.services import AuthService
from src.exceptions import JSRError
from .jwt import verify_access_token
from datetime import datetime as dt
import inspect
import logging


@middleware
async def db_middleware(req: Request, handler, *args, **kwargs):
  session_factory: async_sessionmaker[AsyncSession] = req.app['db_sessionmaker']
  async with session_factory() as session:
    try:
      req['session'] = session
      response = await handler(req, *args, **kwargs)
      if getattr(response, 'status', 200) >= 400:
        await session.rollback()
      else:
        await session.commit()
      return response
    except HTTPNotFound:
      await session.rollback()
      return json_response(dict(status='error', message='Requested page is not found'), status=404)
    except Exception:
      await session.rollback()
      raise


@middleware
async def params_middleware(request, handler):
  params: dict[str, str | list[str]] = {}

  for key in dict.fromkeys(request.query.keys()):
    values = request.query.getall(key)
    params[key] = values if len(values) > 1 else values[0]

  request['params'] = params
  return await handler(request)


@middleware
async def response_middleware(req: Request, handler, *args, **kwargs):
  try:
    call_kwargs = {}
    try:
      sig = inspect.signature(handler)
      params = sig.parameters
      if 'session' in params or any(p.kind == p.VAR_KEYWORD for p in params.values()):
        call_kwargs['session'] = req.get('session')
    except (TypeError, ValueError):
      pass
  
    result = await handler(req, *args, **call_kwargs, **kwargs)
    if isinstance(result, StreamResponse):
      return result
    if isinstance(result, tuple):
      body, message = result
      return json_response(dict(status='success', body=body, message=message))
    return json_response(dict(status='success', body=result))
  except JSRError as e:
    return json_response(**e.json)
  except HTTPException:
    raise
  except Exception as ex:
    logging.exception('Unhandled request error')
    return json_response(dict(status='error', message=str(ex)), status=500)


@middleware
async def jwt_middleware(req: Request, handler, *args, **kwargs):
  from src.models import User
  from src import settings

  route_error = getattr(req.match_info, 'http_exception', None)
  if isinstance(route_error, HTTPNotFound):
    raise route_error
  
  session = req['session']
  if req.path.startswith(tuple(settings.NOT_SECURED_PATHS)):
    return await handler(req, session=session)
  
  auth_header = req.headers.get('Authorization')
  if not auth_header or not auth_header.startswith('Bearer '):
    raise JSRError('missing_auth_header')
  
  token = auth_header.split(' ')[1]
  try:
    payload = verify_access_token(token)
    user = await AuthService.get_user(session, payload['sub'])
    if not user:
      user = User(payload['sub'])
      await user.save(session)
    user.last_seen_at = dt.now()
    req['current_user'] = user
    
  except ExpiredSignatureError: raise JSRError('token_expired')
  except InvalidTokenError: raise JSRError('invalid_token')
  
  return await handler(req, session=session)

middlewares = [db_middleware, params_middleware, response_middleware, jwt_middleware]
