# GitHub Repository to File Converter

This Python script allows you to download and process files from a GitHub repository, making it easier to share code with chatbots that have large context capabilities but don't automatically download code from GitHub.

## Features

- Download and process files from a GitHub repository
- Support for both public and private repositories
- Filter files based on programming language (Python, Markdown, Go, JavaScript)
- Exclude certain directories, file types, and test files
- Remove comments and docstrings from Python source code (optional)
- Specify a branch or tag to download from (default: "master")
- New GUI feature implemented in `github2file-tkinter-GUI.py`
- New `--claude` option for formatting output for Claude
- New script `ts-js-rust2file.py` for handling TypeScript, JavaScript, Svelte, and Rust files

## Install

- conda create -n g2f python=3.10
- conda activate g2f
- pip install -r requirements.txt 

## Usage

To download and process files from a public GitHub repository, run the following command:

```
python github2file.py https://github.com/username/repository
```

For a private repository, use the following format:

```
python github2file.py https://<USERNAME>:<GITHUB_ACCESS_TOKEN>@github.com/username/repository
```

Replace `<USERNAME>` with your GitHub username and `<GITHUB_ACCESS_TOKEN>` with your GitHub personal access token.

### Optional Arguments

- `--lang`: Specify the programming language of the repository. Choices: "md", "go", "javascript" or "python" (default: "python").
- `--keep-comments`: Keep comments and docstrings in the source code (only applicable for Python).
- `--branch_or_tag`: Specify the branch or tag of the repository to download (default: "master").
- `--claude`: Format the output for Claude with document tags

### Example

To download and process files from the Hugging Face Transformers repository, run:

```
python github2file.py https://github.com/huggingface/transformers
```

This will create a file named `transformers_python.txt` containing the combined Python source code from the repository.

To download and process files from a private repository, run:

```
python github2file.py https://<USERNAME>:<GITHUB_ACCESS_TOKEN>@github.com/username/private-repo
```

## Output

The script will create a file named `repository_language.txt` (e.g., `transformers_python.txt`) containing the combined source code from the specified repository. You can then share this file with chatbots like Claude for further analysis or discussion.

## GUI Usage

To use the GUI feature, run the following command:

```
python github2file-tkinter-GUI.py
```

This will open a graphical user interface where you can enter the GitHub repository URL and download the combined source code.

## New Script for TypeScript, JavaScript, Svelte, and Rust

To handle TypeScript, JavaScript, Svelte, and Rust files, use the `ts-js-rust2file.py` script. Run the following command:

```
python ts-js-rust2file.py <github_repo_url>
```

This will create a file named `<repo_name>_code.txt` containing the combined source code from the specified repository.

## Requirements

- Python 3.x
- `requests` library

## License

This project is open-source and available under the [MIT License](LICENSE).
