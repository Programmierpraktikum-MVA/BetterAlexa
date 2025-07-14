#import webbrowser
import os
import subprocess

def join_zoom_meeting(meeting_link):
    """
    Öffnet den Zoom-Meeting-Link im Standardbrowser.
    """
    print(f"Öffne Zoom-Meeting: {meeting_link}")
    #webbrowser.open(meeting_link)

"""
Dieser Code funktioniert entweder nicht oder Zoom autorisiert den Bot nicht. Dieser Code darf also beim Testen ausgelassen werden.
"""
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    zoom_build_dir = os.path.join(current_dir, os.path.abspath("zoom_bot/repo_zoom_sdk/zoomBot-main/build"))

    print(current_dir)
    print(zoom_build_dir)
    # Ensure the build directory exists
    os.makedirs(zoom_build_dir, exist_ok=True)

    # Run 'cmake ..' inside the 'build' directory
    subprocess.run(['cmake', '..'], cwd=zoom_build_dir, check=True)

    # Run 'cmake --build .' inside the 'build' directory
    subprocess.run(['cmake', '--build', '.'], cwd=zoom_build_dir, check=True)

    # Run the compiled executable (adjust the name as needed)
    #subprocess.run(['./your_zoom_bot_executable'], cwd=zoom_build_dir, check=True)

def parse_link(link: str):
    parts = link.split("/")
    print(parts)
    print(parts[4])
    meeting_id, pwd = parts[4].split("?")
    print(meeting_id)
    print(pwd)
    #meeting_id = meeting_id[0:3] + ' ' + meeting_id[3:7] + ' ' + meeting_id[7:10]
    print(meeting_id)
    end = len(pwd) -2
    pwd = pwd[4:end]
    print(pwd)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    zoom_bot_dir = os.path.join(current_dir, os.path.abspath("zoom_bot/repo_zoom_sdk/zoomBot-main"))
    config_file_path = os.path.join(zoom_bot_dir, "config.txt")

    with open(config_file_path, "r") as f:
        lines = f.readlines()

    # Overwrite Meeting_number and meeting_password
    lines[0] = "meeting_number: \"" + meeting_id + "\""
    lines[3] = "meeting_password: \"" + pwd + "\""

    # Write back
    with open(config_file_path, "w") as f:
        f.writelines(lines)



if __name__ == "__main__":
    parse_link("https://tu-berlin.zoom-x.de/j/9065342855?pwd=BoO4Nn2LPfHsCgFlMsXheBYr532Di3.1")
    
