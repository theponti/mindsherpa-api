import os

print(
    "root", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


def get_file_contents(filepath: str):
    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    abs_filepath = os.path.join(root_dir, filepath)
    print("abs_filepath", abs_filepath)
    try:
        with open(abs_filepath, "r") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: {filepath} does not exist in the {dir} folder."
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"
