import os
import sys
import requests
import zipfile
import io
import ast

def is_desired_file(file_path):
    """Check if the file is a Python, JavaScript, TypeScript, Svelte, or Rust file."""
    return file_path.endswith(".py") or file_path.endswith(".js") or file_path.endswith(".ts") or file_path.endswith(".svelte") or file_path.endswith(".rs")

def is_likely_useful_file(file_path):
    """Determine if the file is likely to be useful by excluding certain directories and specific file types."""
    excluded_dirs = ["docs", "examples", "tests", "test", "__pycache__", "scripts", "utils", "benchmarks", "node_modules", ".venv"]
    utility_or_config_files = ["hubconf.py", "setup.py", "package-lock.json"]
    github_workflow_or_docs = ["stale.py", "gen-card-", "write_model_card"]

    if any(part.startswith('.') for part in file_path.split('/')):
        return False
    if 'test' in file_path.lower():
        return False
    for excluded_dir in excluded_dirs:
        if f"/{excluded_dir}/" in file_path or file_path.startswith(
            f"{excluded_dir}/"
        ):
            return False
    for file_name in utility_or_config_files:
        if file_name in file_path:
            return False
    return all(doc_file not in file_path for doc_file in github_workflow_or_docs)

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



def download_repo(repo_url, output_file):
    """Download and process files from a GitHub repository."""
    if '/tree/' in repo_url:
        repo_url = f'https://download-directory.github.io/?{repo_url}'

    response = requests.get(f"{repo_url}/archive/master.zip")
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    with open(output_file, "w", encoding="utf-8") as outfile:
        for file_path in zip_file.namelist():
            # Skip directories, non-Python files, less likely useful files, hidden directories, and test files
            if file_path.endswith("/") or not is_desired_file(file_path) or not is_likely_useful_file(file_path):
                continue

            file_content = zip_file.read(file_path).decode("utf-8")

            # Skip test files based on content and files with insufficient substantive content
            if is_desired_file(file_content) or not has_sufficient_content(file_content):
                continue

            try:
                file_content = remove_comments_and_docstrings(file_content)
            except SyntaxError:
                # Skip files with syntax errors
                continue

            outfile.write(f"# File: {file_path}\n")
            outfile.write(file_content)
            outfile.write("\n\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <github_repo_url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    repo_name = repo_url.split("/")[-1]
    output_file = f"{repo_name}_code.txt"

    download_repo(repo_url, output_file)
    print(f"Combined source code saved to {output_file}")
