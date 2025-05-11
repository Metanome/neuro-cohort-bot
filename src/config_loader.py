import yaml

# Loads the YAML config file (sources and Telegram credentials)
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
    # TODO: Add schema validation for config structure if needed