'''SOME MODULE-LEVEL DOCS SPEC'''
import json

def dump_event_context(event, context):
    ''' Read an item by ID.
    Args:
        item_id (int): The ID of the item to retrieve.
        q (str, optional): An optional query parameter.
    Returns:
        dict: A dictionary containing the item details.
    '''
    
    print("[event]")
    print(event)
    print("[context]")
    print(context)
    return {
        'statusCode': 200,
        'body': json.dumps('Return from Lambda 2')
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2: 
        print(sys.argv)
        print (len(sys.argv))
        raise Exception('Too little arguments')
    print(globals()[sys.argv[1]].__doc__)