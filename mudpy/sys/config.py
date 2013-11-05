from . import wireframe

class Config(wireframe.Blueprint):
    """Generic configurations file."""
    yaml_tag = "u!config"

    def __str__(self):
        return self.name if 'name' in self.__dict__ else 'default'
