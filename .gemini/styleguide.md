# Gemini Cookbook Python notebooks Style Guide

# Introduction
This style guide outlines the coding conventions for Python notebooks developped by the Gemini team.
It's based on PEP 8, but with some modifications to address specific needs and
preferences within our organization.

This guide is mostly about the python content and the notebook, but don't forget to also review the markdown files. In particular, any new notebook should be referenced in the corresponding readmes (at folder level at least, and potentially the one on higer levels).

# Key Principles
* **Readability:** Code should be easy to understand for all developers. Since they are notebooks and aimed at teaching
  how to use Gemini and its API/SDK, the focus should be on writting didactic and easy-to-read code while limiting the
  back and forth with the documentation or within the notebook.
* **Maintainability:** Code should be easy to modify and extend. In particular it must be easy to switch the models used.
* **Consistency:** Adhering to a consistent style across all projects improves
  collaboration and reduces errors. Similar codes (like getting the api key from the secret, initializing the client or
  selecting a model) should always be the same so it's easier for the reader to go directly to the specific content.
* **Performance:** While readability is paramount, code should be efficient.

# Cookbook notebook specific instructions

## Common mistakes

* There are multiple SDKs to use the Gemini APIs. The correct and most recent one is the [Python genai](https://github.com/googleapis/python-genai) one.
    * `%pip install -U -q 'google-genai>=1.0.0'` is the right way to install the SDK. The version indicated should reflect the minimum version needed to use the features used in the notebook (1.0.0 by default or in doubt).
    * `from google import genai` is the right way to import the official SDK.
    * `from google.genai import types` is the right way to uimport the types.
    * `import google.generativeai` is incorrect, this is the old one that was deprecated early 2025.


## Hard-coded API keys

Very important: notebooks must not contain hard-coded API keys. If you find one, immediately tell the author to cancel their submission, revoke the compromised key, and create a new one. Exposed keys are quickly collected and can lead to unauthorized usage and costs for the author.

## Notebook specificities

Most of the cookbook content is Colab notebooks, which are stored as Json.
* Only the `source` of the `cells` should be analyzed/reviewed.
* Those cells can be either Markdown or python code (or sometimes bash in which case the code cell starts with `%%bash`).
* The `outputs` do not have to be ignored, but if none of them changed while some code has, it might be a sign that the
  notebook has not been run to check that it works, in which case a warning should be raised;
* Ideally we want the ouputs to be saved in the notebooks so that one can see what the code does without runnning it. The only exception is when the ouput is tooo large (it contains images or videos for ex.).
* If the `execution_count` has changed to something else than `null`, it usually indicates that the formatting script has not
  been run. A warning should be raised, but only once per notebook. Be very clear that it means that the formatting script must be run, not that the outputs should be removed.

## Notebook style

* Include the collapsed license at the top (uses the Colab "Form" mode to hide the cells).
* Use one `H1` header (`#` in Markdown) for the title.
* Include the "open in colab" button immediately after the `H1`. It should look like
  `<a target=\"_blank\" href=\"URL\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" height=30/>`
  where `URL` should be `https://colab.research.google.com/github/google-gemini/cookbook/blob/main/` followed by the notebook
  location in the cookbook
* Include an overview section before any code.
* use `%pip` instead of `!pip`
* Put the imports when they are first used. Try to avoid having a big "import" cell at the beginning.
* Keep code as brief as possible. 
* Break text cells at headings
* Break code cells between "building" and "running".
* Necessary but uninteresting code (like helper functions) should be hidden in a toggleable code cell by putting `# @title`
  as the first line.

## Code style

* Notebooks are for people. Write code optimized for clarity.
* Use the [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html), where applicable. Code formatted
  by [`pyink`](https://github.com/google/pyink) will always be accepted.
* Ideally, if you define a function, run it and show us what it does before using it in another function.
* Demonstrate small parts before combining them into something more complex.
* Only use helper function when you don't have a choice. If it's only a couple of lines, it's usually better to write them
  everytime so that the readers don't have to check the function definition all the time.
* When selecting a model, use a colab selector for easier maintainability:
  `MODEL_ID="gemini-2.5-flash" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3-pro-preview"] {"allow-input":true, isTemplate: true}`
* Some notebooks can also benefit from having a form to update the prompt:
  `prompt = "Detect the 2d bounding boxes of the cupcakes (with “label” as topping description”)"  # @param {type:"string"}`
  or a list of prompts they can choose from:
 `prompt = "Draw a square around the fox' shadow"  # @param ["Find the two origami animals.", "Where are the origamis' shadows?","Draw a square around the fox' shadow"] {"allow-input":true}`

## Outputs

* Whenever possible simply use `print`.
* When needed use `display(Markdown())` for markdown text, `print(json.dumps(json_string, indent=4))` for Json
  or `display(Image()` for images.

## Text

* Use an imperative style. "Run a prompt using the API."
* Use sentence case in titles/headings.
* Use short titles/headings: "Download the data", "Call the API", "Process the results".
* Use the [Google developer documentation style guide](https://developers.google.com/style/highlights).
* Use [second person](https://developers.google.com/style/person): "you" rather than "we". You will fail the lint check otherwise.
* Explain what you do, the features you use, and link to existing notebooks or to the documentation for more details.

## Examples

* Keep examples quick and concise.
* Do not use extra parameters (like temperature) when not needed to keep the focus on what your notebook is illustrating.
* If you have to use extra-parameters, explain why and why the specific value the first time you do.

# Deviations from PEP 8

## Line Length

* **Maximum line length:** 100 characters (instead of PEP 8's 79).
    * Modern screens allow for wider lines, improving code readability in many cases.
    * Many common patterns in our codebase, like long strings or URLs, often exceed 79 characters.

## Indentation

* **Use 4 spaces per indentation level.** (PEP 8 recommendation)
* When a function has multiple parameters, expend it on multiple lines with proper indentation for better readability:
    ```python
    response = client.models.generate_content(
        model=MODEL_ID,
        contents="Here's my prompt",
        config={
            "response_mime_type": "application/json",
            "response_schema": Schema
        }
    )    
    ```
Notice the line break on the first and last lines.
* Long text variables should use triple double quotes and proper indentation for better readability:
    ```python
    long_prompt = """
        Cupcake ipsum dolor. Sit amet marshmallow topping cheesecake muffin.
        Halvah croissant candy canes bonbon candy. Apple pie jelly beans topping carrot cake danish tart cake cheesecake.
        Muffin danish chocolate soufflé pastry icing bonbon oat cake. Powder cake jujubes oat cake.
        Lemon drops tootsie roll marshmallow halvah carrot cake.
    """    
    ```
Notice the line break on the first and last lines.
    
## Naming Conventions

* **Variables:** Use lowercase with underscores (snake_case): `user_name`, `total_count`
* **Constants:**  Use uppercase with underscores: `MAX_VALUE`, `DATABASE_NAME`
* **Functions:** Use lowercase with underscores (snake_case): `calculate_total()`, `process_data()`
* **Classes:** Use CapWords (CamelCase): `UserManager`, `PaymentProcessor`
* **Modules:** Use lowercase with underscores (snake_case): `user_utils`, `payment_gateway`

## Docstrings

Docstrings are not mandatory, but when used they should follow those conventions:
* **Use triple double quotes (`"""Docstring goes here."""`) for all docstrings.**
* **First line:** Concise summary of the object's purpose.
* **For complex functions/classes:** Include detailed descriptions of parameters, return values,
  attributes, and exceptions.
* **Use Google style docstrings:** This helps with automated documentation generation.
    ```python
    def my_function(param1, param2):
        """Single-line summary.

        More detailed description, if necessary.

        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.

        Returns:
            bool: The return value. True for success, False otherwise.

        Raises:
            ValueError: If `param2` is invalid.
        """
        # function body here
    ```

## Type Hints

Type Hints are not mandatory, but when used they should follow those conventions:
* **Use type hints:**  Type hints improve code readability and help catch errors early.
* **Follow PEP 484:**  Use the standard type hinting syntax.

## Comments

* **Write clear and concise comments:** Explain the "why" behind the code, not just the "what".
* **Comment sparingly:** Well-written code should be self-documenting where possible.
* **Use complete sentences:** Start comments with a capital letter and use proper punctuation.
