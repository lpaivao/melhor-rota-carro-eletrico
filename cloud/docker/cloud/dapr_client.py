import asyncio
import json

from dapr.clients import DaprClient


async def main():
    with DaprClient() as d:
        message = {"name": "Alice"}
        response = await d.invoke_service(
            method="on_message",
            data=json.dumps(message).encode(),
            content_type="application/json",
            service_id="server",
            timeout=5,
        )
        print(f"Received response from server: {response.decode()}")

if __name__ == "__main__":
    asyncio.run(main())
