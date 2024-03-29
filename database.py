# The initialization of the MongoDB is located in here and database related
# functions. 

# internal Python libraries
from typing import Dict, List, Optional
# external libraries
from pymongo import MongoClient



# docker
# HOST = '172.17.0.2'   # If storing MongoDB on a Docker container.
HOST = 'localhost'

client = MongoClient(HOST, 27017)

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


def get_book(collection: str) -> dict:
    return db.book.find_one({'collection' : collection})

def get_book_title(collection: str) -> str:
    return db.book.find_one({'collection' : collection})['title']