import yaml

def read_yaml_path(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

