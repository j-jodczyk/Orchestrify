import os
import zipfile
import shutil

def shorten_path_name(original_path, max_length=250):
    """
    Shortens a file path to ensure its total length does not exceed the specified maximum length.

    Args:
        original_path (str): The original file path.
        max_length (int, optional): The maximum allowed length of the path. Defaults to 250.

    Returns:
        str: The shortened file path.
    """
    path_parts = original_path.split(os.sep)

    shortened_parts = []
    total_length = 0

    for part in path_parts:
        remaining_length = max_length - total_length - len(path_parts) + len(shortened_parts)
        if len(part) > remaining_length:
            shortened_parts.append(part[:remaining_length])
        else:
            shortened_parts.append(part)
        total_length += len(shortened_parts[-1])

    return os.sep.join(shortened_parts)


def extract_and_shorten_paths(zip_file, output_dir, max_length=250):
    """
    Extracts files from a ZIP archive, shortening their paths if necessary.

    Args:
        zip_file (str): Path to the ZIP file to extract.
        output_dir (str): Directory to extract the files to.
        max_length (int, optional): Maximum allowed length for extracted file paths. Defaults to 250.

    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(zip_file, "r") as z:
        for member in z.namelist():
            original_path = member

            if original_path.endswith("/"):
                continue

            shortened_path = shorten_path_name(original_path, max_length)

            output_path = os.path.join(output_dir, shortened_path)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with z.open(member) as source, open(output_path, "wb") as target:
                shutil.copyfileobj(source, target)


if __name__ == "__main__":
    zip_file_path = "path to zip dataset"
    output_directory = "output directory for the dataset"

    extract_and_shorten_paths(zip_file_path, output_directory)
    print(f"Files extracted and paths shortened to: {output_directory}")
