import anki
from anki.storage import Collection
from pypinyin import pinyin
import opencc
from gpt4all import GPT4All
import re

# ! Global variables
col_path = "/Users/zen/Library/Application Support/Anki2/Zen/collection.anki2"  # Path to the Anki collection
col = Collection(col_path)  # Initialize a new collection
# deck_name = "subs2srs"  #! deck name
deck_name = "Spanish::Conjugation"
deck = col.decks.by_name(deck_name)  # Get deck by name
notes = col.find_notes(f'"deck:{deck["name"]}"')  # Get the notes from the deck
model_path = "/Users/zen/Library/Application Support/nomic.ai/GPT4All/Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
model = GPT4All(model_path)


def process_string(text):
    # Extract the text between curly braces
    # Remove line breaks
    text = text.replace("\n", "")
    # Remove HTML tags
    text = re.sub("<[^<]+?>", "", text)
    # Remove special characters
    text = re.sub(r"[{}⇠↧→…〰⊙↬↫()]", "", text)
    # Use regex to match and extract the target
    text = re.sub(r"(.*\s+c\d+::)(.*?)(::.+?\(.*?\))", r"\1\2\3", text)
    # Split the string on spaces
    parts = text.split()
    # Iterate over the parts and process the part containing "::"
    for i, part in enumerate(parts):
        if "::" in part:
            subparts = part.split("::")
            parts[i] = subparts[1]  # Extract "era" from the subparts
    # Join the parts back together with spaces
    result = " ".join(parts)
    return result


def call_chat(translation_input):
    print("-----------------------------------")
    print(f"Original: {translation_input}")
    # Generate the English definition
    enriched_prompt = f"Spanish Sentence: {translation_input}'\nEnglish Translation:."
    out = model.generate(
        enriched_prompt,
        max_tokens=60,
        temp=1,
    )
    english = out.split("\n")[0]
    print(f"English: {english}")
    return english


def update_target_english_definition():
    """Add target english definition to notes"""
    count = 0
    for note_id in notes:
        note = col.get_note(note_id)  # Get the note
        count += 1
        prompt = note.fields[1]
        cleaned_prompt = process_string(prompt)
        if count >= 8:  # skip over intro cards
            english = call_chat(cleaned_prompt)
            note.fields[2] = english  # update english definition field
            col.update_note(note)

    print(f"Added target english definitions to {count} notes (which had no english).")


def main():
    update_target_english_definition()
    col.close()


# if main
if __name__ == "__main__":
    main()
