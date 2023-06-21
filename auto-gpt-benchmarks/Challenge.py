import os


class Challenge:
    """The parent class to all specific challenges classes.
    Defines helper methods for running a challenge"""

    def open_file(self, workspace: str, filename: str):
        with open(os.path.join(workspace, filename), "r") as f:
            return f.read()

    def get_filenames_in_workspace(self, workspace: str):
        return [
            filename
            for filename in os.listdir(workspace)
            if os.path.isfile(os.path.join(workspace, filename))
        ]
