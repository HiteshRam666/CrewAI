# content_crew.py
from dotenv import load_dotenv
from crewai import Crew, Task, Agent, Process, LLM
from crewai.project import CrewBase, agent, task, crew

load_dotenv()
llm = LLM(model="gpt-4o-mini")

@CrewBase
class ContentCrew:
    """Content writing crew with writer + reviewer"""

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            role="Educational Content Writer",
            goal=(
                "Create engaging, informative content that thoroughly explains the "
                "assigned topic and provides valuable insights to the reader"
            ),
            backstory=(
                "You are a talented educational writer with expertise in creating clear, "
                "engaging content. You explain complex concepts in accessible language "
                "and organize information to build understanding."
            ),
            llm=llm,
        )

    @agent
    def content_reviewer(self) -> Agent:
        return Agent(
            role="Educational Content Reviewer and Editor",
            goal=(
                "Ensure content is accurate, comprehensive, well-structured, and "
                "maintains consistency with previously written sections"
            ),
            backstory=(
                "You are a meticulous editor with years of experience reviewing "
                "educational content. You improve clarity, coherence, and accuracy "
                "while preserving the author's voice."
            ),
            llm=llm,
        )

    @task
    def write_section_task(self) -> Task:
        return Task(
            description="""
Write a comprehensive section on the topic: {section_title}
Section description: {section_description}
Target audience: {audience_level} level learners

Your content should:
1. Begin with a brief introduction to the section topic
2. Explain all key concepts clearly with examples
3. Include practical applications or exercises where appropriate
4. End with a summary of key points
5. Be approximately 500-800 words in length

Format your content in Markdown with appropriate headings, lists, and emphasis.

Previously written sections:
{previous_sections}

Make sure your content maintains consistency with previously written sections
and builds upon concepts that have already been explained.
""".strip(),
            expected_output=(
                "A well-structured, comprehensive section in Markdown format that "
                "thoroughly explains the topic and is appropriate for the target audience."
            ),
            agent=self.content_writer(),  # bind agent instance
        )

    @task
    def review_section_task(self) -> Task:
        return Task(
            description="""
Review and improve the following section on "{section_title}":
{draft_content}
Target audience: {audience_level} level learners

Previously written sections:
{previous_sections}

Your review should:
1. Fix any grammatical or spelling errors
2. Improve clarity and readability
3. Ensure content is comprehensive and accurate
4. Verify consistency with previously written sections
5. Enhance the structure and flow
6. Add any missing key information

Provide the improved version of the section in Markdown format.
""".strip(),
            expected_output=(
                "An improved, polished version of the section that maintains the original "
                "structure but enhances clarity, accuracy, and consistency."
            ),
            agent=self.content_reviewer(),
            context=[self.write_section_task()],  # depends on writer task
        )

    @crew
    def crew(self) -> Crew:
        """Sequential pipeline: writer -> reviewer"""
        return Crew(
            agents=[self.content_writer(), self.content_reviewer()],
            tasks=[self.write_section_task(), self.review_section_task()],
            process=Process.sequential,
            verbose=True,
        )
