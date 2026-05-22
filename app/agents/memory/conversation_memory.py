from collections import defaultdict
from datetime import datetime

from app.core.logging import get_logger


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# IN-MEMORY SESSION STORE
# ==========================================
conversation_store = defaultdict(list)


# ==========================================
# MAX MEMORY WINDOW
# ==========================================
MAX_HISTORY = 10


# ==========================================
# ADD MESSAGE TO MEMORY
# ==========================================
def add_message(

    session_id: str,

    role: str,

    message: str
):

    try:

        logger.info(
            f"Adding message to memory "
            f"for session: {session_id}"
        )

        conversation_store[session_id].append({

            "role": role,

            "message": message,

            "timestamp": str(
                datetime.utcnow()
            )
        })

        # ==============================
        # MEMORY WINDOW CONTROL
        # ==============================
        if len(
            conversation_store[session_id]
        ) > MAX_HISTORY:

            conversation_store[session_id] = (
                conversation_store[session_id][
                    -MAX_HISTORY:
                ]
            )

    except Exception as e:

        logger.error(
            f"Failed to add memory: {e}"
        )


# ==========================================
# GET CONVERSATION HISTORY
# ==========================================
def get_conversation_history(
    session_id: str
):

    try:

        logger.info(
            f"Fetching memory for session: "
            f"{session_id}"
        )

        return conversation_store.get(
            session_id,
            []
        )

    except Exception as e:

        logger.error(
            f"Failed to fetch memory: {e}"
        )

        return []


# ==========================================
# CLEAR SESSION MEMORY
# ==========================================
def clear_conversation_history(
    session_id: str
):

    try:

        logger.info(
            f"Clearing memory for session: "
            f"{session_id}"
        )

        if session_id in conversation_store:

            del conversation_store[session_id]

        return True

    except Exception as e:

        logger.error(
            f"Failed to clear memory: {e}"
        )

        return False


# ==========================================
# FORMAT MEMORY FOR LLM
# ==========================================
def format_conversation_history(
    session_id: str
):

    try:

        history = get_conversation_history(
            session_id
        )

        if not history:
            return ""

        formatted_history = []

        for item in history:

            formatted_history.append(

                f"{item['role'].upper()}: "
                f"{item['message']}"
            )

        return "\n".join(
            formatted_history
        )

    except Exception as e:

        logger.error(
            f"Failed to format memory: {e}"
        )

        return ""