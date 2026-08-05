from .main import main
from .proxy import proxy
from .sessions import sessions

routes = (
  *proxy,
  *sessions,
  *main,
)
