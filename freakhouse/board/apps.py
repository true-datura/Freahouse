from django.apps import AppConfig


class BoardConfig(AppConfig):
    name = 'freakhouse.board'
    verbose_name = "Board"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
