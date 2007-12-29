# Context processors for Helios.

import settings

def base_url(request): 
    """ 
    Adds the base url context variable to the context. 
 
    """ 
    return {'BASE_URL': settings.BASE_URL} 

