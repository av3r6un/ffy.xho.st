from aiohttp.web import json_response, middleware, StreamResponse, HTTPException, Request
from aiohttp.web_exceptions import HTTPNotFound
import inspect
import logging

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
  except HTTPException:
    raise
  except Exception as ex:
    logging.exception('Unhandled request error')
    return json_response(dict(status='error', message=str(ex)), status=500)


middlewares = [response_middleware]
