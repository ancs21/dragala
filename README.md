# dragala

Imagine an AI assistant that speaks Python, taking your natural language requests and turning them into instant, executable scripts. That's the power of dragala, an open-source command-line tool designed to supercharge your productivity and automate repetitive tasks.

### Quickstart

1. Install dragala with pip:

   ```
   pip install dragala
   ```

2. Execute a prompt and close

   ```
   dragala Just say hello
   ```

### Configuration

dragala uses `gemini-pro` model for completions. You can config API KEY by modifying `~/.dragla/config.yaml` or run the first time it asks you to input. You can get an API key from [ai.google.dev](https://ai.google.dev/).

### Development

To run dragala from source, clone the repository and install the dependencies:

```
git clone https://github.com/ancs21/dragala
cd dragala

# please install uv first
https://github.com/astral-sh/uv

# create a virtual environment
uv venv .venv -p 3.11

# activate the virtual environment
source .venv/bin/activate

uv pip install -r requirements.txt

# run dragala
dragala "Just say hello"
```


### Contributing

We welcome contributions from the community! If you have an idea for a new feature or want to report a bug, please open an issue. If you'd like to contribute code, please open a pull request.


### License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Inspiration

This project is inspired by [https://github.com/AbanteAI/rawdog](https://github.com/AbanteAI/rawdog). It's designed to be a lightweight, open-source alternative that's easy to use and extend.
