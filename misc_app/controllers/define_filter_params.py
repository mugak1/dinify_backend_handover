"""
constructs the orm filter
"""

RESTAURANT_FILTERS = {
    'name': 'name__icontains',
    'location': 'location__icontains',
    'owner': 'owner',
    'status': 'status',
}

FILTER_DEFINITIONS = {
    'restaurants': RESTAURANT_FILTERS

}


def define_filter_params(get_params, model) -> dict:
    """
    defines the parameters to consider for the filter
    """
    filter_params = {}

    # define the filter considerations
    for key, value in get_params.items():
        # check if the length is greater than 1
        if len(value) > 1:
            filter_considerations = FILTER_DEFINITIONS.get(model)
            filter_params[
                filter_considerations[key.lower()]
            ] = value

    return filter_params
