import warnings
import logging
from datetime import datetime
from crew import AgenticRag
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", 
    handlers=[
        logging.FileHandler("agentic_rag.log"), 
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run():
    logger.info("Starting CrewAI RAG System...")

    """
    Run the crew.
    """
    print("\n" + "="*50)
    print("Starting CrewAI RAG System...")
    print("="*50)

    query = 'What are PEFT techniques ?'
    print(f"\nProcessing query: '{query}'")
    print("-"*50)

    logger.info(f"Processing query: {query}")

    inputs = {
        'query': query
    }


    try:
        logger.debug("Initializing crew...")
        result = AgenticRag().crew().kickoff(inputs=inputs)
        
        logger.info("Execution completed successfully!")
        logger.debug(f"Final result: {result}")
        
        return result

    except Exception as e:
        logger.exception("An error occurred while running the crew")
        raise

if __name__ == "__main__":
    run()

