"""
Module for simplify GraphQl operations
"""

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport
from graphql import get_introspection_query, build_client_schema

class CoreDataGraphQlClient(object):
    def __init__(self, environment: str = 'UAT'):
        self.target_environment = environment.upper()
        if self.target_environment not in ['UAT', 'PRODUCTION']:
            raise ValueError("Invalid environment specified. Use 'UAT' or 'PRODUCTION'.")
        self.graphql_url = "https://coredata-api.uat.mlp.com/graphql"  if environment == 'UAT' else "https://coredata-api.mlp.com/graphql"
        self.event_api_url = "https://coredata-uat.mlp.com/api"  if environment == 'UAT' else "https://coredata.mlp.com/api"

    def get_schema(self, csid_token: str):
        print("Retrieving GraphQL schema...")
        transport = RequestsHTTPTransport(
            url=f"{self.graphql_url}/request",
            headers={"Authorization": f"Bearer {csid_token}"},
            use_json=True,
            verify=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        introspection_query = get_introspection_query(descriptions=True, directive_is_repeatable=True, schema_description=True)

        print("Executing introspection query to retrieve schema...")
        result = client.execute(gql(introspection_query))

        print("Building client schema from introspection result...")
        schema = build_client_schema(result)

        print("Schema retrieval complete.")
        return schema

    async def query(self, query: str, csid_token: str):
        """
        Execute a GraphQL query.
        :param query: The GraphQL query string.
        :param csid_token: The CSID token for authentication.
        :return: The result of the query.
        """
        transport = AIOHTTPTransport(
            url=f"{self.graphql_url}/request",
            headers={"Authorization": f"Bearer {csid_token}"},
            ssl=False,
            client_session_args={"trust_env": True}
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        gql_query = gql(query)
        return await client.execute_async(gql_query)
        #return client.execute(gql_query)