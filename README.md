# anki_utils

Takes a subs2srs deck that only has chinese subtitles and audio and:
- converts any traidtional characters to simplified
- generates pinyin 
- uses LLM to translate to english 
- updates each note in the deck with the above changes.

## Deck Field Format
```bash
0 Sequence Marker
1 Target
2 Simplified
3 Traditional
4 Pinyin
5 English
6 Snapshot
7 Audio
8 Notes
9 Proper_nounts
10 English_Definition
11 am-unknowns
12 am-unknowns-count
13 am-highlighted
14 am-difficulty 

```

## Traditional to simplified (OpenCC)

[opencc github](https://github.com/BYVoid/OpenCC)

[opencc homebrew](https://formulae.brew.sh/formula/opencc)

```bash
brew install opencc
```
```python
# instantiate OpenCC traditional to simplified converter
converter = opencc.OpenCC("t2s")
simplified_sentence = converter.convert(original_sentence)
```

## Hanzi to to pinyin
```python
from pypinyin import pinyin

pinyin_string = " ".join(
    item for sublist in pinyin(simplified_sentence) for item in sublist
)
```

## Gpt4all local translations

List of models with python bindings available: https://github.com/nomic-ai/gpt4all/blob/main/gpt4all-chat/metadata/models2.json

```bash
➜  GPT4All pwd                
/Users/zen/Library/Application Support/nomic.ai/GPT4All
➜  GPT4All ls
.rw-r--r--   46M zen  22 Dec  2023  all-MiniLM-L6-v2-f16.gguf
.rw-r--r--  4.1G zen   1 Dec  2023  mistral-7b-instruct-v0.1.Q4_0.gguf
.rw-r--r--  4.1G zen   1 Dec  2023  mistral-7b-openorca.Q4_0.gguf
.rw-r--r--  7.4G zen   1 Dec  2023  wizardlm-13b-v1.2.Q4_0.gguf
```

```python
from gpt4all import GPT4All
model = GPT4All("mistral-7b-openorca.Q4_0.gguf")
output = model.generate(
    f"Translate the Chinese sentence '{simplified_sentence}' to English.",
    max_tokens=60,
    temp=0.8,
)
print(output)
```

## samples

```bash
-----------------------------------
Original: 现在起才是真正的战斗 L
English: Now is when the real battle begins.
-----------------------------------
Original: 请进来吧
English: Please come in.
-----------------------------------
Original: 要是这个女人
English: If this woman
-----------------------------------
Original: 抢在我之前告诉警方的话…
English: Someone told the police what happened before I did.
-----------------------------------
Original: 但是
English: However
-----------------------------------
Original: 似乎连死神之外的神 也是站在我这边的
English: "It seems like all gods, except for the god of death, are standing on my side."
Added english to 13231 notes (which had no english).
```

## Todo:
- [ ] whisper api to generate cards from audio / video only. 