
from typing import Any, Dict, Optional, Union , List
from fastapi.exceptions import HTTPException
from pydantic import EmailStr
from motor.core import AgnosticDatabase
from bson import ObjectId
import pprint

from app.auth.security import get_password_hash, verify_password_hash
from app.db.base import CRUDBase
from app.user.models import User
from datetime import date

from app.user.schemas import(
    UserCreate,
    UserInDB, UserUpdate,
    UserUpdatas,
    UserData)

from app.auth.schemas import NewTOTP

import datetime
import json
import bson
from bson import json_util

# ODM, Schema, Schema
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(
        self, db: AgnosticDatabase, *, email: EmailStr
    ) -> User | None:  # noqa
        return await self.engine.find_one(User, User.email == email)

    async def create(self, db: AgnosticDatabase, *, obj_in: UserCreate) -> User:  # noqa
        # TODO: Figure out what happens when you have a unique key like 'email'
        user = {
            **obj_in.model_dump(),
            "email": obj_in.email,
            "hashed_password": get_password_hash(obj_in.password)
            if obj_in.password is not None
            else None,
            "full_name": obj_in.full_name,
            "is_superuser": obj_in.is_superuser,
        }

        return await self.engine.save(User(**user))

    async def update(
        self,
        db: AgnosticDatabase,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("email") and db_obj.email != update_data["email"]:
            update_data["email_validated"] = False
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AgnosticDatabase, *, email: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password_hash(
            plain_password=password, hashed_password=user.hashed_password
        ):
            return None
        return user

    async def validate_email(self, db: AgnosticDatabase, *, db_obj: User) -> User:
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        obj_in.email_validated = True
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def activate_totp(
        self, db: AgnosticDatabase, *, db_obj: User, totp_in: NewTOTP
    ) -> User:
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        obj_in = obj_in.model_dump(exclude_unset=True)
        obj_in["totp_secret"] = totp_in.secret
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def deactivate_totp(self, db: AgnosticDatabase, *, db_obj: User) -> User:
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        obj_in = obj_in.model_dump(exclude_unset=True)
        obj_in["totp_secret"] = None
        obj_in["totp_counter"] = None
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def update_totp_counter(
        self, db: AgnosticDatabase, *, db_obj: User, new_counter: int
    ) -> User:
        obj_in = UserUpdate(**UserInDB.model_validate(db_obj).model_dump())
        obj_in = obj_in.model_dump(exclude_unset=True)
        obj_in["totp_counter"] = new_counter
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    async def toggle_user_state(
        self, db: AgnosticDatabase, *, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User | None:
        db_obj = await self.get_by_email(db, email=obj_in.email)
        if not db_obj:
            return None
        return await self.update(db=db, db_obj=db_obj, obj_in=obj_in)

    @staticmethod
    def has_password(user: User) -> bool:
        return user.hashed_password is not None

    @staticmethod
    def is_active(user: User) -> bool:
        return user.is_active

    @staticmethod
    def is_superuser(user: User) -> bool:
        return user.is_superuser

    @staticmethod
    def is_email_validated(user: User) -> bool:
        return user.email_validated
    
    async def update_user_detail(self, db: AgnosticDatabase , user:User , update):
        
        """The functions updates the user detail in the db
        using the usermodel"""
        
        user_collection =db.user
        
        document_to_update ={"_id":ObjectId(user.id)}
        
        update ={"$set":{
            "phone": update.phone,
            "date_of_birth": update.date_of_birth,
            "address": update.address,
            "full_name":update.full_name,
        }}
        
        #document before
        user=await user_collection.find_one(document_to_update)
        
        #updating user
        updated_user = await user_collection.update_one(document_to_update, update)
        # pprint.pprint(updated_user)
        print(updated_user.matched_count)
        
        #geting updated user in db
        user_update = await user_collection.find_one(document_to_update)
        user_update =UserData(**user_update)

        return user_update
    
    
    
user = CRUDUser(User)
