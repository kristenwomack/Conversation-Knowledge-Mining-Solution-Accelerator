import asyncio
import logging


async def stream_processor(response):
    try:
        async for message in response:
            if str(message[0]): # Get remaining generated response if applicable
                await asyncio.sleep(0.1)
                yield str(message[0])
    except Exception as e:
        logging.error(f"Error processing streaming response: {e}", exc_info=True)
        raise