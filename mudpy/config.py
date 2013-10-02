import yaml

class Config(yaml.YAMLObject):
    """Maintains configurations specific to the mud mudpy is running."""
    yaml_tag = "u!config"
