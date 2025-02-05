import genanki
import random
from gpt4all import GPT4All
from pypinyin import pinyin, Style
# from anthropic import Anthropic

def parse_char_freq():
    """Parse CharFreq.txt and extract character, pinyin, and English definition"""
    char_data = []
    
    # Try different encodings commonly used for Chinese text
    encodings = ['gb18030', 'gbk', 'gb2312', 'utf-8']
    
    for encoding in encodings:
        try:
            with open('CharFreq.txt', 'r', encoding=encoding) as f:
                for line in f:
                    # Skip empty lines or header lines
                    if not line.strip() or line.startswith('/*'):
                        continue
                        
                    # Split the line by tabs
                    parts = line.strip().split('\t')
                    
                    # Check if we have the minimum required parts (rank, character, frequency, cumulative_freq)
                    if len(parts) >= 4:
                        rank = parts[0]
                        character = parts[1]
                        frequency = parts[2]
                        cumulative_freq = parts[3]
                        
                        # Handle optional fields with default values
                        pinyin = parts[4] if len(parts) > 4 and parts[4].strip() else ""
                        english = parts[5] if len(parts) > 5 and parts[5].strip() else ""
                        
                        # Skip entries with invalid characters
                        if character.strip() and not character.startswith('�'):
                            char_data.append({
                                'rank': int(rank),
                                'character': character,
                                'frequency': int(frequency),
                                'cumulative_freq': float(cumulative_freq),
                                'pinyin': pinyin,
                                'english': english
                            })
            # If we successfully read the file, break the loop
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with encoding {encoding}: {str(e)}")
            continue
    
    if not char_data:
        raise Exception("Could not read file with any of the attempted encodings")
    
    print(f"Successfully parsed {len(char_data)} characters")
    
    # Print some statistics about missing fields
    missing_pinyin = sum(1 for entry in char_data if entry['pinyin'] == "N/A")
    missing_english = sum(1 for entry in char_data if entry['english'] == "No definition available")
    print(f"Characters missing pinyin: {missing_pinyin}")
    print(f"Characters missing English definition: {missing_english}")
        
    return char_data


def create_char_deck():
    """Create a new Anki deck with character frequency data"""
    
    # Create the note model (template)
    model_id = random.randrange(1 << 30, 1 << 31)  # Random ID for the model
    char_model = genanki.Model(
        model_id,
        'Chinese Character Model',
        fields=[
            {'name': 'Character'},
            {'name': 'Pinyin'},
            {'name': 'English'},
            {'name': "Examples"},
            {'name': 'Rank'},
        ],
        templates=[
            {
                'name': 'Character Card',
                'qfmt': '''
                    {{Character}}
                ''',
                'afmt': '''
                    {{Character}}
                    <hr>
                    <div class="info">
                        <div>{{Pinyin}}</div>
                        <div>{{English}}</div>
                        <div style="white-space: pre-line;">{{Examples}}</div>
                        <div>[Rank: {{Rank}}]</div>
                    </div>
                ''',
            },
        ],
        css='''
            .card {
                font-family: custom;
                font-size: 30px;
                text-align: center;
                color: black;
                background-color: white;
            }
            
            @font-face {
                font-family: custom;
                src: url('_huwawenkaiti.ttf');
            }
            
            /* Character size */
            .card:first-of-type {
                font-size: 80px;
            }
            
            /* Info section styling */
            .info {
                font-size: 24px;
                margin-top: 20px;
            }
            
            hr {
                margin: 20px 0;
            }
        '''
    )

    missing_chars = []

    # Create a new deck
    deck_id = random.randrange(1 << 30, 1 << 31)  # Random ID for the deck
    deck = genanki.Deck(deck_id, 'Chinese Characters')

    # Get character data
    char_data = parse_char_freq()

    model = GPT4All(model_name="Meta-Llama-3-8B-Instruct.Q4_0.gguf", verbose=True)
    # model = GPT4All(model_name="Llama-3.2-1B-Instruct-Q4_0.gguf", verbose=True)
    # Add system prompt and template
    system_prompt = "You are a helpful Chinese language assistant. Provide clear, accurate examples of Chinese words and phrases."
    
    count = 0
    print("getting examples...")
    for entry in char_data:
        count += 1
        print('-------------------')
        print(f"Processing character {entry['character']} ({count}/{len(char_data)})")

        # Create a more structured prompt with clear instructions
         # Improved prompt with more explicit formatting instructions
        prompt = f"""
    Generate exactly three examples following this EXACT format:
    'Chinese word in simplified chinese characters' (pinyin) - English definition

    Rules:
    - Each example MUST be 2-4 characters long in simplified Chinese
    - Each example MUST contain '{entry['character']}'
    - Each example MUST include pinyin in parentheses
    - Each example MUST include English definition after a hyphen
    - Put each example on a new line
    - NO additional text or explanations

    Example format:
    example (pinyin) - english definition"""
    

         # Generate examples using model
        example_field = model.generate(prompt, max_tokens=200, temp=0.0)
        print("raw example")
        print(example_field)
        print("---")
        valid_examples = []
        for line in example_field.split('\n'):
            line = line.strip()
            if not line or len(line) < 4:
                continue
                
            try:
                # Split into Chinese and English parts
                chinese_part = line.split('(')[0].strip().strip("'").strip().strip('"').strip()  # Remove quotes
                english_part = line.split('-')[1].strip()
                # Generate correct pinyin using pypinyin
                py = pinyin(chinese_part, style=Style.TONE)
                pinyin_part = ' '.join([''.join(p) for p in py])
                
                if (entry['character'] in chinese_part and 
                    1 < len(chinese_part) <= 8 and 
                    pinyin_part):
                    # Reconstruct the line with correct pinyin
                    valid_line = f"{chinese_part} ({pinyin_part}) - {english_part}"
                    if valid_line not in valid_examples:
                        valid_examples.append(valid_line)
            except (IndexError, Exception):
                continue
        
        # Take up to 3 valid examples
        valid_examples = valid_examples[:3]
        
        # If we have no valid examples, provide a fallback
        if not valid_examples:
            print(f"No valid examples found for {entry['character']}")
            example_field = ""
            missing_chars.append(entry['character'])
        else:
            example_field = '\n'.join(valid_examples)
        print("valid example")
        print(example_field)

        note = genanki.Note(
            model=char_model,
            fields=[
                entry['character'],
                entry['pinyin'],
                entry['english'],
                example_field,
                str(entry['rank'])  # Convert rank to string
            ])
        deck.add_note(note)
        # if count == 5000: 
        #     break

    # Save the deck to a file
    package = genanki.Package(deck)
    # Add the font file to the package
    package.write_to_file('chinese_characters.apkg')
    print(f"Created deck with {len(char_data)} characters")
    print(f"Missing characters: {missing_chars}")

'''
['了', '就', '但', '与', '把', '入', '四', '城', '李', '六', '仅', '米', '尼', '急', '既', '刘', '佛', '湾', '枪', '予', '厂', '爸', '狂', '沿', '袭', '曼', '彻', '彼', '零', '辆', '绪', '番', '伍', '氏', '媒', '滚', '曹', '韦', '粹', '侯', '齿', '押', '郭', '寸', '薛', '拾', '霞', '璇', '瞬', '仑', '萍', '株', '贬', '丙', '鳞', '暮', '搂', '襟', '撇', '乍', '敛', '汰', '慑', '珀', '洽', '庚', '捂', '铀', '琪', '瑚', '龚', '湛', '俞', '琦', '迸', '卉', '挛', '薯', '眸', '簧', '巳', '漓', '蔼', '蛟', '觑', '圭', '撬', '韬', '唆', '漪', '讪', '挝', '鬓', '珑', '瑾', '赓', '僭', '亘', '欤', '嚏', '鋆', '荼', '皑', '锵', '鸯', '颚', '龛', '镁', '骋', '耘', '涓', '荪', '穑', '徇', '黜', '濑', '璜', '铬', '熠', '瞑', '郅', '弋', '蟠', '粼', '垠', '汩', '宸', '馕', '憩', '荩', '蹶', '睨', '掇', '铡', '觯', '讫', '卞', '镳', '谖', '乩', '骛', '苫', '锟', '洹', '竑', '鍪', '啶', '阄', '郧', '铉', '厝', '莅', '硒', '鼐', '妪', '馔', '窣', '俎', '嬷', '稹', '羯', '圻', '饧', '砝', '開', '魉', '玖', '岢', '戬', '樯', '浠', '龆', '臬', '濉', '聩', '砉', '袢', '侩', '涪', '笾', '骓', '蜍', '禳', '苄', '跹', '磬', '崾', '硪', '揶', '囹', '赅', '贽', '獯', '縯', '彀', '涑', '朐', '匚', '仞', '蝼', '馃', '雠', '蛑', '艉', '捌', '獬', '鄄', '齑', '躅', '俅', '缒', '镆', '甙', '嫘', '鐾', '墉', '岿', '侔', '砹', '锛', '泶', '曛', '轉', '偬', '仫', '欹', '組', '浼', '瀣', '褰', '醍', '謝', '湓', '磴', '锝', '黼', '砬', '硇', '锍', '織', '羼', '䜣', '艟', '達', '跬', '锓', '槠', '锘', '妣', '鄹', '預', '旰', '岜', '镪', '荈', '麴', '顸', '缋', '總', '屣', '獒', '佴', '醌', '岽', '嫜', '砑', '墼', '顒', '妁', '杩', '辋', '豂', '螋', '鄩', '珉', '鞬', '猱', '眢', '镎', '胬', '腳', '記', '錯', '粞', '撙', '洎', '礌', '藚', '牾', '玟', '鮊', '萜', '哚', '疬', '鳑', '觫', '遹', '攴', '埝', '釐', '柝', '摅', '䦟', '諸', '鎯', '箬', '埸', '瞍', '簋', '艖', '鐮', '攉', '癍', '劓', '饾', '埯', '袝', '馘', '谫', '廑', '稓', '绐', '黹', '譞', '釆', '鍏', '筸', '麄', '覩', '祂', '靸', '蠃', '緡', '擐', '臅', '茖', '貙', '䴘', '鎰', '铓', '骃', '诪', '鋬', '埕', '鵳', '圬', '憝', '腠', '翹', '鐣', '鐻', '駚', '罽', '捃', '睺', '顩', '䥇', '馬', '翧', '舡', '䴙', '觍', '羶', '臜', '礞', '纁', '滠', '鋹', '鋵', '訙', '硱', '箖', '酖', '闅', '镈', '罶', '袉', '訚', '眳', '糈', '龜', '綎', '雔', '衒', '鳰', '莾', '讝', '鈩', '閷', '觝', '鳤', '穉', '鐓', '睏', '秵', '黪', '䞍', '洚', '韥', '筅', '诐', '祪', '禘', '臺', '菍', '臒', '苿', '蔂', '跓', '軍', '醿', '駵', '䝼', '艞', '蕡', '鼱', '剞', '瘼', '穪', '粡', '闉', '铥', '觖', '麆', '睪', '袚', '錏', '稟', '鉄', '䜩', '䴗', '鐏', '眎', '肅', '鄦', '筰', '茷', '褧', '檑', '鹯', '錞', '䌷', '襍', '覗', '纘', '鼶', '鈍', '铽', '竝', '酁', '鈿', '腽', '韌', '頎', '顬', '禣', '迏', '鐇', '睄', '窔', '筊', '腪', '戤', '麯', '綈', '冁', '辌', '郪', '韺', '顝', '麉', '藬', '醲', '脺', '祮', '閛', '隸', '籓', '镥', '笖', '粍', '覍', '訌', '釛', '鈶', '顪', '驘', '镦', '禬', '繨', '鹓', '繟', '脰', '苽', '邘', '鑕', '脶', '鶜', '鹍', '䦆', '蠆', '緌', '蠾', '瞫', '艐', '蔲', '蛷', '衋', '鍧', '鍼', '镵', '陗', '鶡', '萗', '転', '鄷', '綑', '臛', '錐', '矊', '秲', '竄', '繉', '脙', '腗', '艜', '覂', '譄', '騺', '鴷', '鼞', '鼤', '齺', '䦶', '䲡', '繑', '纑', '蠙', '鎪', '瞕', '窪', '虰', '籆', '軉', '鋻', '鬑', '祻', '繌', '聜', '艕', '詯', '諓', '謪', '輈', '鄛', '鏉', '雊', '駳', '鮾', '齛', '絾', '襬', '矎', '譔', '趬', '闚', '韗', '鬖', '鳠', '窅', '窾', '筭', '肙', '臞', '苶', '蠜', '覈', '訆', '譻', '貑', '醼', '鋋', '鐄', '駉', '鬿', '稌', '綂', '艎', '苃', '訅', '鈰', '鋫', '鍔', '鐨', '騛', '黋', '緲', '藫', '貎', '逤', '秶', '窇', '簯', '粶', '繚', '翑', '覙', '訑', '詸', '諏', '貋', '贁', '鈉', '鈺', '鋭', '鐖', '鐧', '鐳', '鑱', '閬', '閿', '騼', '鼏', '鼫', '䦂', '䲟', '䴓', '䴕', '䶮', '盬', '錣', '鼊', '䴖', '粛', '靮', '饜', '裛', '鎋', '黿', '秹', '茢', '眃', '硄', '秙', '稧', '稬', '穜', '竒', '筶', '籜', '綡', '綶', '緄', '縋', '繬', '纗', '罯', '肍', '蠪', '腣', '馻', '磞', '醱', '巛', '鐴', '鑵', '飰', '饐', '㳠', '䁖', '磸', '礽', '禌', '詖', '詪', '豗', '貣', '逓', '鄺', '鈪', '鐐', '鼪', '龔', '䴔', '穯', '襛', '簑', '緅', '緍', '艒', '豠', '鼅', '㩳', '眣', '睎', '礒', '禞', '秠', '穱', '糓', '紭', '綅', '羗', '翭', '膋', '舃', '艭', '虵', '譌', '譸', '趝', '躩', '鄟', '鎴', '雋', '颩', '魫', '鷁', '鸘', '盓', '緐', '繖', '翈', '苅', '莁', '蒑', '蓕', '薝', '蠚', '裶', '裺', '誻', '貮', '鄑', '酼', '銒', '鎍', '鐎', '鐤', '鐿', '闛', '餒', '饆', '鬉', '鬸', '魛', '鳷', '鷵', '鼉', '齰', '綀', '缾', '羷', '艍', '蠅', '鈕', '鏍', '觓', '鄍', '衸', '礂', '秼', '筂', '箞', '簤', '綄', '綔', '綗', '綴', '緶', '翢', '聹', '脳', '艙', '蕵', '藳', '螐', '覊', '訡', '謩', '謸', '讍', '讛', '贀', '跈', '輒', '邫', '鄽', '醆', '醞', '醽', '鉍', '鐑', '鑴', '韴', '韷', '饡', '駶', '鬅', '魰', '魸', '鶈', '鼑', '齼', '䦃', '䲣', '䲠', '秅', '鈆', '鈖', '銅', '鍥', '鎇', '鐷', '纍', '翸', '輘', '䓖', '瞡', '岍', '餼', '睉', '礑', '趌', '絒', '蔄', '螦', '錋', '鎝', '鐩', '葇', '蒪', '銫', '関', '秺', '籋', '緵', '魒', '縀', '豰', '錧', '鍚', '魿', '鮅', '鱓', '鴒']
'''

def main():
    create_char_deck()

if __name__ == "__main__":
    main()