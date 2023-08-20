import os


def get_last_subdirectory(directory_path: str) -> str | None:
    # Get all subdirectories in the directory
    subdirs = [
        os.path.join(directory_path, name)
        for name in os.listdir(directory_path)
        if os.path.isdir(os.path.join(directory_path, name))
    ]

    # Sort the subdirectories by creation time
    subdirs.sort(key=os.path.getctime)

    # Return the last subdirectory in the list
    return subdirs[-1] if subdirs else None


def get_agent_report_path(path: str) -> str | None:
    latest_subdir = get_last_subdirectory(path)
    if latest_subdir is not None:
        # Look for 'report.json' in the subdirectory
        report_file = os.path.join(latest_subdir, "report.json")
        return report_file


def get_latest_report_from_agent_directories(
    directory_path: str,
) -> list[tuple[os.DirEntry[str], str]]:
    latest_reports = []

    for subdir in os.scandir(directory_path):
        if subdir.is_dir():
            # Get the most recently created subdirectory within this agent's directory
            report_file = get_agent_report_path(subdir.path)
            if report_file and os.path.isfile(report_file):
                latest_reports.append((subdir, report_file))

    return latest_reports
