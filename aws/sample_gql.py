import json
import os.path

from uuid import uuid4
from datetime import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport
from graphql import get_introspection_query, build_client_schema
import requests
from requests_negotiate_sspi import HttpNegotiateAuth

from utility_types import JwtUtility

import pdb

def read_stored_csid_token():
    print("Reading CSID token from file...")
    token_path = './csid_token.txt'
    if not os.path.exists(token_path):
        return None

    with open(token_path, 'r', encoding='utf-8') as in_file:
        csid_token = in_file.read()

    header, payload, signature = JwtUtility.decode_jwt(csid_token)
    # print("Header:", header, "Payload:", payload, "Signature:", signature)

    expiry_dt = datetime.fromtimestamp(payload['exp'])
    if datetime.now() >= expiry_dt:
        print("CSID token has expired, retrieving a new one from the API.")
        return None

    return csid_token

def get_csid_token_from_api():
    # It is important to verify the certificate with the MLP CA
    # You can download it from https://ca.mlp.com/certData/ca-bundle.txt
    # https://wiki-pm.mlp.com/display/ISEC/Proxies%3A+Certificate
    print("Retrieving CSID token from API...")
    csid_token_url = "https://cs-identity-uat.mlp.com/api/v2.0/token?applications=CoreDataUAT"
    csid_token_response = requests.get(csid_token_url, auth=HttpNegotiateAuth(), verify="C:/Code/certs/cacerts.pem")
    csid_token_response_json = csid_token_response.json()
    csid_token = csid_token_response_json['token']
    with open('csid_token.txt', 'w', encoding='utf-8') as out_file:
        out_file.write(csid_token)
    return csid_token

# MAIN

## SETUP CSID

try:
    csid_token = read_stored_csid_token() or get_csid_token_from_api()
    if not csid_token:
        print("No CSID token found or could not retrieve it from the API.")
        print("Please ensure you have access to the CSID API and that the token is stored in 'csid_token.txt'.")
        exit(9)
except ValueError as e:
    print(f"Error: {e}")


## SETUP NETWORK PROXY

proxy_url = "http://siproxyvip.ad.mlp.com:3128"

headers = {
    "Authorization": f"Bearer {csid_token}",
    # "User-Agent": "GraphQL Client",
    # "Accept": "application/json",
    # "Content-Type": "application/graphql",
    # "x-correlation-id": str(uuid4()),   # Generate a unique correlation ID for each request
    # "x-request-id": str(uuid4()),       # Generate a unique request ID for each request
}

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(
    url="https://coredata-api.uat.mlp.com/graphql/request",
    headers=headers,
    ssl=False,
    client_session_args={"trust_env": True, "proxy": proxy_url}
)

# transport = RequestsHTTPTransport(
#     url="https://coredata-api.uat.mlp.com/graphql/request",
#     headers=headers,
#     use_json=True,
#     verify=True,
# )


def get_schema():
    print("Retrieving GraphQL schema...")
    #graphql_url = "https://security-api.mlp.com/graphql" if prod else "https://security-api.uat.mlp.com/graphql"
    graphql_url = "https://coredata-api.uat.mlp.com/graphql"

    transport = RequestsHTTPTransport(
        url=f"{graphql_url}/request",
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


def main():
    # Example for querying Positions
    client = Client(transport=transport, fetch_schema_from_transport=True)
    query = gql("""
query {
  Positions(
    page: {limit: 10}
    where: {AND: [{AND: [{portfolio: {portfolioTypeCode: {EQ: "Production"}}, account: {fundFamilyCode: {EQ: "MLP"}}, positionOpen: {EQ: "Y"}, effectiveEndTimestamp: {EQ: "2099-12-31T00:00:00Z"}, businessDate: {EQ: "2025-06-16"}}]}]}
  ) {
        select {
            source
            upstreamPositionId
            businessDate
            marketValue
            marketValueUSD
            marketPrice
            positionCurrency
            security { ric }
            account { clearingBrokerCode mainAccountCode }
        }
    }
}
    """)
    query = gql("""
{
  __schema {
    types {
      name
      kind
      fields {
        name
        type {
          name
          kind
        }
      }
    }
    queryType {
      name
    }
    mutationType {
      name
    }
    subscriptionType {
      name
    }
  }
}
    """)

    try:
        # Execute the query on the transport
        result = client.execute(query)
        print(result)
    except Exception as e:
        print(f"Error: {e}")

def bad_example_main2():
    # Meant to be an example of querying with variables; KIV
    print("Using requests to execute GraphQL query...")
    def execute_graphql_query(url, query, variables=None):

        payload = {'query': query}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            raw_json = response.text
            return raw_json
        else:
            raise Exception(f"Query failed with status code: {response.status_code}, {response.text}")

    query = """
subscription {
  Positions(
    page: {limit: 10}
    where: {AND: [{AND: [{portfolio: {portfolioTypeCode: {EQ: "Production"}}, account: {fundFamilyCode: {EQ: "MLP"}}, positionOpen: {EQ: "Y"}, effectiveEndTimestamp: {EQ: "2099-12-31T00:00:00Z"}, businessDate: {EQ: "2025-06-16"}}]}]}
  ) {
        select {
            source
            upstreamPositionId
            businessDate
            marketValue
            marketValueUSD
            marketPrice
            positionCurrency
            security { ric }
            account { clearingBrokerCode mainAccountCode }
        }
    }
}
    """
    variables = {}

    try:
        url = "https://coredata-api.uat.mlp.com/graphql/download"
        raw_response = execute_graphql_query(url, query, variables)
        print(raw_response)

        # Parse the raw JSON if needed
        parsed_response = json.loads(raw_response)
        print(parsed_response)

    except Exception as e:
        print(f"Error: {e}")

def main3():
    # Get the schema directly - no need to parse it again
    executable_schema = get_schema()
    pdb.set_trace()


if __name__ == '__main__':
    main3()