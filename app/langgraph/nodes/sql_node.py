from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

from app.langgraph.state.graph_state import (
    GraphState
)

from app.agents.sql_agents.sql_pipeline import (
    run_sql_pipeline
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# DATABASE SESSION
# ==========================================
DATABASE_URL = (

    f"mysql+pymysql://"

    f"{settings.MYSQL_USER}:"

    f"{settings.MYSQL_PASSWORD}@"

    f"{settings.MYSQL_HOST}:"

    f"{settings.MYSQL_PORT}/"

    f"{settings.MYSQL_DATABASE}"
)

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# SQL NODE
# ==========================================
def sql_node(
    state: GraphState
):

    db = SessionLocal()

    try:

        logger.info(
            "Executing SQL node."
        )

        # ==================================
        # FETCH STATE DATA
        # ==================================
        user_query = state.get(
            "user_query",
            ""
        )

        session_id = state.get(
            "session_id"
        )

        # ==================================
        # RUN SQL PIPELINE
        # ==================================
        result = run_sql_pipeline(

            db=db,

            user_query=user_query,

            session_id=session_id
        )

        logger.info(
            "SQL pipeline executed successfully."
        )

        # ==================================
        # TRACK VISITED NODES
        # ==================================
        visited_nodes = state.get(
            "visited_nodes",
            []
        )

        visited_nodes.append(
            "sql_node"
        )

        # ==================================
        # UPDATE STATE
        # ==================================
        updated_state = {

            **state,

            "success": result.get(
                "success",
                False
            ),

            "generated_sql": result.get(
                "generated_sql"
            ),

            "sql_result": result,

            "final_response": result,

            "visited_nodes": visited_nodes
        }

        return updated_state

    except Exception as e:

        logger.error(
            f"SQL node failed: {e}"
        )

        return {

            **state,

            "success": False,

            "error": str(e)
        }

    finally:

        db.close()
