from langchain_openai import ChatOpenAI
from typing import Dict, Any, AsyncGenerator
from langchain.prompts import ChatPromptTemplate

from utils.logger import logger
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE

CONTENT_WRITER_PROMPT = """
You are a specialized blog content writer. Your task is to:

1. Write a comprehensive blog post based on the outline provided
2. Create engaging, well-structured content with proper headings and subheadings
3. Maintain a conversational and approachable tone
4. Include a strong introduction that hooks the reader and a conclusion that summarizes key points
5. Make the content valuable, informative, and actionable

Outline: {outline}

Write a complete blog post following the outline exactly.
"""


class ContentWriterAgent:
    """Agent responsible for writing blog content."""

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY, model=MODEL_NAME, temperature=TEMPERATURE
        )
        self.prompt = ChatPromptTemplate.from_template(CONTENT_WRITER_PROMPT)
        logger.info("ContentWriterAgent initialized")

    async def process(self, outline: str) -> Dict[str, Any]:
        """Process an outline and write a blog post."""
        logger.info("Writing content based on outline")

        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"outline": outline})
            content_result = response.content

            logger.info("Content writing completed successfully")
            return {"content": content_result, "success": True}
        except Exception as e:
            logger.error(f"Error in content writing: {str(e)}")
            return {"content": f"Error writing content: {str(e)}", "success": False}

    async def stream_process(
        self, outline: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream process an outline and yield blog content results."""
        logger.info("Streaming content writing")

        chain = self.prompt | self.llm

        try:
            async for chunk in chain.astream({"outline": outline}):
                yield {
                    "content": chunk.content
                    if hasattr(chunk, "content")
                    else str(chunk),
                    "done": False,
                }

            yield {"content": "", "done": True}
            logger.info("Content writing streaming completed")
        except Exception as e:
            logger.error(f"Error in content writing streaming: {str(e)}")
            yield {"content": f"Error writing content: {str(e)}", "done": True}
