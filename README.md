# DINIFY BACKEND
The backend application for dinify_project.

## Getting started

## code organisation

## 
ConXXX - Controller class.
SerializerXXX - Serializer class.


# TODO
- Refactor serializer files to smaller manageable ones, probably model based files.
- Refactor to minify endpoint handler files. this may go hand in hand with the refactor to adopt Class-scoped functions.
- Refactor to adopt class implementations for the various functions. Apart from misc/controller functions, many of these functions are likely in the same files or in the same controller folders.
- Refactor to have a single file for string definitions. This may be a huge file but best to keep all string in one location.
- Refactor to have single file for definitions of non-variable dependent messages.

## Background tasks
- Determine customer who has made the order | `python manage.py determine-customers`
- Verify DPO tokens | `python manage.py verify-dpo-tokens`
- Processing Yo responses | `python manage.py process_yo_responses`
- Check transaction status with aggregator | `python manage.py check_transaction_statuses`
- Processing transactions | `python manage.py process_transactions`

/home/venv/bin/python /home/dinify_backend/manage.py determine-customers
/home/venv/bin/python /home/dinify_backend/manage.py verify-dpo-tokens

/home/scripts/determinecustomers.sh >> /home/script_logs/determine_customers/`date +\%Y-\%m-\%d`.log 2>&1

/home/scripts/verifydpotokens.sh >> /home/script_logs/verify_dpo_tokens/`date +\%Y-\%m-\%d`.log 2>&1

- createaccoutswithyo


ConXXX => Custom Controller class for a model.