from crewai import Crew, Task, Process, Agent 
from crewai.project import CrewBase, agent, crew, task 
from crewai_tools import SerperDevTool
from tools.custom_tool import DocumentSearchTool
import logging

pdf_tool = DocumentSearchTool(file_path="C:\\Users\\hites\\OneDrive\\Desktop\\CrewAI\\Agentic_RAG\\knowledge\\AI Engineering.pdf")
web_search_tool = SerperDevTool()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@CrewBase 
class AgenticRag():
    "AgenticRAG Crew" 

    @agent 
    def retriever_agent(self) -> Agent:
        logger.info("Initializing retriever_agent...")
        return Agent(
            role="Retriever",
            goal="Find the most relevant info for a query",
            backstory="An expert retriever for documents and web.",
            verbose=True, 
            tools=[pdf_tool, web_search_tool]
        )
    
    @agent 
    def response_synthesizer_agent(self) -> Agent:
        logger.info("Initializing response_synthesizer_agent...")
        return Agent( 
            role="Responder",
            goal="Synthesize a clear answer from retrieved info",
            backstory="An expert in summarization and synthesis.",
            verbose=True
        )
    
    @task 
    def retrieval_task(self) -> Task:
        logger.info("Creating retrieval_task manually...")
        return Task(
            description="Retrieve the most relevant information from the available sources for the user query: {query}",
            expected_output="The most relevant information in form of text as retrieved from the sources.",
            agent=self.retriever_agent()   # ✅ FIX
        )
    
    @task 
    def response_task(self) -> Task:
        logger.info("Creating response_task manually...")
        return Task(
            description="Synthesize the final response for the user query: {query}",
            expected_output="A concise and coherent response. If nothing is retrieved, respond with 'I'm sorry, I couldn't find the information you're looking for.'",
            agent=self.response_synthesizer_agent()   # ✅ FIX
        )
    
    @crew 
    def crew(self) -> Crew:
        logger.info("Building the crew pipeline...")
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
