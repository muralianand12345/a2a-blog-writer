import os
import uuid
import httpx
import asyncio
from typing import Dict, Any
from a2a.client import A2AClient
from a2a.types import SendMessageResponse, SendMessageSuccessResponse

from config import SERVER_URL
from utils.logger import logger
from prompts import (
    WELCOME_MESSAGE,
    TOPIC_PROMPT,
    STREAMING_PROMPT,
    SAVE_PROMPT,
    FILENAME_PROMPT,
    CONTINUE_PROMPT,
    GOODBYE_MESSAGE,
)
from constants import (
    BLOG_FILE_EXTENSION,
    DEFAULT_FILENAME,
    BLOG_OUTPUT_DIR,
)


async def get_a2a_client():
    """Get a new A2A client."""
    http_client = httpx.AsyncClient()
    client = await A2AClient.get_client_from_agent_card_url(http_client, SERVER_URL)
    logger.info(f"Successfully connected to server at {SERVER_URL}")
    return client, http_client


async def send_blog_request(topic: str, stream: bool = False) -> str:
    """Send a blog writing request to the server."""
    client, http_client = await get_a2a_client()

    try:
        message_id = str(uuid.uuid4())
        send_message_payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": topic}],
                "messageId": message_id,
            },
        }

        if stream:
            result = await stream_blog_request(client, send_message_payload)
        else:
            result = await non_stream_blog_request(client, send_message_payload)

        return result
    finally:
        await http_client.aclose()


async def non_stream_blog_request(client: A2AClient, payload: Dict[str, Any]) -> str:
    """Send a non-streaming blog writing request."""
    logger.info("Sending non-streaming blog request")
    try:
        response: SendMessageResponse = await client.send_message(payload=payload)

        if isinstance(response.root, SendMessageSuccessResponse):
            if hasattr(response.root.result, "parts") and response.root.result.parts:
                # Extract text from message parts
                content = ""
                for part in response.root.result.parts:
                    if hasattr(part.root, "text"):
                        content += part.root.text
                return content
            else:
                logger.warning("Response does not contain expected content")
                return "No content was returned from the server."
        else:
            error_message = getattr(response.root.error, "message", "Unknown error")
            logger.error(f"Error in blog request: {error_message}")
            return f"Error: {error_message}"
    except Exception as e:
        logger.error(f"Error in non-streaming blog request: {str(e)}")
        return f"Error: {str(e)}"


async def stream_blog_request(client: A2AClient, payload: Dict[str, Any]) -> str:
    """Send a streaming blog writing request."""
    logger.info("Sending streaming blog request")
    full_content = ""
    last_update = ""

    try:
        stream_response = client.send_message_streaming(payload=payload)

        print("\n--- Writing your blog post (streaming) ---\n")

        async for chunk in stream_response:
            if hasattr(chunk.root.result, "parts") and chunk.root.result.parts:
                for part in chunk.root.result.parts:
                    if hasattr(part.root, "text"):
                        content = part.root.text
                        # Only print if there's new content to avoid duplicates
                        if not content.startswith(last_update):
                            print(content, end="", flush=True)
                            last_update = content
                        full_content = content  # For the final return value

        print("\n\n--- Blog post completed ---\n")
        return full_content
    except Exception as e:
        logger.error(f"Error in streaming blog request: {str(e)}")
        return f"Error during streaming: {str(e)}"


def save_blog_post(content: str, filename: str = None) -> str:
    """Save the blog post to a file."""
    # Create the output directory if it doesn't exist
    os.makedirs(BLOG_OUTPUT_DIR, exist_ok=True)

    # Use the provided filename or default
    if not filename:
        filename = DEFAULT_FILENAME

    # Add extension if not present
    if not filename.endswith(BLOG_FILE_EXTENSION):
        filename += BLOG_FILE_EXTENSION

    # Create the full file path
    file_path = os.path.join(BLOG_OUTPUT_DIR, filename)

    # Check if file exists and make unique if needed
    counter = 1
    original_filename = filename[: -len(BLOG_FILE_EXTENSION)]
    while os.path.exists(file_path):
        filename = f"{original_filename}_{counter}{BLOG_FILE_EXTENSION}"
        file_path = os.path.join(BLOG_OUTPUT_DIR, filename)
        counter += 1

    # Save the content
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.info(f"Blog post saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving blog post: {str(e)}")
        return None


async def main():
    """Main client application function."""
    print(WELCOME_MESSAGE)

    try:
        # Verify server connection once at startup
        client, http_client = await get_a2a_client()
        await http_client.aclose()

        running = True
        while running:
            # Get the blog topic from the user
            topic = input(TOPIC_PROMPT).strip()
            if not topic:
                print("Topic cannot be empty. Please try again.")
                continue

            # Ask if they want to see the streaming process
            streaming = input(STREAMING_PROMPT).strip().lower().startswith("y")

            # Send the request to the server
            try:
                blog_content = await send_blog_request(topic, stream=streaming)

                if not streaming:
                    print("\n--- Blog Post ---\n")
                    print(blog_content)
                    print("\n--- End of Blog Post ---\n")

                # Ask if they want to save the blog post
                save_blog = input(SAVE_PROMPT).strip().lower().startswith("y")
                if save_blog:
                    filename = input(FILENAME_PROMPT).strip()
                    file_path = save_blog_post(blog_content, filename)
                    if file_path:
                        print(f"\nBlog post saved to: {file_path}\n")
                    else:
                        print("\nFailed to save the blog post.\n")

                # Ask if they want to continue writing another blog
                continue_writing = (
                    input(CONTINUE_PROMPT).strip().lower().startswith("y")
                )
                if not continue_writing:
                    running = False

            except Exception as e:
                logger.error(f"Error during blog writing process: {str(e)}")
                print(f"\nError occurred: {str(e)}\n")

                # Ask if they want to try again
                try_again = (
                    input("Would you like to try again? (y/n)\n> ")
                    .strip()
                    .lower()
                    .startswith("y")
                )
                if not try_again:
                    running = False

        print(GOODBYE_MESSAGE)

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
        print("Please check the logs for details or try again later.")


if __name__ == "__main__":
    asyncio.run(main())
