import csv
import genanki
import sys
import os
import random,requests
from dotenv import load_dotenv
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

load_dotenv("../.env")
output_deck_name = os.environ.get("DECK_NAME")
csv_file_path = "../csv/" + output_deck_name + ".csv"
output_file_path = "../decks/" + output_deck_name + ".apkg"
wordaudio='https://dict.youdao.com/dictvoice?type=0&audio='

def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        word_list = [(row[0], row[1], row[2], row[3], row[4],row[5]) for row in csv_reader]
    return word_list
def download_audio(word):
    full_audio_url = wordaudio + word
    response = requests.get(full_audio_url, headers=HEADERS)

    audio_path = f"/tmp/{word}.mp3"
    with open(audio_path, "wb") as audio_file:
        audio_file.write(response.content)
    return audio_path
def create_anki_deck(deck_name, qa_list):
    model_id = random.randrange(1 << 30, 1 << 31)
    my_model = genanki.Model(
        1607392319,
        'Cambridge Dictionary Model',
        fields=[
            {'name': 'Word'},
            {'name': 'Phonetic'},
            {'name': 'Audio'},
            {'name': 'POC'},
            {'name': 'cnMeaning'},
            {'name': 'enMeaning'},
            {'name': 'tips'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Word}}<br>{{Phonetic}}<br>{{Audio}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{cnMeaning}}<br>{{enMeaning}}<br>{{tips}}',
            },
        ],
    )
    deck_id = random.randrange(1 << 30, 1 << 31)
    my_deck = genanki.Deck(deck_id, deck_name)
    my_package = genanki.Package(my_deck)
    for word_info in read_csv(csv_file_path):
        audio_path = download_audio(word_info[0])
        my_package.media_files.append(audio_path)
        my_note = genanki.Note(
                model=my_model,
                fields=[word_info[0], word_info[1], f'[sound:{word_info[0]}.mp3]',
                        "<br>" + word_info[2], "<br>" + word_info[3], 
                        "<br>"+word_info[4] , "<br>"+word_info[5]]
            )
        my_deck.add_note(my_note)
    my_package.write_to_file(output_file_path)

if __name__ == "__main__":
    create_anki_deck(output_deck_name, csv_file_path)

