import logging
import threading
from typing import Union
from dinify_backend.mongo_db import MONGO_DB
from misc_app.controllers.save_action_log import make_detailed_time

logger = logging.getLogger(__name__)


def save_to_mongodb(
    collection: str,
    data: dict,
    return_id=False,
    async_=False
) -> Union[bool, str]:
    """
    Save data to mongodb.

    When async_=True and return_id=False, the insert runs in a daemon thread
    (fire-and-forget) to avoid blocking the request/response cycle. The
    function returns True immediately in that case. When return_id=True the
    insert must be synchronous because the caller needs the inserted_id.
    """
    creation_time = make_detailed_time()
    data['creation_timestamp'] = creation_time

    if async_ and not return_id:
        def _write():
            try:
                MONGO_DB[collection].insert_one(data)
            except Exception as e:
                logger.error("Failed to save to MongoDB: %s", e)

        threading.Thread(target=_write, daemon=True).start()
        return True

    try:
        record = MONGO_DB[collection].insert_one(data)
        if return_id:
            return str(record.inserted_id)
        return True
    except Exception as e:
        logger.error("Failed to save to MongoDB: %s", e)
        return False

