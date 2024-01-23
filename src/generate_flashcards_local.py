from langchain_community.llms import Ollama

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List
import pandas as pd
import os,time,json

# loading api key and defining vars

load_dotenv("../.env")
deck_name = os.environ.get("DECK_NAME")
csv_file_path = "../csv/" + deck_name + ".csv"

model = "mistral"
temperature = 0.0


class FlashCard(BaseModel):
    word: str = Field(description="The word")
    phonetic: str = Field(description="The phonetic pronunciation of the word")
    pos: str = Field(description="The part of speech of the word")
    cnMeaning: str = Field(description="The Chinese meaning of the word")
    enMeaning: str = Field(description="The English meaning of the word")
    tips: str = Field(description="Tips for learning the word")

class FlashCardArray(BaseModel):
    flashcards: List[FlashCard]

def create_flashcards_from_text(input_text: str, user_prompt: str, csv_file_path: str):
    llm = Ollama(model=model, temperature=temperature)
    print("Creating flashcards...")

    pydantic_parser = PydanticOutputParser(pydantic_object=FlashCardArray)

    format_instructions = pydantic_parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_template(template=user_prompt)
    messages = prompt.format_messages(input_text=input_text, format_instructions=format_instructions)

    output = llm.invoke(messages)
    print(output)
    flashcards = pydantic_parser.parse(json.loads(output))

    list_of_flashcards = [card.dict() for card in flashcards.flashcards]

    df = pd.DataFrame(list_of_flashcards)

    if os.path.isfile(csv_file_path):
        df.to_csv(csv_file_path, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_file_path, mode="w", header=False, index=False)

def main():
    try:
        chunk_size = 10
        chunks = []

        with open("input.txt", "r") as f:
            lines = f.readlines()
            comma_separated_lines = [line.strip() for line in lines]
            chunks = [comma_separated_lines[i:i + chunk_size] for i in range(0, len(comma_separated_lines), chunk_size)]
            

        with open("prompt.txt", "r") as f:
            user_prompt = f.read()
            for chunk in chunks:
                input_text = ' '.join(chunk)
                create_flashcards_from_text(input_text, user_prompt, csv_file_path)
                # sleep 2 seconds
                time.sleep(2)

    except Exception as e:
        print(f"Error occurred: {e}")
        return


if __name__ == "__main__":
    main()
