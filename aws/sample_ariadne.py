from ariadne import ObjectType, QueryType, gql, make_executable_schema
from ariadne.asgi import GraphQL

type_defs = """
    type Query {
        hello: String!
        user: User
        holidays(year: Int): [String]!

    }

    type User {
        username: String!
        surname: String
        fullName: String
    }
"""


# Create type instance for Query type defined in our schema...
# query = QueryType()
query = ObjectType("Query")

# ...and assign our resolver function to its "hello" field.
@query.field("hello")
def resolve_hello(_, info):
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent

@query.field("user")
def resolve_user(_, info):
    return {"first_name": "John", "last_name": "Lennon"}

user = ObjectType("User")


@user.field("username")
def resolve_username(obj, *_):
    return f"{obj['first_name']} {obj['last_name']}"

user.set_alias("fullName", "username")

@user.field("surname")
def resolve_surname(obj, *_):
    return "OOO"


# def resolve_email_with_permission_check(obj, info):
#     if info.context["user"].is_administrator:
#         return obj.email
#     return None
#
# user.set_field("email", resolve_email_with_permission_check)


@query.field("holidays")
def resolve_holidays(*_, year=None):
    if year:
        return ["New Year's Day", "Independence Day", "Christmas"]
    return ["New Year's Day", "Independence Day", "Christmas", "Halloween", "Thanksgiving"]


schema = make_executable_schema(type_defs, [query, user])

from graphql import print_schema
print(print_schema(schema))

app = GraphQL(schema, debug=True)

# Main function

def main():
    import uvicorn
    uvicorn.run("sample_ariadne:app", host="localhost", port=9300, reload=True)

if __name__ == '__main__':
    main()