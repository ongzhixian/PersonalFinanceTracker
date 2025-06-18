from ariadne import ObjectType

from shared_counter import CounterRepository

import pdb

def resolve_counters(parent, info, id=None):
    # print('resolve_counters:parent', parent)
    # print('resolve_counters:info', info)
    # print('resolve_counters:id', id)
    counter_repository = CounterRepository()
    #operation_result_message = counter_repository.get_counter_name_list()
    if id is None:
        operation_result_message = counter_repository.get_all_counters()
        if operation_result_message.is_success and operation_result_message.data_object is not None:
            return operation_result_message.data_object
    else:
        operation_result_message = counter_repository.get_counter(id)
        if operation_result_message.is_success and operation_result_message.data_object is not None:
            return [operation_result_message.data_object]
    return []



def resolve_increment_counter(_, info, id:str):
    print('resolve_increment_counter:info', info, 'id:', id)
    counter_repository = CounterRepository()
    counter_repository.add_to_counter(id, 1)
    return True
    # request = info.context["request"]
    # user = auth.authenticate(username, password)
    # if user:
    #     auth.login(request, user)
    #     return {"status": True, "user": user}
    # return {"status": False, "error": "Invalid username or password"}

########################################
# GraphQL schema and resolvers for Counter

def resolve_counter_id(obj, info):
    print('resolve_counter_id:parent', obj)
    print('resolve_counter_id:info', info)
    return obj[info.field_name]

def resolve_counter_field(obj, info):
    print('resolve_counter_field:parent', obj)
    print('resolve_counter_field:info', info)
    return obj[info.field_name]

counter_type = ObjectType("Counter")
counter_type.set_field("id", resolve_counter_id)
counter_type.set_field("description", resolve_counter_field)
counter_type.set_field("value", resolve_counter_field)