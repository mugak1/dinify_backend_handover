"""
configurations or definitions of various values on the syste
"""


# a dictionary of the various configurations to consider
class ConfigDictionary(object):
    def __init__(self, dictionary):
        self.__dict__ = dictionary


# the roles that can be granted on the system
ROLES = {
    'DINIFY_ADMIN': 'dinify_admin',
    'RESTAURANT_MANAGER': 'restaurant_manager',
    'RESTAURANT_STAFF': 'restaurant_staff',
    'DINER': 'diner'
}

# ROLES = ConfigDictionary(roles)
