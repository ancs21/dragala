import argparse
import io
from contextlib import redirect_stdout

from dragala.llm import LLMClient

llm_client = LLMClient()


def dragala(prompt: str):
    error, script, output = "", "", ""
    try:
        response, script = llm_client.get_script(prompt)
        if script:
            with redirect_stdout(io.StringIO()) as f:
                exec(script, globals())
            output = f.getvalue()
            print(output)
        else:
            print("No script generated")
            print(response)
    except KeyboardInterrupt:
        error = "Execution interrupted"
        raise error
    except Exception as e:
        error = f"Error: {e}"
        raise error


def main():
    parser = argparse.ArgumentParser(
        description="Dragala: A command-line coding assistant that generates and auto-executes Python scripts"
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="A natural language prompt for the assistant to respond to",
    )

    args = parser.parse_args()

    if len(args.prompt) > 0:
        dragala(" ".join(args.prompt))
