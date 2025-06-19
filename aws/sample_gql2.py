from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

proxy_url = "http://siproxyvip.ad.mlp.com:3128"

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(
    ssl=False,
    url="https://countries.trevorblades.com/",
    client_session_args={"trust_env": True, "proxy": proxy_url}
)

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(
    """
    query getContinents {
      continents {
        code
        name
      }
    }
"""
)

# Execute the query on the transport
result = client.execute(query)
print(result)