from langchain_openai import ChatOpenAI
from typing import Dict, Any, AsyncGenerator
from langchain.prompts import ChatPromptTemplate

from utils.logger import logger
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE

TOPIC_RESEARCH_PROMPT = """
You are a specialized blog topic research agent. Your task is to:

1. Analyze the given blog topic
2. Research key points that should be included
3. Identify the target audience
4. Suggest a clear angle or perspective 
5. Provide 3-5 key points that should be covered in the blog post

Topic: {topic}

Provide your research in a structured format with clear sections.
"""


class TopicResearchAgent:
    """Agent responsible for blog topic research."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=TEMPERATURE
        )
        self.prompt = ChatPromptTemplate.from_template(TOPIC_RESEARCH_PROMPT)
        logger.info("TopicResearchAgent initialized")

    async def process(self, topic: str) -> Dict[str, Any]:
        """Process a topic and return research results."""
        logger.info(f"Researching topic: {topic}")

        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"topic": topic})
            research_result = response.content

            logger.info("Topic research completed successfully")
            return {"content": research_result, "success": True}
        except Exception as e:
            logger.error(f"Error in topic research: {str(e)}")
            return {"content": f"Error researching topic: {str(e)}", "success": False}

    async def stream_process(self, topic: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream process a topic and yield research results."""
        logger.info(f"Streaming research for topic: {topic}")

        chain = self.prompt | self.llm

        try:
            async for chunk in chain.astream({"topic": topic}):
                yield {
                    "content": chunk.content
                    if hasattr(chunk, "content")
                    else str(chunk),
                    "done": False,
                }

            yield {"content": "", "done": True}
            logger.info("Topic research streaming completed")
        except Exception as e:
            logger.error(f"Error in topic research streaming: {str(e)}")
            yield {"content": f"Error researching topic: {str(e)}", "done": True}
