import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AssetStatus(str, enum.Enum):
    ORDERED = "ordered"
    AVAILABLE = "available"
    ACTIVE = "active"
    SPARE = "spare"
    IN_REPAIR = "in_repair"
    DISPOSED = "disposed"
    LOST_STOLEN = "lost_stolen"


class AssetType(str, enum.Enum):
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    MONITOR = "monitor"
    DOCKING_STATION = "docking_station"
    PERIPHERAL = "peripheral"
    NETWORKING = "networking"
    OTHER = "other"


class DisposalMethod(str, enum.Enum):
    SOLD = "sold"
    RECYCLED = "recycled"
    DONATED = "donated"
    SCRAPPED = "scrapped"
    RETURNED = "returned"


class Office(str, enum.Enum):
    CHICAGO = "Chicago"
    MORGAN_HILL = "Morgan_Hill"
    HARTFORD = "Hartford"
    RALEIGH_DURHAM = "Raleigh-Durham"
    IRVINE = "Irvine"
    HILLSBORO = "Hillsboro"
    ALLIANCE = "Alliance"
    CLINTON = "Clinton"
    TRUMBULL = "Trumbull"


class DeviceCatalog(Base):
    __tablename__ = "device_catalog"

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType))
    current_price: Mapped[float | None] = mapped_column(Numeric(10, 2))
    price_updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    assets: Mapped[list["Asset"]] = relationship(back_populates="device")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("device_catalog.id"))
    description: Mapped[str | None] = mapped_column(Text)

    # Financial
    purchase_date: Mapped[date | None] = mapped_column(Date)
    purchase_cost: Mapped[float | None] = mapped_column(Numeric(10, 2))
    po_number: Mapped[str | None] = mapped_column(String(50))
    vendor: Mapped[str | None] = mapped_column(String(200))

    # Assignment
    assigned_user: Mapped[str | None] = mapped_column(String(200))
    department: Mapped[str | None] = mapped_column(String(100))
    office: Mapped[Office | None] = mapped_column(Enum(Office))

    # Status
    status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    warranty_expiration: Mapped[date | None] = mapped_column(Date)

    # Disposal
    disposal_date: Mapped[date | None] = mapped_column(Date)
    disposal_method: Mapped[DisposalMethod | None] = mapped_column(Enum(DisposalMethod))
    disposal_value: Mapped[float | None] = mapped_column(Numeric(10, 2))
    disposal_notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    device: Mapped[DeviceCatalog | None] = relationship(back_populates="assets")
