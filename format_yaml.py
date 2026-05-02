import os
from ruamel.yaml import YAML

yaml = YAML()
yaml.explicit_start = True
yaml.indent(mapping=2, sequence=4, offset=2)

IGNORE_DIRS = {".github", ".git", "__pycache__"}

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

    for name in files:
        if name.endswith((".yml", ".yaml")):
            path = os.path.join(root, name)

            try:
                with open(path, "r") as f:
                    data = yaml.load(f)

                if data is None:
                    continue

                with open(path, "w") as f:
                    yaml.dump(data, f)

                print(f"Formatted: {path}")

            except Exception as e:
                print(f"Skipped {path}: {e}")
