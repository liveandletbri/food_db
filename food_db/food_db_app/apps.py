from django.apps import AppConfig


class FoodDbAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'food_db_app'
    
    def ready(self):
        """Run validation and other startup tasks."""
        try:
            from .views.tutorial_validation import validate_tutorial_steps
            validate_tutorial_steps()
        except ImportError:
            # If validation module doesn't exist, skip validation (shouldn't happen in production)
            pass