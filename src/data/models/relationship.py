from sqlalchemy import Column, Float, ForeignKey, String, UUID, func

from src.data.db import Base


class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4()
    )
    entity1_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    entity2_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    relationship_type = Column(String, nullable=False)
    strength = Column(Float)

    def __repr__(self):
        return f"<Relationship(id={self.id}, entity1_id={self.entity1_id}, entity2_id={self.entity2_id})>"
