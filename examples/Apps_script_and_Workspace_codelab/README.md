# Gemini API and Google Workspace Codelab

These are the final, accompanying files for the [Automate Google Workspace tasks with the Gemini API
](https://codelabs.developers.google.com/codelabs/gemini-workspace) codelab. This codelabs shows you how to
connect to the Gemini API using Apps Script, and uses the function calling, vision and text capabilities to automate
Google Workspace tasks - summarising a document, analyzing a chart, sending an email and generating some slides directly. All of this is done from a free text input.

Please read and follow along with the main codelab, and if you get stuck you can load these files directly.

This workshop was featured at [Google I/O 2024](https://io.google/2024/).

## Using `google.golang.org/genai` in Apps Script

To use `google.golang.org/genai` in your Apps Script project, follow these steps:

1. Open your Apps Script project.
2. Click on the `+` button to add a new library.
3. In the "Script ID" field, enter the following ID: `google.golang.org/genai`.
4. Click "Add" to add the library to your project.
5. You can now use the `google.golang.org/genai` library in your Apps Script code.

## Project Structure

```
mpl_project/       # (Or any top-level name you prefer)
├── src/
│   ├── lexer.h
│   ├── lexer.cpp
│   ├── ast.h
│   ├── ast.cpp
│   ├── parser.h
│   ├── parser.cpp
│   ├── interpreter.h
│   ├── interpreter.cpp
│   ├── mpl_vm.h      # (Optional, for later)
│   └── mpl_vm.cpp    # (Optional, for later)
├── examples/
│   └── example.mpl  # Example MPL programs
├── tests/          # Unit tests (using Catch2 or similar)
│   ├── test_lexer.cpp
│   ├── test_parser.cpp
│   └── test_interpreter.cpp
├── build/         # Compiled files (can be ignored by Git)
├── CMakeLists.txt # (Or Makefile)
└── README.md
```
