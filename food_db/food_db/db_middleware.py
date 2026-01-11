from .db_router import set_database_for_thread


class DatabaseSelectionMiddleware:
    """
    Middleware to detect test_db query parameter and route database accordingly.
    If ?test_db=true is in the URL, routes to 'test' database, otherwise 'default'.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for test_db query parameter
        test_db = request.GET.get('test_db', '').lower()
        if test_db == 'true':
            set_database_for_thread('test')
        else:
            set_database_for_thread('default')
        
        response = self.get_response(request)
        return response

