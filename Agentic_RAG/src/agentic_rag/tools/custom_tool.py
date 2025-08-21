import os
from crewai.tools import BaseTool 
from typing import TypedDict, Type 
from pydantic import BaseModel, Field, ConfigDict 
from markitdown import MarkItDown 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from dotenv import load_dotenv 
import logging 
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DocumentSearchToolInput(BaseModel):
    query: str = Field(..., description="Query to search the document. Must contain a 'query' key with the query string")

class DocumentSearchTool(BaseTool):
    name: str = "DocumentSearchTool" 
    description: str = "Search the document for the given query string."
    args_schema: Type[BaseModel] = DocumentSearchToolInput
    file_path: str
    client: QdrantClient = None

    model_config = ConfigDict(extra="allow")

    def __init_post_init__(self, file_path: str):
        """Initialize the searcher with a PDF file path and set up the Qdrant collection."""
        self.file_path = file_path 
        self.client = QdrantClient(":memory:")
        logger.info(f"Initialized DocumentSearchTool with file: {file_path}")
        self._process_document() 
    
    def _extract_text(self) -> str:
        """Extract raw text from PDF using MarkItDown."""
        logger.debug(f"Extracting text from: {self.file_path}")
        md = MarkItDown() 
        result = md.convert(self.file_path)
        logger.debug("Text extraction completed") 
        return result.text_content
    
    def _create_chunks(self, raw_text) -> list:
        logger.debug("Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 532,
            chunk_overlap = 50, 
            length_function = len, 
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_text(raw_text)
        logger.info(f"Created {len(chunks)} chunks")
        return [{"text": chunk} for chunk in chunks]
    
    def _process_document(self):
        """Process the document and add chunks to Qdrant collection."""
        logger.info("Processing document...")
        raw_text = self._extract_text()
        chunks = self._create_chunks(raw_text)

        # Access the 'text' attribute from the dictionaries in 'chunks'
        docs = [chunk["text"] for chunk in chunks]

        # Keep the rest of the code the same
        metadata = [{"source": os.path.basename(self.file_path)} for _ in range(len(chunks))]
        ids = list(range(len(chunks)))

        self.client.add(
            collection_name="demo_collection", 
            documents = docs, 
            metadata = metadata, 
            ids = ids
        )
        logger.info("Document processed and indexed in Qdrant")
    
    def _run(self, query: dict) -> list:
        """Search the document with a query string."""
        logger.info(f"Running search query: {query['query']}")
        query = query["query"] 
        relevant_chunks = self.client.query(
            collection_name="demo_collection", 
            query_text=query
        )
        docs = [chunk.document for chunk in relevant_chunks]
        seperator = "\n___\n"
        logger.info(f"Retrieved {len(docs)} relevant chunks")
        return seperator.join(docs)