from odmantic import Field
from app.db.base_class import Base

class Featured(Base):
    project_id: str = Field(default=None, description="this is the id of a project from mongo db object id", max_length=24)