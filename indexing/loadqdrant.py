from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
import json
import os
import time
from deep_translator import GoogleTranslator
import langdetect



# encoder = None
encoder = SentenceTransformer("all-MiniLM-L6-v2")
# client = None
client = QdrantClient(url="http://localhost:6333")

# Code below vectorizes the transcriptions and saves them as JSONs
def create_vector_json(folder_path, course):
    big_dict = []
    with open(os.path.join(folder_path, "download_log.json"), 'r') as f:
        download_log_data = json.load(f)
    
    for item in download_log_data:
        title = item['Title']
        website = item['Website']
        
        # Compare the first 5 characters of the title with the course variable
        if title[:5] == course:
            # Create a directory named after the first 5 characters of the title
            dir_path = os.path.join(folder_path, title[:5])
            os.makedirs(dir_path, exist_ok=True)
            print(f"Processing {title}")
            startlecture = time.time()
            # Create a JSON file named after the entire title within the newly created directory
            transcription = os.path.join(dir_path, f"{title}.json")
            with open(transcription,'r') as json_file:
                lecture = json.load(json_file)
            for lecture in lecture:
                timestamps = lecture['Timestamps']
                # Sort timestamps based on the 'start' field, treating None as infinity
                sorted_timestamps = sorted(timestamps, key=lambda x: float('inf') if x['start'] is None else x['start'])
                for timestamp in sorted_timestamps:
                    content = timestamp['text']
                    start = time.time()
                    content = GoogleTranslator(source='de', target='en').translate(content)
                    # print(f"Translation time took: {time.time()-start}")
                    start = time.time()
                    vector = encoder.encode(content).tolist()
                    # print(f"Encoding time took: {time.time()-start}")
                    # Add the data to the big dictionary
                    big_dict.append({
                        'lecture': title,
                        'content': content,
                        'lecture_link': website,
                        'course': course,
                        'vector': vector,
                        'start': timestamp['start'],
                    })
            print(f"Processing lecture took: {(time.time()-startlecture)/60} minutes")
                
            
    file_path = os.path.join(os.path.join(folder_path, course), f"{course}.json")        
    with open(file_path, 'w') as json_file:
        json.dump(big_dict, json_file)
    
def createcollection(name, dimensions, courses, folder):
    start = time.time()
    client.recreate_collection(
        collection_name=name,
        vectors_config=models.VectorParams(
            size=dimensions,  # Vector size is defined by used model
            distance=models.Distance.COSINE,
        ))
    print(f"Recreating collection took: {time.time()-start}")
    initialstart = time.time()
    counter = 1  # Initialize counter before starting the loop over courses
    for course in courses:
        start = time.time()
        filepath = os.path.join(folder, f"{course}.json")
        with open(filepath) as f:
            documents = json.load(f)
        if documents:  # Check if the list is not empty
            print(f"First document type: {type(documents[0])}")
        for doc in documents:
            client.upload_points(
                collection_name=name,
                points=[
                    models.PointStruct(
                        id=counter,  # Use the counter as a unique identifier for each document
                        vector=doc["vector"], 
                        payload={**{key: value for key, value in doc.items() if key != 'vector'}, 'course': course}
                    )
                ],
            )
            counter += 1  # Increment the counter for each document
        print(f"Uploading points took: {time.time()-start}")
    print(f"Total time taken: {time.time()-initialstart}")

def queryCollection(query,collection):
    coursenames = {
        '23037': 'System Programmierung SoSe21',
        '25797': 'Wissenschaftliches Rechnen WiSe21/22',
        '28622': 'Diskrete Strukturen SoSe22',
        '30325': 'Wissenschaftliches Rechnen WiSe22/23',
        '30385':'Berechenbarkeit und Komplexität WiSe22/23',
        '30849': 'Softwaretechnik und Programmierparadigmen WiSe22/23',
        '31070': 'Analysis 1 und Lineares Algebra WiSe22/23',
        '31624': 'Algorithmen und Datenstrukturen SoSe23',
        '33475': 'Diskrete Strukturen SoSe23',
        '33845': 'Algorithmentheorie SoSe23',
        '34637': 'Robotics WiSe23/24',
        '35440': 'Logik Wise23/24',
        '35532': 'IntroProg Wise23/24',
        '35958': 'Softwaretechnik und Programmierparadigmen WiSe23/24',
        '36347': 'Betriebsysteme Praktikum WiSe23/24',
        '37656': 'Verteilte Systeme SoSe24',
        '37800': 'Algorithmentheorie SoSe24',
        '38479': 'Algorithmen und Datenstrukturen SoSe24'
    } 
    lang = langdetect.detect(query)
    print(f"Detected language: {lang}")
    if lang != 'en':
        query = GoogleTranslator(source=lang, target='en').translate(query)
    start = time.time()
    query_vector = encoder.encode(query).tolist()
    search_results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=5,
    )
    print(f"Querying took: {time.time()-start}")
    results = []
    visited = []
    outstring = ""
    first = True
    for res in search_results:
        if res.score>0.65 and res.payload['course'] not in visited:
            results.append(res)
            visited.append(res.payload['course'])
            website = res.payload['lecture_link'] + '#@' + str(int(res.payload['start']))
            if first:
                if lang != 'en':
                    outstring += f"Folgende relevante Videos wurden gefunden: \n"
                else:
                    outstring += f"Following relevant videoes were found: \n"
                first = False
            if lang != 'en':
                outstring += f"Vom Kurs {coursenames[res.payload['course']]}: {website} \n"
            else:
                outstring += f"From course {coursenames[res.payload['course']]}: {website} \n"
    if not results:
        if lang != 'en':
            outstring += "Keine relevanten Videos gefunden"
        else:
            outstring += "No relevant videos found"
    return outstring

# Code below vectorizes the transcriptions and saves them as JSONs
#To reuse, change the folder path and course variable
# NOTE CAN TAKE A WHILE TO RUN for all courses listed in done took around 26 hours

# actualstart = time.time()
# create_vector_json(r'F:\MVA\Video_Indexing', '25797')
# Done: '23037','25797','28622','30325', '30849', ,'31070','31624','33475','33845','34637','35440','35532','35958','36347','37656','37800','38479'
# courses = ['30385']
# print(f"Running batch with {len(courses)} courses")
# splits = []
# for course in courses:
#     start = time.time()
#     print(f"\n \n Processing course: {course}")
#     create_vector_json(r'F:\MVA\Video_Indexing', course) # Change the folder path to the folder containing the course folders
#     print(f"\n \n Creating vector json took: {(time.time()-start)/60} minutes")
#     splits.append(f"Course {course} took {(time.time()-start)/60} minutes")

# print(f"Total time taken: {(time.time()-actualstart)/60} minutes")
# for split in splits:
#     print(split)


# Code below creates a collection in Qdrant and uploads a list of jsons
# createcollection('MVA', encoder.get_sentence_embedding_dimension(), ['23037','25797','28622','30325', '30385','30849','31070','31624','33475','33845','34637','35440','35532','35958','36347','37656','37800','38479'], 'Vectorized/')




# print(queryCollection('Wie funktuniert Matrizen multiplikation? ich habe es nicht wirklich in der Vorlesung verstanden','MVA'))

