import ast
import json
from pathlib import Path

import yaml

def parse_script(response: str) -> tuple[str, str]:
    """Split the response into a message and a script.

    Expected use is: run the script if there is one, otherwise print the message.
    """
    # Parse delimiter
    n_delimiters = response.count("```")
    if n_delimiters < 2:
        return f"Error: No script found in response:\n{response}", ""
    segments = response.split("```")
    message = f"{segments[0]}\n{segments[-1]}"
    script = "```".join(segments[1:-1]).strip()  # Leave 'inner' delimiters alone

    # Check for common mistakes
    if script.split("\n")[0].startswith("python"):
        script = "\n".join(script.split("\n")[1:])
    try:  # Make sure it isn't json
        script = json.loads(script)
    except Exception as e:
        pass
    try:  # Make sure it's valid python
        ast.parse(script)
    except SyntaxError as e:
        return f"Script contains invalid Python:\n{response}", ""
    return response, script



dragala_dir = Path.home() / ".dragala"
dragala_dir.mkdir(exist_ok=True)
config_path = dragala_dir / "config.yaml"


def load_config():
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    else:
        return {}


def save_config(config):
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)


def get_gemini_api_key():
    config = load_config()
    return config.get("GOOGLE_API_KEY")


def set_gemini_api_key(api_key: str):
    config = load_config()
    config["GOOGLE_API_KEY"] = api_key
    save_config(config)
