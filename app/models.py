import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False, index=True)
    function_name = Column(String, nullable=False)
    starter_code = Column(Text, nullable=False)
    test_code = Column(Text, nullable=False)

    @property
    def module_path(self) -> str:
        """Generate module path from category and function_name."""
        category_module = self.category.replace("-", "_")
        return f"{category_module}.{self.function_name}"
