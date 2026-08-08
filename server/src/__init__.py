from aiohttp.web import Application, run_app
from dotenv import load_dotenv
from .utils import middlewares
from .config import Settings
from .services import Youtube
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys


settings = Settings()

load_dotenv((settings.ROOT / '..' / '.env').resolve())

youtube = Youtube(settings)


def configure_logging() -> Path:
  project_root = Path(__file__).resolve().parent.parent
  configured_path = Path(os.getenv('LOG_FILE', 'logs/all.log'))
  log_path = configured_path if configured_path.is_absolute() else project_root / configured_path
  log_path.parent.mkdir(parents=True, exist_ok=True)

  level_name = os.getenv('LOG_LEVEL', 'INFO').upper()
  level = getattr(logging, level_name, logging.INFO)
  formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    '%Y-%m-%d %H:%M:%S',
  )

  file_handler = RotatingFileHandler(
    log_path,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8',
  )
  file_handler.setFormatter(formatter)
  handlers = [file_handler]

  debug_enabled = os.getenv('DEBUG', '').strip().lower() in {'1', 'true', 'yes', 'on'}
  if debug_enabled:
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    handlers.append(console)

  logging.basicConfig(
    level=level,
    handlers=handlers,
    force=True,
  )
  logging.getLogger(__name__).info('Logging configured; file=%s', log_path)
  return log_path

async def db_ctx(app: Application):
  from .utils.engine import session_maker, dispose
  app['db_sessionmaker'] = session_maker
  yield
  await dispose()

def create_app():
  from .routes import routes
  from .services import ProxyService, SessionService, StartupService
  configure_logging()
  settings.load_settings()
  app = Application(middlewares=middlewares)
  app.cleanup_ctx.append(db_ctx)
  ProxyService.setup(app)
  SessionService.setup(app)
  StartupService.setup(app)
  app.add_routes(routes)
  return app

def start():
  run_app(
    create_app(),
    host="0.0.0.0",
    port=int(os.getenv('APP_PORT', '8090')),
    access_log_format='%{X-Forwarded-For}i %s - "%r" (%b | %D) %{User-Agent}i',
  )
