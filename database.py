# The initialization of the MongoDB is located in here and database related
# functions. 

# internal Python libraries
from typing import Dict, List, Optional
# external libraries
from pymongo import MongoClient



# docker
# HOST = '172.17.0.2'
HOST = 'localhost'

client = MongoClient(HOST, 27017)

# these are the database collections of the different legal codes
# TODO: this should be configurable from mongodb
# db_collection = {'alcons': client.al_constitution }

db = client.legal_text


def get_books() -> List[Dict]:
    """ this returns a dictionary like so
    [{ 'collection' : 'alcons', 'title': "Alabama Constitution" }]
    
    collection is the name of the collection, title is the legal book's title.
    """
    return list(db.book.find())

def has_book(book: str) -> bool:
    """Is there a legal book (collection) with this name?"""
    return db.book.find_one({'collection': book}) is not None

def add_book(collection: str, title: str) -> bool:
    """add a book"""
    # Ensure 1. there are names for the collection and title
    #        2. The collection name doesn't already exist
    #        3. There isn't a document in the book collection with this collection attribute.
    # print(f"collection {collection}")
    # print(f"title {title}")
    # print(f"collection not in db.list_collections(): {collection not in db.list_collections()}")
    # _ot_evaluate = db.book.find_one({'collection': collection}) is not None
    # print(f"db.book.find_one...is not None: {_ot_evaluate}")
    # _ot_res = db.book.find_one({'collection': collection})
    # print(f'db.book.find_one: {_ot_res}')
    if collection and title \
       and collection not in db.list_collections() \
       and db.book.find_one({'collection': collection}) is None:
        
        db.create_collection(collection)
        doc = {'collection': collection, 'title': title}
        db.book.insert_one(doc)
        return True
    return False

def set_book_editable(collection: str):
    if has_book(collection):
        # ASSUMPTION:  That this will only result in one record.
        result = db.book.find_one({'collection' : collection})
        edit_status = result.get('editable', False)
#        update_result = result
#        if not editable:
#            update_result['editable'] = True
#        else:
#            update_result['editable'] = False
#        db.book.update_one({'collection' : collection}, update_result)
        db.book.update_one({'collection' : collection}, 
                            {'$set' : {'editable' : not edit_status}})
 
        print('ran set_book_editable()')


def is_book_editable(collection: str) -> Optional[bool]:
    """return True/False for editable and None if there is no such collection."""
    if not has_book(collection):
        return None
    
    result = db.book.find_one({'collection' : collection})
    return result.get('editable', False)


def delete_book(collection: str):
    if has_book(collection):
        db.book.delete_one({'collection' : collection})
