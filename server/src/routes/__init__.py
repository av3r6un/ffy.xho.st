from .main import main
from .proxy import proxy

routes = (
  *proxy,
  *main,
)
