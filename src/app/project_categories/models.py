from odmantic import ObjectId, Field
from app.db.base_class import Base

class ProjectCategories(Base):
    name: str = Field(default=None, description="this is the project category")
