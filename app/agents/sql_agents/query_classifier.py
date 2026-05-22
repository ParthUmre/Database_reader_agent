from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.core.logging import get_logger

# ==========================================
# LOGGER
# ==========================================
logger = get_logger(__name__)


# ==========================================
# LLM INITIALIZATION
# ==========================================
classifier_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,  # Uses google_api_key parameter
    temperature=0.1,
    max_tokens=20
)


# ==========================================
# CLASSIFICATION PROMPT
# ==========================================
CLASSIFICATION_PROMPT = PromptTemplate(
    input_variables=["query"],
    template="""
You are an enterprise AI query classifier.

Your task:
Classify the user query into EXACTLY one category.

AVAILABLE CATEGORIES:

1. SQL
- Database retrieval
- Inventory lookup
- Warehouse lookup
- Finance transaction queries
- Structured reporting
- Aggregations
- Counts
- Filtering
- Exact data retrieval

2. RAG
- Explanations
- Definitions
- Business understanding
- Operational guidance
- SOP retrieval
- Semantic knowledge queries

3. ANALYTICS
- Trends
- Summaries
- Insights
- Performance analysis
- Comparative analysis
- KPI-related requests

4. PREDICTIVE
- Forecasting
- Future demand prediction
- Risk prediction
- Recommendation requests
- Future trends

RULES:
- Return ONLY category name
- No explanation
- No punctuation
- One word only

EXAMPLES:

Query:
Show products with low stock

Category:
SQL

----------------------------

Query:
Explain inventory turnover ratio

Category:
RAG

----------------------------

Query:
Analyze warehouse performance trends

Category:
ANALYTICS

----------------------------

Query:
Predict future laptop demand

Category:
PREDICTIVE

----------------------------

USER QUERY:
{query}

CATEGORY:
"""
)


# ==========================================
# CLASSIFY QUERY
# ==========================================
def classify_query(user_query: str):
    try:
        logger.info(f"Classifying query: {user_query}")

        prompt = CLASSIFICATION_PROMPT.format(query=user_query)
        response = classifier_llm.invoke(prompt)

        # ✨ FIX: Extract the text string from the AIMessage object's content attribute
        if hasattr(response, "content"):
            raw_category = response.content
        else:
            raw_category = str(response)

        category = raw_category.strip().upper()

        allowed_categories = [
            "SQL",
            "RAG",
            "ANALYTICS",
            "PREDICTIVE"
        ]

        if category not in allowed_categories:
            logger.warning(f"Invalid classification: {category}")
            return "SQL"

        logger.info(f"Query classified as: {category}")
        return category

    except Exception as e:
        logger.error(f"Query classification failed: {e}")
        return "SQL"