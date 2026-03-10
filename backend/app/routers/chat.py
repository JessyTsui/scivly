from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.deps import PaginationParams, get_current_user, get_pagination_params
from app.middleware.error_handler import APIError
from app.schemas.auth import UserOut
from app.schemas.chat import ChatMessageCreate, ChatMessageOut, ChatReplyOut, ChatSessionCreate, ChatSessionOut
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

SESSIONS = {
    UUID("16161616-1616-1616-1616-161616161616"): ChatSessionOut(
        id=UUID("16161616-1616-1616-1616-161616161616"),
        workspace_id=UUID("22222222-2222-2222-2222-222222222222"),
        paper_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        session_type="paper_qa",
        title="Sparse self-critique paper QA",
        created_at=datetime(2026, 3, 10, 2, 0, tzinfo=timezone.utc),
    )
}

MESSAGES = {
    UUID("16161616-1616-1616-1616-161616161616"): [
        ChatMessageOut(
            id=UUID("17171717-1717-1717-1717-171717171717"),
            session_id=UUID("16161616-1616-1616-1616-161616161616"),
            role="user",
            content="What is the main contribution?",
            model=None,
            created_at=datetime(2026, 3, 10, 2, 1, tzinfo=timezone.utc),
        ),
        ChatMessageOut(
            id=UUID("18181818-1818-1818-1818-181818181818"),
            session_id=UUID("16161616-1616-1616-1616-161616161616"),
            role="assistant",
            content="The paper introduces a staged control loop that escalates expensive tool calls only after metadata signals justify it.",
            model="gpt-4o-mini",
            created_at=datetime(2026, 3, 10, 2, 1, 5, tzinfo=timezone.utc),
        ),
    ]
}


def _get_session(session_id: UUID) -> ChatSessionOut:
    session = SESSIONS.get(session_id)
    if session is None:
        raise APIError(status_code=404, code="chat_session_not_found", message="Chat session not found.")
    return session


@router.get("/sessions", response_model=PaginatedResponse[ChatSessionOut])
def list_sessions(
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[ChatSessionOut]:
    items = sorted(SESSIONS.values(), key=lambda session: session.created_at, reverse=True)
    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    return PaginatedResponse[ChatSessionOut](
        items=items[start:end],
        total=len(items),
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_session(payload: ChatSessionCreate, _: UserOut = Depends(get_current_user)) -> ChatSessionOut:
    return ChatSessionOut(
        id=UUID("19191919-1919-1919-1919-191919191919"),
        workspace_id=payload.workspace_id,
        paper_id=payload.paper_id,
        session_type=payload.session_type,
        title=payload.title or "New Scivly chat session",
        created_at=datetime(2026, 3, 10, 9, 25, tzinfo=timezone.utc),
    )


@router.get("/sessions/{session_id}/messages", response_model=PaginatedResponse[ChatMessageOut])
def get_history(
    session_id: UUID,
    pagination: PaginationParams = Depends(get_pagination_params),
    _: UserOut = Depends(get_current_user),
) -> PaginatedResponse[ChatMessageOut]:
    _get_session(session_id)
    items = MESSAGES.get(session_id, [])
    start = (pagination.page - 1) * pagination.per_page
    end = start + pagination.per_page
    return PaginatedResponse[ChatMessageOut](
        items=items[start:end],
        total=len(items),
        page=pagination.page,
        per_page=pagination.per_page,
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatReplyOut)
def send_message(
    session_id: UUID,
    payload: ChatMessageCreate,
    _: UserOut = Depends(get_current_user),
) -> ChatReplyOut:
    session = _get_session(session_id)
    user_message = ChatMessageOut(
        id=UUID("20202020-2020-2020-2020-202020202020"),
        session_id=session_id,
        role="user",
        content=payload.content,
        model=None,
        created_at=datetime(2026, 3, 10, 9, 27, tzinfo=timezone.utc),
    )
    assistant_message = ChatMessageOut(
        id=UUID("21212121-2121-2121-2121-212121212121"),
        session_id=session_id,
        role="assistant",
        content="Mock answer: the current backend skeleton returns placeholder chat completions while preserving the final response shape.",
        model="gpt-4o-mini",
        created_at=datetime(2026, 3, 10, 9, 27, 3, tzinfo=timezone.utc),
    )
    return ChatReplyOut(
        session=session,
        user_message=user_message,
        assistant_message=assistant_message,
        cited_paper_ids=[paper_id for paper_id in [session.paper_id] if paper_id is not None],
    )
