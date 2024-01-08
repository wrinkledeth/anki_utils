import anki
from anki.storage import Collection
from pypinyin import pinyin
import opencc
from gpt4all import GPT4All

# ! Global variables
col_path = "/Users/zen/Library/Application Support/Anki2/Zen/collection.anki2"  # Path to the Anki collection
col = Collection(col_path)  # Initialize a new collection
# deck_name = "subs2srs"  #! deck name
deck_name = "All::Mandarin::sentences"
deck = col.decks.by_name(deck_name)  # Get deck by name
notes = col.find_notes(f'"deck:{deck["name"]}"')  # Get the notes from the deck
converter = opencc.OpenCC(
    "t2s"
)  # instantiate OpenCC traditional to simplified converter
model = GPT4All(
    model_name="mistral-7b-instruct-v0.1.Q4_0.gguf", verbose=True
)  # instantiate GPT4All


def trad_to_simp():
    """Convert traditional chinese to simplified chinese"""
    count = 0
    for note_id in notes:
        note = col.get_note(note_id)  # Get the note
        original_sentence = note.fields[2]  # og hanzi
        simplified_sentence = converter.convert(
            original_sentence
        )  # convert to simplified
        # # Look at original_sentence and check if it has traditional characters, if it does, convert to simplified
        if simplified_sentence != original_sentence:
            count += 1
            # print("-----------------------------------")
            # print("Found traditional characters in note: ")
            # print(f"Original: {original_sentence}")
            # print(f"Simplified: {simplified_sentence}")
        note.fields[2] = simplified_sentence  # update original field
        col.update_note(note)  #! update note
    print(f"Converted traditional characters to simplified in {count} notes.")


def update_pinyin():
    """Add pinyin to notes"""
    count = 0
    for note_id in notes:
        note = col.get_note(note_id)  # Get the note
        if note.fields[4] != "":  # pinyin
            continue
        count += 1
        simplified_sentence = note.fields[2]  # og hanzi
        pinyin_string = " ".join(  # determine pinyin
            item for sublist in pinyin(simplified_sentence) for item in sublist
        )
        # print("-----------------------------------")
        # print(f"Original: {simplified_sentence}")
        # print(f"Pinyin: {pinyin_string}")
        note.fields[4] = pinyin_string  # update pinyin field
        col.update_note(note)  #! update note
    print(f"Added pinyin to {count} notes (which had no pinyin).")


def update_english():
    """Add english to notes"""
    count = 0
    for note_id in notes:
        note = col.get_note(note_id)  # Get the note
        if note.fields[5] != "":  # english
            continue
        count += 1
        simplified_sentence = note.fields[2]  # og hanzi
        english = model.generate(
            f"Translate the Chinese sentence '{simplified_sentence}' to English.",
            max_tokens=60,
            temp=0.8,
        )
        # remove "Answer:" prefix from english if it is there:
        if ":" in english:
            english = english.split(":")[1].strip()
        print("-----------------------------------")
        print(f"Original: {simplified_sentence}")
        print(f"English: {english}")
        note.fields[5] = english  # update english field
        col.update_note(note)  #! update note
        # if count == 10:
        #     break
    print(f"Added english to {count} notes (which had no english).")


def update_target_english_definition():
    """Add target english definition to notes"""
    count = 0
    for note_id in notes:
        note = col.get_note(note_id)  # Get the note
        # 11 am-unknowns
        # 12 am-unknowns-count
        am_target = note.fields[11]  # am-unknowns
        am_target_count = note.fields[12]  # am-unknowns-count
        if am_target_count == "1":  # if there are no unknowns
            count += 1
            english = model.generate(
                f"Translate the Chinese word '{am_target}' to English.",
                max_tokens=60,
                temp=0.8,
            )
            # remove "Answer:" prefix from english if it is there:
            if ":" in english:
                english = english.split(":")[1].strip()
            print("-----------------------------------")
            print(f"Original: {am_target}")
            print(f"English: {english}")
            note.fields[10] = english  # update english definition field
            col.update_note(note)  #! update note
        # if count == 10:
        #     break
    print(f"Added target english definitions to {count} notes (which had no english).")


def main():
    # trad_to_simp()
    # update_pinyin()
    # update_english()
    update_target_english_definition()
    col.close()


# if main
if __name__ == "__main__":
    main()
