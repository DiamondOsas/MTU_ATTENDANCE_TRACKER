from pathlib import Path
import os
# I just fighured out this fucntion will be used a lot in exporting files in the new way so i just did it 

def _get_documents_folder() -> Path:
    """
    Attempts to find the user's "Documents" folder in Widows.
    Who tf in MTU uses Linux NOBODY not even me YET>>>.
    """
    # Windows typically stores Documents under the USERPROFILE directory.
    return Path(os.environ['USERPROFILE']) / "Documents"


def get_target_dir(level: str, type: str) -> str:
    documents_path = _get_documents_folder()
    return str(documents_path / "ATTENDANCE_MTU" / level / type)