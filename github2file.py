import os
import requests
import zipfile
import io

def download_repo(repo_url, output_file):
    # Download the repository as a ZIP file
    response = requests.get(repo_url + "/archive/master.zip")
    
    # Extract the ZIP file in memory
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    
    # Get the name of the root directory in the ZIP file
    root_dir = zip_file.namelist()[0]
    
    # Open the output file for writing
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Iterate over the files in the ZIP file
        for file_path in zip_file.namelist():
            # Skip directories and non-source files
            if file_path.endswith("/") or not file_path.endswith((".py", ".java", ".c", ".cpp", ".h", ".js", ".html", ".css")):
                continue
            
            # Extract the file content
            file_content = zip_file.read(file_path).decode("utf-8")
            
            # Write the file path and content to the output file
            outfile.write(f"// File: {file_path[len(root_dir):]}\n")
            outfile.write(file_content)
            outfile.write("\n\n")

# Example usage
repo_url = "https://github.com/username/repo"
output_file = "combined_source.txt"

download_repo(repo_url, output_file)
print(f"Combined source code saved to {output_file}")
