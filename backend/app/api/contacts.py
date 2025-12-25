"""Contacts API routes."""

from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.contact import Contact, ContactCreate, ContactResponse, Interaction
from app.models.db_models import ContactDB, InteractionDB

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=List[ContactResponse])
async def list_contacts(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all contacts."""
    query = select(ContactDB)

    if search:
        query = query.where(
            ContactDB.name.ilike(f"%{search}%") |
            ContactDB.email.ilike(f"%{search}%") |
            ContactDB.company.ilike(f"%{search}%")
        )

    query = query.order_by(ContactDB.updated_at.desc()).limit(limit)

    result = await db.execute(query)
    contacts = result.scalars().all()

    responses = []
    for contact in contacts:
        # Get interaction stats
        interaction_result = await db.execute(
            select(
                func.count(InteractionDB.id),
                func.max(InteractionDB.date),
                func.min(InteractionDB.date)
            ).where(InteractionDB.contact_id == contact.id)
        )
        stats = interaction_result.first()

        responses.append(ContactResponse(
            id=contact.id,
            email=contact.email,
            name=contact.name,
            title=contact.title,
            company=contact.company,
            phone=contact.phone,
            linkedin_url=contact.linkedin_url,
            twitter_url=contact.twitter_url,
            tags=contact.tags or [],
            custom_fields=contact.custom_fields or {},
            crm_id=contact.crm_id,
            crm_provider=contact.crm_provider,
            total_interactions=stats[0] or 0,
            last_interaction=stats[1],
            first_interaction=stats[2],
            created_at=contact.created_at,
            updated_at=contact.updated_at
        ))

    return responses


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get contact details."""
    result = await db.execute(
        select(ContactDB).where(ContactDB.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Get interaction stats
    interaction_result = await db.execute(
        select(
            func.count(InteractionDB.id),
            func.max(InteractionDB.date),
            func.min(InteractionDB.date)
        ).where(InteractionDB.contact_id == contact.id)
    )
    stats = interaction_result.first()

    return ContactResponse(
        id=contact.id,
        email=contact.email,
        name=contact.name,
        title=contact.title,
        company=contact.company,
        phone=contact.phone,
        linkedin_url=contact.linkedin_url,
        twitter_url=contact.twitter_url,
        tags=contact.tags or [],
        custom_fields=contact.custom_fields or {},
        crm_id=contact.crm_id,
        crm_provider=contact.crm_provider,
        total_interactions=stats[0] or 0,
        last_interaction=stats[1],
        first_interaction=stats[2],
        created_at=contact.created_at,
        updated_at=contact.updated_at
    )


@router.post("", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact."""
    # Check for existing
    existing = await db.execute(
        select(ContactDB).where(ContactDB.email == contact.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Contact with this email already exists")

    db_contact = ContactDB(
        id=str(uuid.uuid4()),
        email=contact.email,
        name=contact.name,
        title=contact.title,
        company=contact.company,
        phone=contact.phone,
        tags=contact.tags
    )

    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)

    return ContactResponse(
        id=db_contact.id,
        email=db_contact.email,
        name=db_contact.name,
        title=db_contact.title,
        company=db_contact.company,
        phone=db_contact.phone,
        tags=db_contact.tags or [],
        custom_fields={},
        total_interactions=0,
        created_at=db_contact.created_at,
        updated_at=db_contact.updated_at
    )


@router.get("/{contact_id}/history")
async def get_contact_history(
    contact_id: str,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get interaction history for a contact."""
    # Verify contact exists
    result = await db.execute(
        select(ContactDB).where(ContactDB.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Get interactions
    interactions_result = await db.execute(
        select(InteractionDB)
        .where(InteractionDB.contact_id == contact_id)
        .order_by(InteractionDB.date.desc())
        .limit(limit)
    )
    interactions = interactions_result.scalars().all()

    return {
        "contact_id": contact_id,
        "contact_name": contact.name,
        "interactions": [
            {
                "id": i.id,
                "type": i.type,
                "date": i.date.isoformat(),
                "summary": i.summary,
                "sentiment": i.sentiment,
                "key_topics": i.key_topics or []
            }
            for i in interactions
        ]
    }


@router.put("/{contact_id}")
async def update_contact(
    contact_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db)
):
    """Update a contact."""
    result = await db.execute(
        select(ContactDB).where(ContactDB.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    allowed_fields = ["name", "title", "company", "phone", "linkedin_url", "twitter_url", "tags"]
    for field in allowed_fields:
        if field in updates:
            setattr(contact, field, updates[field])

    contact.updated_at = datetime.utcnow()
    await db.commit()

    return {"updated": True, "contact_id": contact_id}


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a contact."""
    result = await db.execute(
        select(ContactDB).where(ContactDB.id == contact_id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    await db.delete(contact)
    await db.commit()

    return {"deleted": True, "contact_id": contact_id}
