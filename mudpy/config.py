from . import wireframe

class Config(wireframe.Blueprint):
    """Maintains configurations specific to the mud mudpy is running."""
    yaml_tag = "u!config"
