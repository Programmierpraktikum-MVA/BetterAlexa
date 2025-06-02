import webbrowser

def join_zoom_meeting(meeting_link):
    """
    Öffnet den Zoom-Meeting-Link im Standardbrowser.
    """
    print(f"Öffne Zoom-Meeting: {meeting_link}")
    webbrowser.open(meeting_link)
