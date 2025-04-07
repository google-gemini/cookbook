# Contributing to the Gemini API Cookbook

We would love to accept your patches and contributions to the Gemini API Cookbook. We are excited that you are considering donating some of your time, and this guide will help us be respectful of that time.

# Before you send anything

## Sign our contributor agreement

All contributions to this project must be accompanied by a [Contributor License Agreement](https://cla.developers.google.com/about) (CLA). You (or your employer) retain the copyright to your contribution; this simply gives us permission to use and redistribute your contributions as part of the project.

If you or your current employer have already signed the Google CLA (even if it was for a different project), you probably don't need to do it again.

Visit [https://cla.developers.google.com/](https://cla.developers.google.com/) to see your current agreements or to sign a new one.

## Style guides

Before you start writing, take a look at the [technical writing style guide](https://developers.google.com/style). You don’t need to fully digest the whole document, but do read the [highlights](https://developers.google.com/style/highlights) so you can anticipate the most common feedback.

Also check out the relevant [style guide](https://google.github.io/styleguide/) for the language you will be using. These apply strictly to raw code files (e.g. *.py, *.js), though code fragments in documentation (such as markdown files or notebooks) tend to favor readability over strict adherence.

For Python notebooks (*.ipynb files), consider running `pyink` over your notebook. It is not required, but it will avoid style-related nits.

See bellow more detailed guidelines, some specific to writting notebooks and guides.

# Making changes

## Small fixes

Small fixes, such as typos or bug fixes, can be submitted directly via a pull request.

## Content submission

Before you send a PR, or even write a single line, please file an [issue](https://github.com/google-gemini/cookbook/issues). There we can discuss the request and provide guidance about how to structure any content you write.

Adding a new guide often involves lots of detailed reviews and we want to make sure that your idea is fully formed and has full support before you start writing anything. If you want to port an existing guide across (e.g. if you have a guide for Gemini on your own GitHub), feel free to link to it in the issue.

When you're ready, start by using the [notebook
template](./quickstarts/Template.ipynb) and following the guidance within.

Before submitting your notebook, it's recommended to run linting and formatting tools locally to ensure consistency and adherence to style guidelines.

1. Install Dependencies:

First, install the necessary packages using pip:

```bash
pip install -U tensorflow-docs
```

2. Format the Notebook:

Use the nbfmt tool from tensorflow-docs to automatically format your notebook:

```
python -m tensorflow_docs.tools.nbfmt path/to/notebook
```

Replace `path/to/notebook` with the actual path to your notebook file.

3. Lint the Notebook:

Use the nblint tool to check for style and consistency issues:

```
python -m tensorflow_docs.tools.nblint \
            --styles=google,tensorflow \
            --arg=repo:google-gemini/cookbook \
            --arg=branch:main \
            --exclude_lint=tensorflow::button_download \
            --exclude_lint=tensorflow::button_website \
            --arg=base_url:https://ai.google.dev/ \
            --exclude_lint=tensorflow::button_github \
            path/to/notebook
```

Replace `path/to/notebook` with the actual path to your notebook file.

## Things we consider

When accepting a new guide, we want to balance a few aspects.
* Originality - e.g. Is there another guide that does the same thing?
* Pedagogy - e.g. Does this guide teach something useful? Specifically for a Gemini API feature?
* Quality - e.g. Does this guide contain clear, descriptive prose? Is the code easy to understand?

It is not crucial for a submission to be strong along all of these dimensions, but the stronger the better. Old submissions may be replaced in favor of newer submissions that exceed these properties.

## Attribution
If you have authored a new guide from scratch, you are welcome to include a byline at the top of the document with your name and GitHub username.

# Detailed coding guidelines
## Notebook style

* Include the collapsed license at the top (uses the Colab "Form" mode to hide the cells).
* Use one `H1` header (`#` in Markdown) for the title.
* Include the "open in colab" button immediately after the `H1`. It should look like
  `<a target=\"_blank\" href=\"URL\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" height=30/>`
  where `URL` should be `https://colab.research.google.com/github/google-gemini/cookbook/blob/main/` followed by the notebook
  location in the cookbook
* Include an overview section before any code.
* use %pip instead of !pip
* Put the imports when they are first used.
* Keep code as brief as possible. Do not add extra options without explaining them, focus on what you want to showcase.
* Break text cells at headings
* Break code cells between "building" and "running".
* Necessary but uninteresting code (like helper functions) should be hidden in a toggleable code cell by putting `# @title`
  as the first line.

## Code style

* Notebooks are for people. Write code optimized for clarity.
* Demonstrate small parts before combining them into something more complex.
* Use the [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html), where applicable. Code formatted
  by [`pyink`](https://github.com/google/pyink) will always be accepted.
* Ideally, if you define a function, run it and show us what it does before using it in another function.
* Only use helper function when you don't have a choice. If it's only a couple of lines, it's usually better to write them
  everytime so that the readers don't have to check the function definition all the time.
* When selecting a model, use a colab selector for easier maintainability:
  `MODEL_ID="gemini-2.0-flash" # @param ["gemini-2.0-flash-lite","gemini-2.0-flash","gemini-2.5-pro-exp-03-25"] {"allow-input":true, isTemplate: true}`
* Some notebooks can also benefit from having a form to update the prompt:
  `prompt = "Detect the 2d bounding boxes of the cupcakes (with “label” as topping description”)"  # @param {type:"string"}`
  or a list of prompts they can choose from:
 `prompt = "Draw a square around the fox' shadow"  # @param ["Find the two origami animals.", "Where are the origamis' shadows?","Draw a square around the fox' shadow"] {"allow-input":true}`
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

## Comments

* **Write clear and concise comments:** Explain the "why" behind the code, not just the "what".
* **Comment sparingly:** Well-written code should be self-documenting where possible.
* **Use complete sentences:** Start comments with a capital letter and use proper punctuation.

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
