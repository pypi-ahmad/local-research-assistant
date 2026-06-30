"""Chat and RAG endpoints."""

from __future__ import annotations

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lra_api.api.deps import get_current_user
from lra_api.db.models import Chat, Citation, Message, Notebook, User
from lra_api.db.session import get_db_session
from lra_api.schemas.chat import ChatCreateRequest, ChatMessageRequest, ChatMessageResponse
from lra_api.schemas.search import SearchRequest
from lra_api.services.retrieval.service import RetrievalService

router = APIRouter()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: ChatCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Create research chat session."""
    notebook_result = await db.execute(
        select(Notebook).where(Notebook.id == payload.notebook_id, Notebook.owner_id == current_user.id)
    )
    notebook = notebook_result.scalar_one_or_none()
    if notebook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found")

    chat = Chat(notebook_id=payload.notebook_id, title=payload.title)
    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    return {"chat_id": str(chat.id)}


@router.get("/sessions/{chat_id}")
async def get_chat_session(
    chat_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    """Get chat session and message history for resume workflows."""
    chat_result = await db.execute(
        select(Chat)
        .join(Notebook, Notebook.id == Chat.notebook_id)
        .where(Chat.id == chat_id, Notebook.owner_id == current_user.id)
    )
    chat = chat_result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    messages_result = await db.execute(select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at.asc()))
    messages = messages_result.scalars().all()

    return {
        "chat_id": str(chat.id),
        "title": chat.title,
        "notebook_id": str(chat.notebook_id),
        "messages": [
            {
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "citations": message.citations_json,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ],
    }


@router.get("/sessions")
async def list_chat_sessions(
    notebook_id: UUID | None = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, str]]:
    """List available chat sessions for user notebook history."""
    query = select(Chat).join(Notebook, Notebook.id == Chat.notebook_id).where(Notebook.owner_id == current_user.id)
    if notebook_id is not None:
        query = query.where(Chat.notebook_id == notebook_id)
    result = await db.execute(query.order_by(Chat.updated_at.desc()))
    chats = result.scalars().all()
    return [{"chat_id": str(chat.id), "title": chat.title, "notebook_id": str(chat.notebook_id)} for chat in chats]


@router.post("/sessions/{chat_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    chat_id: UUID,
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ChatMessageResponse:
    """Generate grounded response with citations."""
    chat_result = await db.execute(
        select(Chat)
        .join(Notebook, Notebook.id == Chat.notebook_id)
        .where(Chat.id == chat_id, Notebook.owner_id == current_user.id)
    )
    chat = chat_result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    user_msg = Message(chat_id=chat.id, role="user", content=payload.query, citations_json=[])
    db.add(user_msg)
    await db.flush()

    retrieval = RetrievalService()
    hits = await retrieval.search(
        db=db,
        query=payload.query,
        notebook_id=str(chat.notebook_id),
        top_k=payload.top_k,
        source_types=[],
        date_from=None,
        date_to=None,
    )
    answer, citations = await retrieval.build_answer(payload.query, hits)

    assistant_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=answer,
        citations_json=json.loads(json.dumps(citations)),
    )
    db.add(assistant_msg)
    await db.flush()

    for citation in citations:
        db.add(
            Citation(
                message_id=assistant_msg.id,
                document_id=UUID(citation["document_id"]),
                chunk_id=UUID(citation["chunk_id"]),
                quote=citation["quote"],
                page_number=citation.get("page_number"),
            )
        )

    await db.commit()

    return ChatMessageResponse(answer=answer, citations=citations)


@router.post("/rag", response_model=ChatMessageResponse)
async def rag_answer(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ChatMessageResponse:
    """One-shot RAG answer without chat session persistence."""
    retrieval = RetrievalService()
    hits = await retrieval.search(
        db=db,
        query=payload.query,
        notebook_id=str(payload.notebook_id) if payload.notebook_id else None,
        top_k=payload.top_k,
        source_types=payload.source_types,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )
    answer, citations = await retrieval.build_answer(payload.query, hits)
    return ChatMessageResponse(answer=answer, citations=citations)


@router.post("/sessions/{chat_id}/stream")
async def stream_message(
    chat_id: UUID,
    payload: ChatMessageRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> EventSourceResponse:
    """Stream grounded answer tokens for chat UX."""
    chat_result = await db.execute(
        select(Chat)
        .join(Notebook, Notebook.id == Chat.notebook_id)
        .where(Chat.id == chat_id, Notebook.owner_id == current_user.id)
    )
    chat = chat_result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    retrieval = RetrievalService()
    hits = await retrieval.search(
        db=db,
        query=payload.query,
        notebook_id=str(chat.notebook_id),
        top_k=payload.top_k,
        source_types=[],
        date_from=None,
        date_to=None,
    )
    answer, citations = await retrieval.build_answer(payload.query, hits)

    async def _event_generator() -> object:
        yield {"event": "start", "data": json.dumps({"citations": citations})}
        for token in answer.split():
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(_event_generator())
