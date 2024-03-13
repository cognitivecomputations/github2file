import os
import sys
import requests
import zipfile
import io
import ast

def is_python_file(file_path):
    """Check if the file is a Python file."""
    return file_path.endswith(".py")

def is_likely_useful_file(file_path):
    """Determine if the file is likely to be useful by excluding certain directories and specific file types."""
    excluded_dirs = ["docs", "examples", "tests", "test", "__pycache__", "scripts", "utils", "benchmarks"]
    utility_or_config_files = ["hubconf.py", "setup.py"]
    github_workflow_or_docs = ["stale.py", "gen-card-", "write_model_card"]
    
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

def is_test_file(file_content):
    """Determine if the file content suggests it is a test file."""
    test_indicators = ["import unittest", "import pytest", "from unittest", "from pytest"]
    return any(indicator in file_content for indicator in test_indicators)

def has_sufficient_content(file_content, min_line_count=10):
    """Check if the file has a minimum number of substantive lines."""
    lines = [line for line in file_content.split('\n') if line.strip() and not line.strip().startswith('#')]
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

def download_repo(repo_url, output_file, branch_name='master'):
    repo_owner, repo_name = repo_url.split('/')[-2:]
    api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/zipball/{branch_name}'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for file_path in zip_file.namelist():
                if file_path.endswith('/') or (not is_likely_useful_file(file_path)):
                    continue
                try:
                    file_content = zip_file.read(file_path).decode('utf-8')
                except UnicodeDecodeError:
                    print(f"Skipping file '{file_path}' due to encoding issues.")
                    continue
                if not has_sufficient_content(file_content):
                    continue
                try:
                    file_content = remove_comments_and_docstrings(file_content)
                except SyntaxError:
                    continue
                outfile.write(f'# File: {file_path}\n')
                outfile.write(file_content)
                outfile.write('\n\n')
    else:
        print(f"Failed to download the repository. Status code: {response.status_code}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Usage: python script.py <github_repo_url> [branch_name]')
        sys.exit(1)
    
    repo_url = sys.argv[1]
    branch_name = sys.argv[2] if len(sys.argv) == 3 else 'master'
    
    repo_name = repo_url.split('/')[-1]
    output_file = f'{repo_name}_code.txt'
    
    download_repo(repo_url, output_file, branch_name)
    print(f'Combined source code saved to {output_file}')