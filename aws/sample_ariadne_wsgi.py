from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from . import type_defs, resolvers

schema = make_executable_schema(type_defs, resolvers)
app = GraphQL(schema)