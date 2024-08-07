import whisper_timestamped as whisper #pip install -U git+https://github.com/linto-ai/whisper-timestampe
import os
import json
import time

MODELSIZE = "small"
def transcribe_audio(file_path):
    print("Called Transcribe_audio")
    now = time.time()
    audio = whisper.load_audio(file_path)
    model = whisper.load_model(MODELSIZE)
    print(f"Loading the audio and model took {time.time() - now} seconds")
    now = time.time()
    result = model.transcribe(file_path)
    print(f"Transcription took {time.time() - now} seconds")
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]

    # Create a dictionary with lecture and Timestamps
    data = {
        "lecture": filename_without_ext,
        "Timestamps": clean_transcriptions(create_segment(result))
    }

    # Get the directory of the file
    dir_path = os.path.dirname(file_path)

    # Define the path for the transcriptions.json file
    json_file_path = os.path.join(dir_path, "transcriptions.json")

    # Check if the file exists, if not create it and write the data
    if not os.path.exists(json_file_path):
        with open(json_file_path, 'w') as f:
            json.dump([data], f)  # Enclose the data in a list
    else:
    # If the file exists, append the new data
        with open(json_file_path, 'r+') as f:
            existing_data = json.load(f)
            existing_data.append(data)  # Append the new data to the list
            f.seek(0)
            json.dump(existing_data, f)



def create_segment(data):
    new_segments = []
    current_segment = ''
    segment_start = None  # Initialize the start time of the current segment
    for segment in data['segments']:
        text = segment['text']
        if segment_start is None:  # If this is the first segment in the new segment
            segment_start = segment['start']  # Set the start time of the current segment
        if len(current_segment + text) <= 400:
            current_segment += ' ' + text
        else:
            last_period_index = current_segment.rfind('.')
            if last_period_index != -1:
                new_segments.append({
                    'text': current_segment[:last_period_index + 1],
                    'start': segment_start,  # Use the start time of the current segment
                    'end': segment['end']  # Use the end time of the current segment
                })
                current_segment = current_segment[last_period_index + 2:] + ' ' + text
            else:
                new_segments.append({
                    'text': current_segment,
                    'start': segment_start,  # Use the start time of the current segment
                    'end': segment['end']  # Use the end time of the current segment
                })
                current_segment = text
            segment_start = None  # Reset the start time for the next segment
    if current_segment:
        new_segments.append({
            'text': current_segment,
            'start': segment_start,  # Use the start time of the last segment
            'end': data['segments'][-1]['end']  # Use the end time of the last segment
        })
    return new_segments
def clean_transcriptions(json_obj):
    # Define the mapping of characters
    mapping = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue'
    }

    # Check if json_obj is a list of dictionaries
    if isinstance(json_obj, list) and all(isinstance(item, dict) for item in json_obj):
        # Iterate over the items in the json object
        for item in json_obj:
            # Replace the characters in the 'text' field
            for old_char, new_char in mapping.items():
                item['text'] = item['text'].replace(old_char, new_char)
    else:
        raise ValueError("json_obj must be a list of dictionaries with a 'text' key")

    return json_obj

def clean_transcription_file(file_path):
    # Load the existing data from the file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Parse the 'Timestamps' field into a list of dictionaries
    timestamps = (data['Timestamps'])

    # Clean the transcriptions in the 'Timestamps' field
    cleaned_transcriptions = clean_transcriptions(timestamps)

    # Replace the 'Timestamps' field with the cleaned transcriptions
    data['Timestamps'] = cleaned_transcriptions

    # Write the cleaned data back to the file
    with open(file_path, 'w') as f:
        json.dump(data, f)


def transcribe_folder(folder_path, timeout=None):
    # Define the path to the download_log.json file
    # download_log_path = os.path.join(folder_path, 'download_log.json')
    download_log_path = os.path.join(folder_path, 'rerunv1.json')
    
    # Load the data from the download_log.json file
    with open(download_log_path, 'r') as f:
        data = json.load(f)

    # Convert the timeout from hours to seconds, if specified
    timeout_seconds = timeout * 60 * 60 if timeout else None

    # Get the current time
    start_time = time.time()

    # Create a list to store the items that weren't processed
    rerun_items = []

    # Iterate over the items in the data
    for item in data:
        # Define the path to the audio file
        audio_file_path = os.path.join(folder_path, item['Title'])

        # Check if the timeout has been exceeded
        if timeout_seconds and time.time() - start_time > timeout_seconds:
            # If the timeout has been exceeded, add the item to the rerun_items list
            rerun_items.append(item)
            print(f"Timeout reached. Remaining items will be added to rerun.json")
        else:
            print(f"Transcribing audio file:{item['Title']} with path: {audio_file_path}")
            # Call transcribe_audio for the audio file
            transcribe_audio(audio_file_path)
    print(f"Transcription completed total time took: {(time.time() - start_time)/(60*60)} hours")

    # If there are any items that weren't processed, write them to the rerun.json file
    if rerun_items:
        rerun_file_path = os.path.join(folder_path, 'rerun.json')
        with open(rerun_file_path, 'w') as f:
            json.dump(rerun_items, f)
def main():
    # Define the path to the audio file
    audio_file_path = 'F:\\MVA\\Video_Indexing\\AudioFiles\\Analina'
    transcribe_folder(audio_file_path,0.5)
    #transcribe_audio(r"F:\MVA\Video_Indexing\AudioFiles\Beko\Exkurs_Nichtdeterminismus_1.mp3")
if __name__ == "__main__":
    main()