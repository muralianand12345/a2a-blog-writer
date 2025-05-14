import click
from uuid import uuid4
from a2a.server import A2AServer
from a2a.server.request_handlers import DefaultA2ARequestHandler
from a2a.server.events import EventQueue
from a2a.server.agent_execution import BaseAgentExecutor
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Message,
    Part,
    Role,
    SendMessageRequest,
    SendStreamingMessageRequest,
    Task,
    TextPart,
)

from agents import BlogWriterAgent
from config import HOST, PORT
from utils.logger import logger
from utils.helpers import extract_text_from_parts


class BlogWriterAgentExecutor(BaseAgentExecutor):
    """A2A Agent Executor for the Blog Writer Agent."""

    def __init__(self):
        self.agent = BlogWriterAgent()
        logger.info("BlogWriterAgentExecutor initialized")

    async def on_message_send(
        self, request: SendMessageRequest, event_queue: EventQueue, task: Task | None
    ) -> None:
        """Handler for 'message/send' requests."""
        try:
            ack_message = Message(
                role=Role.agent,
                parts=[
                    Part(
                        TextPart(
                            text="Your blog post is being generated. This may take a minute..."
                        )
                    )
                ],
                messageId=str(uuid4()),
                final=False,
            )
            event_queue.enqueue_event(ack_message)

            topic = extract_text_from_parts(
                [part.root.model_dump() for part in request.params.message.parts]
            )

            result = await self.agent.invoke(topic)

            message = Message(
                role=Role.agent,
                parts=[Part(TextPart(text=result["content"]))],
                messageId=str(uuid4()),
                final=True,
            )
            event_queue.enqueue_event(message)
            logger.info("Blog writing completed and response sent")
        except Exception as e:
            logger.error(f"Error in blog writing: {str(e)}")
            message = Message(
                role=Role.agent,
                parts=[Part(TextPart(text=f"Error writing blog: {str(e)}"))],
                messageId=str(uuid4()),
                final=True,
            )
            event_queue.enqueue_event(message)

    async def on_message_stream(
        self,
        request: SendStreamingMessageRequest,
        event_queue: EventQueue,
        task: Task | None,
    ) -> None:
        """Handler for 'message/stream' requests."""
        try:
            topic = extract_text_from_parts(
                [part.root.model_dump() for part in request.params.message.parts]
            )

            async for chunk in self.agent.stream(topic):
                message = Message(
                    role=Role.agent,
                    parts=[Part(TextPart(text=chunk["content"]))],
                    messageId=str(uuid4()),
                    final=chunk["done"],
                )
                event_queue.enqueue_event(message)

            logger.info("Blog writing streaming completed")
        except Exception as e:
            logger.error(f"Error in blog writing streaming: {str(e)}")
            message = Message(
                role=Role.agent,
                parts=[Part(TextPart(text=f"Error writing blog: {str(e)}"))],
                messageId=str(uuid4()),
                final=True,
            )
            event_queue.enqueue_event(message)


@click.command()
@click.option("--host", default=HOST, help="Server host")
@click.option("--port", default=PORT, type=int, help="Server port")
def main(host: str, port: int):
    """Start the Blog Writer A2A Server."""
    logger.info(f"Starting Blog Writer A2A Server on {host}:{port}")

    # Define agent skill
    skill = AgentSkill(
        id="blog_writer",
        name="Blog Writer",
        description="Writes comprehensive blog posts on any topic",
        tags=["blog", "writing", "content creation"],
        examples=[
            "Write a blog about artificial intelligence",
            "Create a travel blog post about Paris",
            "Write a technical blog about Python programming",
        ],
    )

    # Create agent card
    agent_card = AgentCard(
        name="Blog Writer Agent",
        description="An advanced blog writing agent that creates high-quality blog posts on any topic",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
        authentication=AgentAuthentication(schemes=["public"]),
    )

    request_handler = DefaultA2ARequestHandler(agent_executor=BlogWriterAgentExecutor())

    server = A2AServer(agent_card=agent_card, request_handler=request_handler)
    logger.info("A2A Server initialized, starting now...")
    server.start(host=host, port=port)


if __name__ == "__main__":
    main()
