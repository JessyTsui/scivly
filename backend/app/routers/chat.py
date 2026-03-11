from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import PaginationParams, get_current_user, get_db, get_pagination_params
from app.middleware.error_handler import APIError
from app.models import ChatMessage, ChatSession, Paper
from app.persistence import ensure_user
from app.schemas.auth import UserOut
from app.schemas.chat import ChatMessageCreate, ChatMessageOut, ChatReplyOut, ChatSessionCreate, ChatSessionOut
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


def _serialize_session(row) -> ChatSessionOut:
    return ChatSessionOut(
        id=row.id,
        workspace_id=row.workspace_id,
        paper_id=row.paper_id,
        session_type=row.session_type,
        title=row.title,
        created_at=row.created_at,
    )


def _serialize_message(row) -> ChatMessageOut:
    return ChatMessageOut(
        id=row.id,
        session_id=row.session_id,
        role=row.role,
        content=row.content,
        model=row.model,
        created_at=row.created_at,
    )


async def _get_session_row(session: AsyncSession, session_id: UUID, current_user: UserOut):
    row = (
        await session.execute(
            select(
                ChatSession.id,
                ChatSession.workspace_id,
                ChatSession.paper_id,
                ChatSession.session_type,
                ChatSession.title,
                ChatSession.created_at,
            )
            .where(ChatSession.id == session_id)
            .where(ChatSession.workspace_id == current_user.workspace_id)
            .where(ChatSession.user_id == current_user.id)
        )
    ).one_or_none()
    if row is None:
        raise APIError(status_code=404, code="chat_session_not_found", message="Chat session not found.")
    return row


@router.get("/sessions", response_model=PaginatedResponse[ChatSessionOut])
async def list_sessions(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ChatSessionOut]:
    total = (
        await session.execute(
            select(func.count())
            .select_from(ChatSession)
            .where(ChatSession.workspace_id == current_user.workspace_id)
            .where(ChatSession.user_id == current_user.id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                ChatSession.id,
                ChatSession.workspace_id,
                ChatSession.paper_id,
                ChatSession.session_type,
                ChatSession.title,
                ChatSession.created_at,
            )
            .where(ChatSession.workspace_id == current_user.workspace_id)
            .where(ChatSession.user_id == current_user.id)
            .order_by(ChatSession.created_at.desc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    return PaginatedResponse[ChatSessionOut](
        items=[_serialize_session(row) for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: ChatSessionCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ChatSessionOut:
    session_id = uuid4()
    title = payload.title or "New Scivly chat session"

    if payload.paper_id is not None:
        paper_exists = (
            await session.execute(select(Paper.id).where(Paper.id == payload.paper_id))
        ).scalar_one_or_none()
        if paper_exists is None:
            raise APIError(status_code=404, code="paper_not_found", message="Paper not found.")

    await ensure_user(session, current_user)
    try:
        await session.execute(
            insert(ChatSession).values(
                id=session_id,
                workspace_id=current_user.workspace_id,
                user_id=current_user.id,
                paper_id=payload.paper_id,
                session_type=payload.session_type,
                title=title,
            )
        )
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise APIError(status_code=400, code="chat_session_invalid", message="Chat session payload is invalid.") from exc

    row = await _get_session_row(session, session_id, current_user)
    return _serialize_session(row)


@router.get("/sessions/{session_id}/messages", response_model=PaginatedResponse[ChatMessageOut])
async def get_history(
    session_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ChatMessageOut]:
    await _get_session_row(session, session_id, current_user)
    total = (
        await session.execute(
            select(func.count())
            .select_from(ChatMessage)
            .where(ChatMessage.session_id == session_id)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(
                ChatMessage.id,
                ChatMessage.session_id,
                ChatMessage.role,
                ChatMessage.content,
                ChatMessage.model,
                ChatMessage.created_at,
            )
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .offset((pagination.page - 1) * pagination.per_page)
            .limit(pagination.per_page)
        )
    ).all()

    return PaginatedResponse[ChatMessageOut](
        items=[_serialize_message(row) for row in rows],
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatReplyOut)
async def send_message(
    session_id: UUID,
    payload: ChatMessageCreate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ChatReplyOut:
    session_row = await _get_session_row(session, session_id, current_user)

    paper_title = None
    if session_row.paper_id is not None:
        paper_title = (
            await session.execute(select(Paper.title).where(Paper.id == session_row.paper_id))
        ).scalar_one_or_none()

    user_message_id = uuid4()
    assistant_message_id = uuid4()
    assistant_content = (
        f"Stored placeholder reply for {paper_title}."
        if paper_title
        else "Stored placeholder reply for this Scivly chat session."
    )

    await session.execute(
        insert(ChatMessage).values(
            id=user_message_id,
            session_id=session_id,
            role="user",
            content=payload.content,
            model=None,
        )
    )
    await session.execute(
        insert(ChatMessage).values(
            id=assistant_message_id,
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            model="gpt-4.1-mini",
        )
    )
    await session.commit()

    message_rows = (
        await session.execute(
            select(
                ChatMessage.id,
                ChatMessage.session_id,
                ChatMessage.role,
                ChatMessage.content,
                ChatMessage.model,
                ChatMessage.created_at,
            )
            .where(ChatMessage.id.in_([user_message_id, assistant_message_id]))
            .order_by(ChatMessage.created_at.asc())
        )
    ).all()

    user_message = next(row for row in message_rows if row.id == user_message_id)
    assistant_message = next(row for row in message_rows if row.id == assistant_message_id)

    return ChatReplyOut(
        session=_serialize_session(session_row),
        user_message=_serialize_message(user_message),
        assistant_message=_serialize_message(assistant_message),
        cited_paper_ids=[paper_id for paper_id in [session_row.paper_id] if paper_id is not None],
    )
