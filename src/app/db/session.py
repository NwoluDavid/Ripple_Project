from motor import motor_asyncio, core
from odmantic import AIOEngine
from pymongo.driver_info import DriverInfo
from app.config import settings

DRIVER_INFO = DriverInfo(
    name="full-stack-fastapi-mongodb", version=f"{settings.MONGO_DRIVER_VERSION}"
)


class _MongoClientSingleton:
    mongo_client: motor_asyncio.AsyncIOMotorClient | None
    engine: AIOEngine

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(_MongoClientSingleton, cls).__new__(cls)
            cls.instance.mongo_client = motor_asyncio.AsyncIOMotorClient(
                f"{settings.MONGO_DATABASE_URI}",

                # f"{settings.MONGO_DATABASE_URI}://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:27017/?authSource=admin&directConnection=true",  # noqa
                driver=DRIVER_INFO,
            )
            cls.instance.engine = AIOEngine(
                client=cls.instance.mongo_client,
                database=settings.MONGO_DATABASE,  # noqa
            )
        return cls.instance


def MongoDatabase() -> core.AgnosticDatabase:
    return _MongoClientSingleton().mongo_client[settings.MONGO_DATABASE]


def get_engine() -> AIOEngine:
    return _MongoClientSingleton().engine


async def ping():
    await MongoDatabase().command("ping")


__all__ = ["MongoDatabase", "ping"]
