from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import get_logger

from app.vectorstore.search import (
    semantic_search
)


# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# LLM INITIALIZATION
# ==========================================

rag_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Or "gemini-2.5-pro" for complex reasoning tasks
    api_key=settings.GEMINI_API_KEY,  # Swapped to your Gemini key configuration
    temperature=0.3,
    max_tokens=400  # Note: 'max_new_tokens' changes to 'max_tokens'
)


# ==========================================
# RAG PROMPT
# ==========================================
RAG_PROMPT = PromptTemplate(

    input_variables=[
        "context",
        "question"
    ],

    template="""
You are an enterprise warehouse and finance AI assistant.

Your responsibilities:
- Explain warehouse operations
- Explain inventory concepts
- Explain finance transaction insights
- Answer operational business questions
- Use provided context only
- Generate clear professional responses

==================================================
RETRIEVED BUSINESS CONTEXT
==================================================

{context}

==================================================
RULES
==================================================

1. Use ONLY provided context
2. Do NOT hallucinate information
3. If answer is not available, say:
   "Relevant information was not found."
4. Be concise and professional
5. Focus on business understanding
6. Structure responses clearly

==================================================
USER QUESTION
==================================================

{question}

==================================================
ANSWER
==================================================
"""
)


# ==========================================
# RAG PIPELINE
# ==========================================
def run_rag_pipeline(
    user_query: str
):

    try:

        logger.info(
            f"Starting RAG pipeline for: "
            f"{user_query}"
        )

        # ==================================
        # STEP 1: RETRIEVE CONTEXT
        # ==================================
        rag_results = semantic_search(
            user_query,
            limit=5
        )

        logger.info(
            f"Retrieved {len(rag_results)} "
            f"context chunks."
        )

        # ==================================
        # STEP 2: BUILD CONTEXT
        # ==================================
        context = "\n\n".join([

            f"Context {index + 1}:\n"
            f"{result['text']}"

            for index, result
            in enumerate(rag_results)

        ])

        # ==================================
        # STEP 3: BUILD PROMPT
        # ==================================
        final_prompt = RAG_PROMPT.format(
            context=context,
            question=user_query
        )

        # ==================================
        # STEP 4: GENERATE RESPONSE
        # ==================================
        response = rag_llm.invoke(
            final_prompt
        )

        logger.info(
            "RAG response generated successfully."
        )

        # ==================================
        # FINAL RESPONSE
        # ==================================
        return {
            "success": True,
            "query_type": "RAG",
            "user_query": user_query,
            "retrieved_contexts": len(rag_results),
            "answer": response.strip(),
            "sources": rag_results
        }

    except Exception as e:

        logger.error(
            f"RAG pipeline failed: {e}"
        )

        return {
            "success": False,
            "error": str(e)
        }