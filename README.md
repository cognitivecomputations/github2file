# GitHub Repository to File Converter

This Python script allows you to download and process files from a GitHub repository, making it easier to share code with chatbots that have large context capabilities but don't automatically download code from GitHub.

## Features

- Download and process files from a GitHub repository
- Support for both public and private repositories
- Filter files based on programming language (Python or Go)
- Exclude certain directories, file types, and test files
- Remove comments and docstrings from Python source code (optional)
- Specify a branch or tag to download from (default: "master")

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

- `--lang`: Specify the programming language of the repository. Choices: "go" or "python" (default: "python").
- `--keep-comments`: Keep comments and docstrings in the source code (only applicable for Python).
- `--branch_or_tag`: Specify the branch or tag of the repository to download (default: "master").

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

## Requirements

- Python 3.x
- `requests` library

## License

This project is open-source and available under the [MIT License](LICENSE).