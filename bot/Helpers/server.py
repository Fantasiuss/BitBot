import asyncio
from spacetimedb_sdk.spacetimedb_async_client import SpacetimeDBAsyncClient
import module_bindings

async def main():
    # Initialize client with dummy 'module_bindings' folder (we won't use generated bindings)
    client = SpacetimeDBAsyncClient(module_bindings)

    async def on_connect():
        print("Connected to STDB, subscribing to PlayerState data...")
        # Subscribe to the PlayerState table with a simple query
        client.subscribe("SELECT * FROM PlayerState", on_player_state_update)

    def on_player_state_update(data):
        print("PlayerState data update received:")
        # Data is a list of rows; just print raw JSON here
        for row in data:
            print(row)

    # Connect and start listening to PlayerState changes
    await client.run(
        auth_token="your_auth_token_here",  # Replace with your actual token
        module_url="https://bitcraft-beta-live.adokkf74uopr5hao3ww3hejuu.com/",
        module_name="bitcraft-global",
        on_connect=on_connect,
        initial_queries=["SELECT * FROM PlayerState"]
    )

if __name__ == "__main__":
    asyncio.run(main())
