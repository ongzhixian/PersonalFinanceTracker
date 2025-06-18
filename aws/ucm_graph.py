import json

from ariadne import ObjectType, QueryType, MutationType, graphql, make_executable_schema, gql
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
    return "Hello, world!"
    # http_context = info.context["requestContext"]["http"]
    # user_agent = http_context.get("userAgent") or "Anon"
    # return f"Hello {user_agent}!"



query_type.set_field("counters", resolve_counters)

mutation_type = MutationType()
mutation_type.set_field("incrementCounter", resolve_increment_counter)


# Collate resolvers and create the final executable schema
schema = make_executable_schema(type_defs, [query_type, mutation_type, counter_type])

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
    from graphql import print_schema
    print(print_schema(schema))
    app = GraphQL(schema, debug=True)
    uvicorn.run(app, host="localhost", port=9400, reload=False)
    # uvicorn.run("ucm_graph:app", host="localhost", port=9400, reload=True)

if __name__ == '__main__':
    main()