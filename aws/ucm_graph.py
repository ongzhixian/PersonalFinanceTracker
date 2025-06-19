import asyncio
import json

from ariadne import ObjectType, QueryType, MutationType, SubscriptionType, graphql, make_executable_schema, gql

from ucm_graph_counters_resolver import resolve_counters, counter_type, resolve_increment_counter

import pdb

########################################
# Private functions

def _load_type_defs():
    with open('./ucm_graph_schema.graphql', 'r', encoding='utf-8') as in_file:
        return gql(in_file.read())

########################################
# GraphQL schema and resolvers

type_defs = _load_type_defs()

query_type = QueryType()

@query_type.field("hello")
def resolve_hello(parent, info):
    print('resolve_hello:parent', parent)
    print('resolve_hello:info', info)
    return "Hello, world from UCM!"
    # http_context = info.context["requestContext"]["http"]
    # user_agent = http_context.get("userAgent") or "Anon"
    # return f"Hello {user_agent}!"



query_type.set_field("counters", resolve_counters)

mutation_type = MutationType()
mutation_type.set_field("incrementCounter", resolve_increment_counter)



async def counter_generator(obj, info):
    for i in range(5):
        await asyncio.sleep(1)
        yield i


def counter_resolver(count, info):
    return count + 1

subscription_type = SubscriptionType()
subscription_type.set_field("beanCounter", counter_resolver)
subscription_type.set_source("beanCounter", counter_generator)


# Collate resolvers and create the final executable schema
schema = make_executable_schema(type_defs, [query_type, mutation_type, subscription_type, counter_type])

########################################
# Lambda handler

def response(body: dict, status_code: int = 200):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body),
    }

async def ucm_graphql(event: dict, context: dict):
    try:
        data = json.loads(event.get("body") or "") # Bad :-(
    except ValueError as exc:
        return response({"error": f"Failed to parse JSON: {exc}"}, 405)

    success, result = await graphql(
        schema,
        data,
        context_value=event
    )

    return response(result, 200 if success else 400)

########################################
# Main

def main():
    import uvicorn
    from ariadne.asgi import GraphQL
    # from ariadne.asgi.handlers import GraphQLWSHandler # Uses websocket protocol: subscriptions-transport-ws
    # from ariadne.asgi.handlers import GraphQLTransportWSHandler # graphql-ws
    from ariadne.contrib.sse import GraphQLHTTPSSEHandler # Server-Sent Events (SSE) handler
    from graphql import print_schema
    print(print_schema(schema))

    # graphql_app = GraphQL(schema, debug=True, websocket_handler=GraphQLWSHandler())
    graphql_app = GraphQL(schema, debug=True, http_handler=GraphQLHTTPSSEHandler())
    # Lifespan allows your application to run code when the server starts up and when it is about to shut down.
    # But it requires an ASGI lifespan manager `pip install asgi-lifespan`, which is not included in the default ASGI app.
    # from asgi_lifespan import LifespanManager
    # app = LifespanManager(graphql_app)
    # If we do not use Lifespan, we can just run the app directly and set lifespan="off" (to turn off warning messages:
    # ASGI 'lifespan' protocol appears unsupported.
    uvicorn.run(graphql_app, host="localhost", port=9400, reload=False, lifespan="off")
    # uvicorn.run("ucm_graph:app", host="localhost", port=9400, reload=True)

def starlette_main():
    pass

def fastapi_main():
    from fastapi import FastAPI
    from ariadne.asgi import GraphQL
    app = FastAPI()
    graphql_app = GraphQL(schema, debug=True)

    app.mount("/graphql", graphql_app)

if __name__ == '__main__':
    main()