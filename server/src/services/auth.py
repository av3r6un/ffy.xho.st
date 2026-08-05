from src.models import User


class AuthService:
  
  @classmethod
  async def get_user(cls, session, uid) -> User | None:
    return await User.first(session, uid=uid)
