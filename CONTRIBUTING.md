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

See below for more detailed guidelines specific to writing notebooks and guides.

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

# Detailed Coding and Notebook Guidelines
## Notebook Style

* Include the collapsed license at the top (uses the Colab "Form" mode to hide the cells).
* Save the notebook with the table of contents open.
* Use one `H1` header (`#` in Markdown) for the title.
* Include the "Open in Colab" button immediately after the `H1`. It should look like:
    ```html
    <a target="_blank" href="URL"><img src="[https://colab.research.google.com/assets/colab-badge.svg](https://colab.research.google.com/assets/colab-badge.svg)" height=30/></a>
    ```
    where `URL` should be `https://colab.research.google.com/github/google-gemini/cookbook/blob/main/` followed by the notebook location in the cookbook.
* Include an overview section before any code.
* Put all your installs (using `%pip` instead of `!pip`) and imports in a dedicated setup section near the beginning.
* Keep code and text cells as brief as possible.
* Break text cells at headings.
* Break code cells between distinct logical steps, such as "building" and "running", or between processing/printing different results.
* Necessary but uninteresting code (like helper functions) should be hidden in a toggleable code cell by putting `# @title` as the first line.

## Code Style

* Notebooks are for people. Write code optimized for clarity.
* Use the [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html), where applicable. Code formatted by [`pyink`](https://github.com/google/pyink) will always be accepted.
* **Use 4 spaces per indentation level.** (PEP 8 recommendation)
* In particular, defining functions and variables takes extra spaces around the `=` sign, while function parameters don't:
    ```python
    var = value

    function(
        parameter=value
    )
    ```
* When a function has multiple parameters, expand it onto multiple lines with proper indentation for better readability:
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
    *Notice the line break after the opening parenthesis and before the closing parenthesis.*
* Long text variables should use triple double quotes and proper indentation for better readability:
    ```python
    long_prompt = """
        Cupcake ipsum dolor. Sit amet marshmallow topping cheesecake muffin.
        Halvah croissant candy canes bonbon candy. Apple pie jelly beans topping carrot cake danish tart cake cheesecake.
        Muffin danish chocolate soufflé pastry icing bonbon oat cake. Powder cake jujubes oat cake.
        Lemon drops tootsie roll marshmallow halvah carrot cake.
    """
    ```
    *Notice the line break after the opening triple quotes and before the closing triple quotes.*
* Demonstrate small parts before combining them into something more complex.
* If you define a function, ideally run it and show its output immediately before using it in another function or a more complex block.
* Only use helper functions when necessary (e.g., for code reuse or complexity management). If a piece of logic is only a couple of lines and used once, it's often clearer to write it inline so readers don't have to look up the function definition. Hide helper function definitions using `# @title`.
* Keep examples quick and concise. Do not add extra options or parameters (like `temperature`) without explaining them; focus on what you want to showcase.
* If you *must* use extra parameters, explain *why* they are needed and the reasoning behind the specific value the first time you use them.
* When selecting a model, use a Colab form selector for easier maintainability:
    ```python
    MODEL_ID="gemini-1.5-flash" # @param ["gemini-1.0-pro", "gemini-1.5-flash", "gemini-1.5-pro"] {"allow-input":true, isTemplate: true}
    ```
* Some notebooks can benefit from having a form to update the prompt:
    ```python
    prompt = "Detect the 2d bounding boxes of the cupcakes (with 'label' as topping description')"  # @param {type:"string"}
    ```
    or a list of prompts:
    ```python
    prompt = "Draw a square around the fox' shadow"  # @param ["Find the two origami animals.", "Where are the origamis' shadows?","Draw a square around the fox' shadow"] {"allow-input":true}
    ```
* To ensure notebook text remains accurate, present model metadata (like context window size) by executing code, not by hardcoding it in Markdown.
    * Example: Instead of writing "This model has a 1M token context window", display the output of `genai.get_model('models/gemini-1.5-pro-latest').input_token_limit`.

## Naming Conventions

* **Variables:** Use lowercase with underscores (snake\_case): `user_name`, `total_count`
* **Constants:** Use uppercase with underscores: `MAX_VALUE`, `DATABASE_NAME`
* **Functions:** Use lowercase with underscores (snake\_case): `calculate_total()`, `process_data()`
* **Classes:** Use CapWords (CamelCase): `UserManager`, `PaymentProcessor`
* **Modules:** Use lowercase with underscores (snake\_case): `user_utils`, `payment_gateway`

## Comments

* Write clear and concise comments: Explain the "why" behind the code, not just the "what".
* Comment sparingly: Well-written code should be self-documenting where possible.
* Use complete sentences: Start comments with a capital letter and use proper punctuation.

## Outputs

* Whenever possible, simply use `print()` for basic output.
* When needed, use `display(Markdown())` for formatted Markdown text, `print(json.dumps(json_string, indent=4))` for readable JSON, or `display(Image())` for images.

## Text

* Use an imperative style: "Run a prompt using the API."
* Use sentence case in titles/headings: "Download the data", "Call the API", "Process the results".
* Use short titles/headings.
* Use the [Google developer documentation style guide](https://developers.google.com/style/highlights).
* Use [second person](https://developers.google.com/style/person): "you" rather than "we". (You will fail the lint check otherwise).
* Explain what you are doing and the features you are using. Link to relevant documentation or other notebooks for more details where appropriate.

## GitHub Workflow

* Be consistent about how you save your notebooks (e.g., with ToC open, potentially omitting outputs) to keep JSON diffs manageable. Tools like [`nbfmt` and `nblint`](https://github.com/tensorflow/docs/blob/master/tools/tensorflow_docs/tools/README.md) can help enforce consistency.
* Consider setting the "Omit code cell output when saving this notebook" option if outputs (like inline images) make diffs too large for GitHub.
* [ReviewNB.com](http://reviewnb.com) can assist with reviewing notebook diffs in pull requests.
* Use the [Open in Colab](https://chrome.google.com/webstore/detail/open-in-colab/iogfkhleblhcpcekbiedikdehleodpjo) browser extension to easily open GitHub notebooks in Colab.
* The easiest way to edit a notebook tracked in GitHub is often:
    1.  Open the notebook in Colab directly from the GitHub branch you intend to edit.
    2.  Make your changes in Colab.
    3.  Use Colab's "File" -> "Save a copy in GitHub" menu option to save it back to the same branch.
* For Pull Requests (PRs), it's helpful to include a direct Colab link to the notebook version in the PR head for easier review: `https://colab.research.google.com/github/{USER}/{REPO}/blob/{BRANCH}/{PATH}.ipynb`
