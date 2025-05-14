from langchain_openai import ChatOpenAI
from typing import Dict, Any, AsyncGenerator
from langchain.prompts import ChatPromptTemplate

from utils.logger import logger
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE

OUTLINE_GENERATOR_PROMPT = """
You are a specialized blog outline generator. Your task is to:

1. Create a compelling and structured outline based on the research provided
2. Include an engaging introduction, clear sections with subpoints, and a conclusion
3. Make sure the outline flows logically and covers all key points
4. Suggest a compelling title for the blog post

Research Summary: {research}

Provide a detailed outline with a clear structure, including title, introduction, sections, and conclusion.
"""


class OutlineGeneratorAgent:
    """Agent responsible for generating blog outlines."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=TEMPERATURE
        )
        self.prompt = ChatPromptTemplate.from_template(OUTLINE_GENERATOR_PROMPT)
        logger.info("OutlineGeneratorAgent initialized")

    async def process(self, research: str) -> Dict[str, Any]:
        """Process research and generate a blog outline."""
        logger.info("Generating outline based on research")

        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"research": research})
            outline_result = response.content

            logger.info("Outline generation completed successfully")
            return {"content": outline_result, "success": True}
        except Exception as e:
            logger.error(f"Error in outline generation: {str(e)}")
            return {"content": f"Error generating outline: {str(e)}", "success": False}

    async def stream_process(
        self, research: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream process research and yield outline generation results."""
        logger.info("Streaming outline generation")

        chain = self.prompt | self.llm

        try:
            async for chunk in chain.astream({"research": research}):
                yield {
                    "content": chunk.content
                    if hasattr(chunk, "content")
                    else str(chunk),
                    "done": False,
                }

            yield {"content": "", "done": True}
            logger.info("Outline generation streaming completed")
        except Exception as e:
            logger.error(f"Error in outline generation streaming: {str(e)}")
            yield {"content": f"Error generating outline: {str(e)}", "done": True}
