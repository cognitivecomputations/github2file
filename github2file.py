import os
import sys
import requests
import zipfile
import io
import ast
import argparse
from typing import List

def get_language_extensions(language: str) -> List[str]:
    """Return a list of file extensions for the specified programming language."""
    language_extensions = {
        "python": [".py", ".pyw"],  # Add .ipynb extension for Python notebooks
        #TODO convert python notebooks to python files or some format that allow conversion between notebook and python file.
        "go": [".go"],
        "md": [".md"],  # Markdown files
    }
    return language_extensions[language.lower()]

def is_file_type(file_path: str, language: str) -> bool:
    """Check if the file has a valid extension for the specified language."""
    extensions = get_language_extensions(language)
    return any(file_path.endswith(ext) for ext in extensions)

def is_likely_useful_file(file_path, lang):
    """Determine if the file is likely useful by applying various filters."""
    excluded_dirs = ["examples", "tests", "test", "scripts", "utils", "benchmarks"]
    utility_or_config_files = []
    github_workflow_or_docs = [".github", ".gitignore", "LICENSE", "README"]

    if lang == "python":
        excluded_dirs.append("__pycache__")
        utility_or_config_files.extend(["hubconf.py", "setup.py"])
        github_workflow_or_docs.extend(["stale.py", "gen-card-", "write_model_card"])
    elif lang == "go":
        excluded_dirs.append("vendor")
        utility_or_config_files.extend(["go.mod", "go.sum", "Makefile"])

    if any(part.startswith('.') for part in file_path.split('/')):
        return False
    if 'test' in file_path.lower():
        return False
    for excluded_dir in excluded_dirs:
        if f"/{excluded_dir}/" in file_path or file_path.startswith(excluded_dir + "/"):
            return False
    for file_name in utility_or_config_files:
        if file_name in file_path:
            return False
    for doc_file in github_workflow_or_docs:
        if doc_file in file_path:
            return False
    return True

def is_test_file(file_content, lang):
    """Determine if the file content suggests it is a test file."""
    test_indicators = {
        "python": ["import unittest", "import pytest", "from unittest", "from pytest"],
        "go": ["import testing", "func Test"]
    }
    indicators = test_indicators.get(lang, [])
    return any(indicator in file_content for indicator in indicators)

def has_sufficient_content(file_content, min_line_count=10):
    """Check if the file has a minimum number of substantive lines."""
    lines = [line for line in file_content.split('\n') if line.strip() and not line.strip().startswith(('#', '//'))]
    return len(lines) >= min_line_count

def remove_comments_and_docstrings(source):
    """Remove comments and docstrings from the Python source code."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and ast.get_docstring(node):
            node.body = node.body[1:]  # Remove docstring
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            node.value.s = ""  # Remove comments
    return ast.unparse(tree)

def download_repo(repo_url, output_file, lang, keep_comments=False, branch_or_tag="master", claude=False):
    """Download and process files from a GitHub repository."""
    download_url = f"{repo_url}/archive/refs/heads/{branch_or_tag}.zip"

    print(f"Downloading from: {download_url}")
    response = requests.get(download_url)

    if response.status_code == 200:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        with open(output_file, "w", encoding="utf-8") as outfile:
            if claude and isinstance(claude, bool):
                outfile.write("Here are some documents for you to reference for your task:\n\n")
                outfile.write("<documents>\n")

            index = 1
            for file_path in zip_file.namelist():
                # Skip directories, non-language files, less likely useful files, hidden directories, and test files
                if file_path.endswith("/") or not is_file_type(file_path, lang) or not is_likely_useful_file(file_path, lang):
                    continue
                file_content = zip_file.read(file_path).decode("utf-8")

                # Skip test files based on content and files with insufficient substantive content
                if is_test_file(file_content, lang) or not has_sufficient_content(file_content):
                    continue
                if lang == "python" and not keep_comments:
                    try:
                        file_content = remove_comments_and_docstrings(file_content)
                    except SyntaxError:
                        # Skip files with syntax errors
                        continue

                if claude and isinstance(claude, bool):
                    outfile.write(f"<document index=\"{index}\">\n")
                    outfile.write(f"<source>{file_path}</source>\n")
                    outfile.write(f"<document_content>\n{file_content}\n</document_content>\n")
                    outfile.write("</document>\n\n")
                    index += 1
                else:
                    outfile.write(f"{'// ' if lang == 'go' else '# '}File: {file_path}\n")
                    outfile.write(file_content)
                    outfile.write("\n\n")

            if claude and isinstance(claude, bool):
                outfile.write("</documents>")
    else:
        print(f"Failed to download the repository. Status code: {response.status_code}")
        sys.exit(1)

def print_usage():
    print("Usage: python github2file.py <repo_url> [--lang <language>] [--keep-comments] [--branch_or_tag <branch_or_tag>] [--claude]")
    print("Options:")
    print("  <repo_url>               The URL of the GitHub repository")
    print("  --lang <language>        The programming language of the repository (choices: go, python, md). Default: python")
    print("  --keep-comments          Keep comments and docstrings in the source code (only applicable for Python)")
    print("  --branch_or_tag <branch_or_tag>  The branch or tag of the repository to download. Default: master")
    print("  --claude                 Format the output for Claude with document tags")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Repository URL is required.")
        print_usage()
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Download and process files from a GitHub repository.')
    parser.add_argument('repo_url', type=str, help='The URL of the GitHub repository')
    parser.add_argument('--lang', type=str, choices=['go', 'python', 'md'], default='python', help='The programming language of the repository')
    parser.add_argument('--keep-comments', action='store_true', help='Keep comments and docstrings in the source code (only applicable for Python)')
    parser.add_argument('--branch_or_tag', type=str, help='The branch or tag of the repository to download', default="master")
    parser.add_argument('--claude', action='store_true', help='Format the output for Claude with document tags')

    args = parser.parse_args()
    output_file_base = f"{args.repo_url.split('/')[-1]}_{args.lang}.txt"
    output_file = output_file_base if not args.claude else f"{output_file_base}-claude.txt"

    try:
        download_repo(args.repo_url, output_file, args.lang, args.keep_comments, args.branch_or_tag, args.claude)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Combined {args.lang.capitalize()} source code saved to {output_file}")