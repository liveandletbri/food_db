import threading
from django.conf import settings

_thread_local = threading.local()


def set_database_for_thread(db_name):
    """Set which database should be used for the current thread."""
    _thread_local.database = db_name


def get_database_for_thread():
    """Get which database should be used for the current thread."""
    return getattr(_thread_local, 'database', 'default')


class DatabaseRouter:
    """
    A router to control all database operations.
    Routes food_db_app models to 'test' database when test_db is active, otherwise uses 'default'.
    Django system models (auth, sessions, admin, etc.) always use 'default'.
    """
    
    def db_for_read(self, model, **hints):
        """Suggest which database to read from."""
        # Only route food_db_app models based on test_db
        # Django system models always use default
        if model._meta.app_label == 'food_db_app':
            return get_database_for_thread()
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest which database to write to."""
        # Only route food_db_app models based on test_db
        # Django system models always use default
        if model._meta.app_label == 'food_db_app':
            return get_database_for_thread()
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both objects are in the same database."""
        db_set = {'default', 'test'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that migrations only run on the appropriate database."""
        # food_db_app can migrate to both databases
        if app_label == 'food_db_app':
            return True
        # Django system apps only migrate to default
        elif db == 'default':
            return True
        return None

