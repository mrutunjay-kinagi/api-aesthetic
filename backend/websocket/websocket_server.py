import asyncio
import websockets
import json

connected_clients = set()

async def handle_client(websocket, path):
    # Register the client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast received message to all connected clients
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    finally:
        # Unregister the client
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 5002):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
