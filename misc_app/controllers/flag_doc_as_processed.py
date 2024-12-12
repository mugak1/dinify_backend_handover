from bson import ObjectId
from dinify_backend.mongo_db import MONGO_DB
from misc_app.controllers.describe_time import describe_time


def flag_doc_as_processed(collection_name, doc_id: str):
    processing_time = describe_time()
    MONGO_DB[collection_name].update_one(
        {'_id': ObjectId(doc_id)},
        {
            '$set': {
                'dinify_processed': True,
                'dinify_processed_time': processing_time
            }
        }
    )
