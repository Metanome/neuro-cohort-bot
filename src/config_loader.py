"""
Configuration loading module for the Neuro Cohort Bot.

This module handles loading and validating configuration from YAML files.
"""
import yaml
import logging
import os
from src.utils import handle_error

def load_config(file_path):
    """
    Load and validate configuration from a YAML file.
    
    Args:
        file_path (str): Path to the YAML configuration file
        
    Returns:
        dict: Parsed configuration dictionary
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the config file contains invalid YAML
    """
    # Check if file exists
    if not os.path.exists(file_path):
        logging.error(f"Config file not found: {file_path}")
        raise FileNotFoundError(f"Config file not found: {file_path}")
    
    try:
        # Load and parse the YAML file
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            
        # Basic validation
        validate_config(config)
        
        return config
        
    except yaml.YAMLError as e:
        handle_error(e, "yaml_config_parsing", with_traceback=True)
        raise

def validate_config(config):
    """
    Perform basic validation of the configuration structure.
    
    Args:
        config (dict): Configuration dictionary to validate
        
    Raises:
        ValueError: If required configuration sections are missing
    """
    # Check for required top-level sections
    required_sections = ['sources', 'telegram']
    for section in required_sections:
        if section not in config:
            logging.error(f"Missing required section '{section}' in config")
            raise ValueError(f"Missing required section '{section}' in config")
    
    # Check for required Telegram settings
    required_telegram = ['token', 'chat_id']
    for field in required_telegram:
        if field not in config['telegram']:
            logging.error(f"Missing required Telegram setting '{field}' in config")
            raise ValueError(f"Missing required Telegram setting '{field}' in config")
    
    # Validate that there's at least one source defined
    if not config['sources'] or len(config['sources']) == 0:
        logging.warning("No sources defined in config")
        
    logging.info(f"Config validated with {len(config['sources'])} sources")