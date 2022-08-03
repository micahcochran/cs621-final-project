# The initialization of the MongoDB is located in here and database related
# functions. 

# internal Python libraries
from typing import Dict, List
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

# there should be something like
# legal_text.books
#  
# from MongoDB command line
# db.book.insertOne({ 'collection' : 'alcons', 'title': "Alabama Constitution" });
# title with abreviation should fill in the header
# 
# Put some functions in the footer. Add a new code book.

# connect to the database -- FIXME database will need to be abstracted at some point.
# db = client.al_constitution

# get_books() 


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
    