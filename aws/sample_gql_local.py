"""
Sample GraphQL client using the gql library with both HTTP and WebSocket transports.
"""
from os import environ
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport
from gql.transport.requests import RequestsHTTPTransport
# This is only available in the gql library development version, not in the stable release.
# from gql.transport.router import RouterTransport
# SETUP

## Set up the proxy URL if needed, based on the environment variable USERDNSDOMAIN

proxy_url = "http://siproxyvip.ad.mlp.com:3128" if environ.get('USERDNSDOMAIN') == 'AD.MLP.COM' else None
proxy_url = None

## Setup transport with the GraphQL endpoint

headers = {
    # "Authorization": f"Bearer {csid_token}",
    # "User-Agent": "GraphQL Client",
    # "Accept": "application/json",
    # "Content-Type": "application/graphql",
    # "x-correlation-id": str(uuid4()),   # Generate a unique correlation ID for each request
    # "x-request-id": str(uuid4()),       # Generate a unique request ID for each request
}

use_async_transport = True  # Set to True for AIOHTTPTransport, False for RequestsHTTPTransport
graph_ql_url="http://localhost:9400"

if use_async_transport:
    # Asynchronous transport using AIOHTTPTransport
    http_transport = AIOHTTPTransport(
        url=graph_ql_url,
        headers=headers,
        ssl=False,
        client_session_args={"trust_env": True, "proxy": proxy_url}
    )
else:
    # Synchronous transport using RequestsHTTPTransport
    http_transport = RequestsHTTPTransport(
        url=graph_ql_url,
        headers=headers,
        use_json=True,
        verify=True,
    )

# WebSocket transport for subscriptions
websocket_transport = WebsocketsTransport(url="ws://localhost:9400")

# Router transport to switch between HTTP and WebSocket based on the operation type
# Unforunately, RouterTransport is not available in the stable version of gql library.
# router_transport = RouterTransport(
#     http_transport=http_transport,
#     websocket_transport=websocket_transport
# )


# Create a GraphQL client using the defined transport
# If using RouterTransport, uncomment the next line and comment out the client creation below.
# However, since RouterTransport is not available in the stable version, we will use http_transport directly.
# client = Client(transport=router_transport, fetch_schema_from_transport=True)

# Default client using the HTTP transport for queries and mutations
client = Client(transport=http_transport, fetch_schema_from_transport=True)

# Main -- examples of how to use the client

def main():
    # Provide a GraphQL query
    query = gql(
        """
        query getHello {
          hello
        }
    """
    )

    # Execute the query on the transport
    result = client.execute(query)
    print(result)


def main_hello_example():
    # Demonstration of a simple GraphQL query
    query = gql(
        """
        query getHello {
          hello
        }
    """
    )
    try:
        result = client.execute(query)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")

async def http_main():
    """Asynchronous example using AIOHTTPTransport for HTTP requests."""
    http_transport = AIOHTTPTransport(url="http://localhost:9400")
    async with Client(transport=http_transport, fetch_schema_from_transport=True) as session:
        query = gql("query { hello }")
        result = await session.execute(query)
        print("Query result:", result)

async def ws_main():
    """Asynchronous example using WebsocketsTransport for subscriptions."""
    # Set up the WebSocket transport
    transport = WebsocketsTransport(url="ws://localhost:9400")

    # Create the client
    async with Client(transport=transport, fetch_schema_from_transport=True) as session:
        # Define the subscription
        subscription = gql("""
            subscription {
                beanCounter
            }
        """)

        # Execute the subscription and listen for results
        async for result in session.subscribe(subscription):
            print("Received:", result)


def sse_main():
    """Example using Server-Sent Events (SSE) for subscriptions."""
    subscription_query = """
    subscription {
      beanCounter
    }
    """
    payload = {
        "query": subscription_query,
        "variables": {},
        "operationName": None
    }
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }
    import requests
    import json
    url = "http://localhost:9400"
    with requests.post(url, headers=headers, data=json.dumps(payload), stream=True) as resp:
        lines = resp.iter_lines()
        event = {}
        data_lines = []
        for line in lines:
            line = line.decode("utf-8").strip()
            #print(line)
            if line.startswith("data:"):
                data_lines.append(line[5:].lstrip())
            elif line.startswith("event:"):
                event['event'] = line[6:].lstrip()
        # for event in parse_sse(lines):
        #     print("Received event:")
        #     print(event)
        #     # Optionally parse JSON data
        #     if 'data' in event:
        #         try:
        #             data = json.loads(event['data'])
        #             print("Parsed data:", data)
        #         except Exception as e:
        #             print("Failed to parse JSON:", e)

if __name__ == "__main__":
    sse_main()
    #main_hello_example()
    # main()

    # Async examples
    import asyncio
    # asyncio.run(http_main())
    # asyncio.run(ws_main())