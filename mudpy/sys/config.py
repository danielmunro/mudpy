from . import wireframe

class Config(wireframe.Blueprint):
    """Maintains configurations specific to the mud mudpy is running."""
    yaml_tag = "u!config"

    def __str__(self):
        return self.name if 'name' in self.__dict__ else 'default'
