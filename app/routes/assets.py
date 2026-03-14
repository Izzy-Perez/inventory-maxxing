from datetime import date

from fastapi import APIRouter, Depends, Form, Query, Request
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Asset, AssetStatus, AssetType, DisposalMethod, Location
from app.templating import templates

router = APIRouter(prefix="/assets")


@router.get("/")
async def list_assets(
    request: Request,
    q: str = Query("", alias="q"),
    status: str = Query("", alias="status"),
    location_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Asset).options(selectinload(Asset.location))

    if q:
        query = query.where(
            or_(
                Asset.asset_tag.ilike(f"%{q}%"),
                Asset.serial_number.ilike(f"%{q}%"),
                Asset.assigned_user.ilike(f"%{q}%"),
                Asset.make.ilike(f"%{q}%"),
                Asset.model.ilike(f"%{q}%"),
            )
        )
    if status:
        query = query.where(Asset.status == status)
    if location_id:
        query = query.where(Asset.location_id == location_id)

    query = query.order_by(Asset.asset_tag)
    result = await db.execute(query)
    assets = result.scalars().all()

    locations = (await db.execute(select(Location).order_by(Location.name))).scalars().all()

    ctx = {
        "assets": assets,
        "locations": locations,
        "statuses": AssetStatus,
        "q": q,
        "current_status": status,
        "current_location_id": location_id,
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(request, "assets/_table.html", ctx)

    return templates.TemplateResponse(request, "assets/list.html", ctx)


@router.get("/new")
async def new_asset_form(request: Request, db: AsyncSession = Depends(get_db)):
    locations = (await db.execute(select(Location).order_by(Location.name))).scalars().all()
    return templates.TemplateResponse(
        request,
        "assets/form.html",
        {
            "asset": None,
            "locations": locations,
            "asset_types": AssetType,
            "statuses": AssetStatus,
            "disposal_methods": DisposalMethod,
        },
    )


@router.post("/new")
async def create_asset(
    request: Request,
    asset_tag: str = Form(...),
    asset_type: AssetType = Form(...),
    serial_number: str = Form(""),
    make: str = Form(""),
    model: str = Form(""),
    description: str = Form(""),
    purchase_date: date | None = Form(None),
    purchase_cost: float | None = Form(None),
    po_number: str = Form(""),
    vendor: str = Form(""),
    assigned_user: str = Form(""),
    department: str = Form(""),
    location_id: int | None = Form(None),
    status: AssetStatus = Form(AssetStatus.ACTIVE),
    warranty_expiration: date | None = Form(None),
    disposal_date: date | None = Form(None),
    disposal_method: DisposalMethod | None = Form(None),
    disposal_value: float | None = Form(None),
    disposal_notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    asset = Asset(
        asset_tag=asset_tag,
        asset_type=asset_type,
        serial_number=serial_number or None,
        make=make or None,
        model=model or None,
        description=description or None,
        purchase_date=purchase_date,
        purchase_cost=purchase_cost,
        po_number=po_number or None,
        vendor=vendor or None,
        assigned_user=assigned_user or None,
        department=department or None,
        location_id=location_id,
        status=status,
        warranty_expiration=warranty_expiration,
        disposal_date=disposal_date,
        disposal_method=disposal_method,
        disposal_value=disposal_value,
        disposal_notes=disposal_notes or None,
    )
    db.add(asset)
    await db.commit()

    return templates.TemplateResponse(
        request,
        "assets/_saved.html",
        {"asset": asset},
        headers={"HX-Push-Url": f"/assets/{asset.id}"},
    )


@router.get("/{asset_id}")
async def detail_asset(request: Request, asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id, options=[selectinload(Asset.location)])
    return templates.TemplateResponse(request, "assets/detail.html", {"asset": asset})


@router.get("/{asset_id}/edit")
async def edit_asset_form(request: Request, asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    locations = (await db.execute(select(Location).order_by(Location.name))).scalars().all()
    return templates.TemplateResponse(
        request,
        "assets/form.html",
        {
            "asset": asset,
            "locations": locations,
            "asset_types": AssetType,
            "statuses": AssetStatus,
            "disposal_methods": DisposalMethod,
        },
    )


@router.post("/{asset_id}/edit")
async def update_asset(
    request: Request,
    asset_id: int,
    asset_tag: str = Form(...),
    asset_type: AssetType = Form(...),
    serial_number: str = Form(""),
    make: str = Form(""),
    model: str = Form(""),
    description: str = Form(""),
    purchase_date: date | None = Form(None),
    purchase_cost: float | None = Form(None),
    po_number: str = Form(""),
    vendor: str = Form(""),
    assigned_user: str = Form(""),
    department: str = Form(""),
    location_id: int | None = Form(None),
    status: AssetStatus = Form(AssetStatus.ACTIVE),
    warranty_expiration: date | None = Form(None),
    disposal_date: date | None = Form(None),
    disposal_method: DisposalMethod | None = Form(None),
    disposal_value: float | None = Form(None),
    disposal_notes: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    asset = await db.get(Asset, asset_id)
    asset.asset_tag = asset_tag
    asset.asset_type = asset_type
    asset.serial_number = serial_number or None
    asset.make = make or None
    asset.model = model or None
    asset.description = description or None
    asset.purchase_date = purchase_date
    asset.purchase_cost = purchase_cost
    asset.po_number = po_number or None
    asset.vendor = vendor or None
    asset.assigned_user = assigned_user or None
    asset.department = department or None
    asset.location_id = location_id
    asset.status = status
    asset.warranty_expiration = warranty_expiration
    asset.disposal_date = disposal_date
    asset.disposal_method = disposal_method
    asset.disposal_value = disposal_value
    asset.disposal_notes = disposal_notes or None
    await db.commit()

    return templates.TemplateResponse(
        request,
        "assets/_saved.html",
        {"asset": asset},
        headers={"HX-Push-Url": f"/assets/{asset.id}"},
    )


@router.delete("/{asset_id}")
async def delete_asset(asset_id: int, db: AsyncSession = Depends(get_db)):
    asset = await db.get(Asset, asset_id)
    await db.delete(asset)
    await db.commit()
    return ""
