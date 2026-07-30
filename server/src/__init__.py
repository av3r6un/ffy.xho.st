from aiohttp.web import Application, run_app
from dotenv import load_dotenv
from .utils import middlewares
from .config import Settings
from .services import Youtube
import logging
import os


load_dotenv('server/.env')

settings = Settings()
youtube = Youtube(settings)

def create_app():
  from .routes import routes
  from .routes.proxy import setup_proxy
  app = Application(middlewares=middlewares)
  setup_proxy(app)
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] WEB: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
  )
  
  app.add_routes(routes)
  if os.getenv('DEBUG', False):
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] WEB: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logging.getLogger().addHandler(console)
  
  return app

def start():
  run_app(
    create_app(),
    host="0.0.0.0",
    port=int(os.getenv('APP_PORT', '8090')),
    access_log_format='%{X-Forwarded-For}i %s - "%r" (%b | %D) %{User-Agent}i',
  )
