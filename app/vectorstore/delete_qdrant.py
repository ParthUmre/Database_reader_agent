from qdrant_client import QdrantClient

client = QdrantClient(
    host="localhost",
    port=6333
)

client.delete_collection(
    collection_name="enterprise_knowledge_base"
)

print("Collection deleted successfully")