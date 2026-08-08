from .main import main
from .proxy import proxy
from .sessions import sessions
from .subscriptions import subscriptions
from .shortcuts import shortcuts

routes = (
  *proxy,
  *sessions,
  *subscriptions,
  *shortcuts,
  *main,
)
