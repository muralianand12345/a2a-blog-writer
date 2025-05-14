from typing import Dict, Any, AsyncGenerator

from utils.logger import logger
from agents.topic_research_agent import TopicResearchAgent
from agents.outline_generator_agent import OutlineGeneratorAgent
from agents.content_writer_agent import ContentWriterAgent


class BlogWriterAgent:
    """Main Blog Writer Agent that coordinates the specialized agents."""

    def __init__(self):
        self.topic_researcher = TopicResearchAgent()
        self.outline_generator = OutlineGeneratorAgent()
        self.content_writer = ContentWriterAgent()
        logger.info("BlogWriterAgent initialized with all specialized agents")

    async def invoke(self, topic: str) -> Dict[str, Any]:
        """Process a blog writing request end-to-end."""
        logger.info(f"Starting blog writing process for topic: {topic}")

        # Step 1: Research the topic
        logger.info("Step 1/3: Researching topic...")
        research_result = await self.topic_researcher.process(topic)
        if not research_result["success"]:
            return {
                "content": f"Research failed: {research_result['content']}",
                "success": False,
            }

        # Step 2: Generate an outline
        logger.info("Step 2/3: Generating outline...")
        outline_result = await self.outline_generator.process(
            research_result["content"]
        )
        if not outline_result["success"]:
            return {
                "content": f"Outline generation failed: {outline_result['content']}",
                "success": False,
            }

        # Step 3: Write the content
        logger.info("Step 3/3: Writing content...")
        content_result = await self.content_writer.process(outline_result["content"])

        # Return the final result
        logger.info("Blog writing process completed")
        return content_result

    async def stream(self, topic: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the blog writing process, showing progress at each stage."""
        logger.info(f"Starting streaming blog writing process for topic: {topic}")

        # Step 1: Research the topic (streaming)
        yield {"content": "\n\n🔍 Researching topic...\n\n", "done": False}
        research_content = ""

        async for chunk in self.topic_researcher.stream_process(topic):
            if chunk["done"]:
                research_content = research_content.strip()
                yield {"content": "\n\n✅ Research completed\n\n", "done": False}
                break

            research_content += chunk["content"]
            yield {"content": chunk["content"], "done": False}

        if not research_content:
            yield {"content": "\n\n❌ Research failed\n\n", "done": True}
            return

        # Step 2: Generate an outline (streaming)
        yield {"content": "\n\n📝 Generating outline...\n\n", "done": False}
        outline_content = ""

        async for chunk in self.outline_generator.stream_process(research_content):
            if chunk["done"]:
                outline_content = outline_content.strip()
                yield {"content": "\n\n✅ Outline completed\n\n", "done": False}
                break

            outline_content += chunk["content"]
            yield {"content": chunk['content'], "done": False}

        if not outline_content:
            yield {"content": "\n\n❌ Outline generation failed\n\n", "done": True}
            return

        # Step 3: Write the content (streaming)
        yield {"content": "\n\n✍️ Writing blog content...\n\n", "done": False}
        blog_content = ""

        async for chunk in self.content_writer.stream_process(outline_content):
            if chunk["done"]:
                yield {"content": "\n\n✅ Blog writing completed\n\n", "done": False}
                break

            blog_content += chunk["content"]
            yield {"content": chunk["content"], "done": False}

        # Final result
        if blog_content:
            yield {"content": f"\n\n{blog_content}\n", "done": True}
        else:
            yield {"content": "\n\n❌ Content writing failed\n\n", "done": True}
