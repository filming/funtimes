import os


def get_extension_paths() -> list[str]:
	"""Recursively get all the extension paths."""

	extension_paths = []
	blacklisted_dirs_files = {"__pycache__", "__init__.py"}
	base_cog_path = os.path.join(".", "cogs")

	def recursively_collect_paths(curr_path: str) -> None:
		for unknown in os.listdir(curr_path):
			if unknown not in blacklisted_dirs_files:
				full_path = os.path.join(curr_path, unknown)
				if os.path.isfile(full_path):
					if full_path.endswith(".py"):
						# Formatting path into a dot-separated path
						extension_paths.append(full_path[2:-3].replace(os.sep, "."))
				else:
					recursively_collect_paths(full_path)

	recursively_collect_paths(base_cog_path)

	return extension_paths
