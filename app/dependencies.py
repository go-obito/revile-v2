from fastapi import Depends

from app.db import get_db

DbSession = Depends(get_db)
