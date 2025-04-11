import laima
from chatbot.core.chat_service import ChatService


@laima.inject
def chat_endpoint(
    chat_id: str,
    message: str,
    service: ChatService,
) -> str:
    return service.chat(chat_id, message)
