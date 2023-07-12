from typing import Dict, Optional

import yaml
import os


def load_config(file_name: str, relative_dir_path: Optional[str] = None) -> Dict[str, Dict[str, any]]:
	"""
	load YAML with dictionary-like structure at its root

	:param file_name: the file name for the YAML file (including its file extension)
	:param relative_dir_path: OPTIONAL the subdirectory, relative the root directory
										(if omitted, file is assumed to be in the rasa-project's root directory)
	:return: the load YAML data
	"""
	target_dir = os.path.join('..', relative_dir_path) if relative_dir_path else '..'
	response_texts_path = os.path.join(os.path.dirname(__file__), target_dir, file_name)
	with open(response_texts_path, 'r', encoding='utf-8') as file:
		return yaml.safe_load(file)

