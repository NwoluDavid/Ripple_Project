from motor.core import AgnosticDatabase

from app.config import settings
from app.user import crud, schemas


async def init_db(db: AgnosticDatabase) -> None:
    user_in_db = await crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)  # noqa
    if not user_in_db:
        # Create user auth
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name=settings.FIRST_SUPERUSER,
        )
        user = await crud.user.create(db, obj_in=user_in)  # noqa: F841
