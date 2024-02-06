import datetime
import os
import platform
from pathlib import Path

import google.generativeai as genai

from dragala.utils import get_gemini_api_key, parse_script, set_gemini_api_key

script_prompt = """\
You are a command-line coding assistant called dragala that generates and auto-executes Python scripts.

A typical interaction goes like this:
1. The user gives you a natural language.
2. You:
    i. Determine what needs to be done
    ii. Write a short Python SCRIPT to do it 
    iii. Communicate back to the user by printing to the console in that SCRIPT
3. The compiler checks your SCRIPT using ast.parse() then runs it using exec()

Please follow these conventions carefully:
- Decline any tasks that seem dangerous, irreversible, or that you don't understand.
- Always review the full conversation prior to answering and maintain continuity.
- If asked for information, just print the information clearly and concisely.
- If asked to do something, print a concise summary of what you've done as confirmation.
- If asked a question, respond in a friendly, conversational way. Use programmatically-generated and natural language responses as appropriate.
- If you need clarification, return a SCRIPT that prints your question. In the next interaction, continue based on the user's response.
- Assume the user would like something concise. For example rather than printing a massive table, filter or summarize it to what's likely of interest.
- Actively clean up any temporary processes or files you use.
- When looking through files, use git as available to skip files, and skip hidden files (.env, .git, etc) by default.
- You can plot anything with matplotlib.
- ALWAYS Return your SCRIPT inside of a single pair of ``` delimiters. Only the console output of the first such SCRIPT is visible to the user, so make sure that it's complete and don't bother returning anything else.

Today's date is {date}.
The current working directory is {cwd}, which {is_git} a git repository.
The user's operating system is {os}
""".format(
    date=datetime.date.today().isoformat(),
    cwd=Path.cwd(),
    os=platform.system(),
    is_git="IS" if Path(".git").exists() else "is NOT",
)


class LLMClient:
    def __init__(self):
        self.api_key = get_gemini_api_key() or os.environ.get("GOOGLE_API_KEY")
        while self.api_key is None:
            print(f"GOOGLE_API_KEY ({self.api_key}) not found. ")
            self.api_key = input("Enter API Key: ").strip()
            set_gemini_api_key(self.api_key)

        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
            },
        ]
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        )

    def get_response(
        self,
        message: str,
    ) -> str:
        try:
            response = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [script_prompt],
                    },
                    {
                        "role": "model",
                        "parts": [
                            '```python\nprint("OK. I\'m dragala, a command-line coding assistant that generates and auto-executes Python scripts.")\nprint("You can check my work with the ast module, but you can also just ask me for a summary.")\nprint("Let\'s get started!")\nCONTINUE\n```'
                        ],
                    },
                    {
                        "role": "user",
                        "parts": [
                            'EXAMPLES:\\nPROMPT: Kill the process running on port 3000\\n\\nSCRIPT: \\n```\\nimport os\\ntry:\\n    os.system("kill $(lsof -t -i:3000)")\\n    print("Process killed")\\nexcept Exception as e:\\n    print("Error:", e)\\n```\\n-------------------------------------------------------------------------------\\nPROMPT: Rename the photos in this directory with "nyc" and their timestamp\\n\\nSCRIPT: \\n```\\nimport os\\nimport time\\ntry:\\n    image_files = [f for f in os.listdir(\\\'.\\\') if f.lower().endswith((\\\'.png\\\', \\\'.jpg\\\', \\\'.jpeg\\\'))]\\n    def get_name(f):\\n        timestamp = time.strftime(\\\'%Y%m%d_%H%M%S\\\', time.localtime(os.path.getmtime(f)))\\n        return f"nyc_{timestamp}{os.path.splitext(f)[1]}"\\n    [os.rename(f, get_name(f)) for f in image_files]\\n    print("Renamed files")\\nexcept Exception as e:\\n    print("Error:", e)\\n```\\n-------------------------------------------------------------------------------\\nPROMPT: Summarize my essay, "Essay 2021-09-01.txt"\\n\\nSCRIPT: \\n```\\nwith open("Essay 2021-09-01.txt", "r") as f:\\n    print(f.read())\\nprint("CONTINUE")\\n```\\n\\nLAST SCRIPT OUTPUT:\\nJohn Smith\\nEssay 2021-09-01\\n...\\n\\nSCRIPT:\\n```\\nprint("The essay is about...")\\n```\\n-------------------------------------------------------------------------------\\n'
                        ],
                    },
                    {
                        "role": "model",
                        "parts": [
                            '```python\nprint("Got it! I\'ll help you with that.")\n```'
                        ],
                    },
                    {"role": "user", "parts": ["show me file"]},
                    {
                        "role": "model",
                        "parts": [
                            '```python\ndef print_file(filename):\n    """Prints the contents of a file to the console."""\n    try:\n        with open(filename, "r") as f:\n            print(f.read())\n    except FileNotFoundError:\n        print("File not found.")\n    except Exception as e:\n        print("Error:", e)\n\nprint_file("file.txt")\n```'
                        ],
                    },
                ]
            )

            response.send_message(message)
            text = response.last.text

            return text
        except Exception as e:
            print(f"Error:\n", str(e))

    def get_script(self, prompt: str):
        response = self.get_response(prompt)
        return parse_script(response)
