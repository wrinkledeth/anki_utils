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

    actual_missing_chars = ['们', '么', '当', '但', '者', '与', '使', '果', '通', '数', '办', '夫', '兵', '城', '断', '营', '型', '友', '助', '帝', '久', '衣', '敢', '野', '娘', '笔', '诸', '爸', '植', '曼', '缘', '尾', '辩', '辑', '稍', '署', '凭', '绪', '伍', '绕', '彭', '瞧', '殿', '践', '籍', '脉', '帐', '曰', '揭', '蛇', '抛', '纠', '赔', '粹', '娃', '缝', '丑', '肠', '壳', '喂', '扇', '姻', '卵', '狭', '披', '嫁', '拆', '咐', '孕', '棵', '趁', '倘', '仑', '裸', '绵', '剪', '柄', '鞭', '嚷', '焰', '恳', '瓷', '蝶', '颁', '袍', '雀', '捧', '爪', '兔', '姜', '冤', '彪', '桶', '攀', '趟', '株', '熙', '镑', '蚁', '稻', '伽', '烛', '冀', '笛', '贿', '踩', '拱', '枕', '掷', '藩', '氢', '钞', '躬', '蛛', '侣', '畴', '栋', '毯', '稚', '镖', '碳', '咧', '麟', '捡', '哉', '妓', '娥', '匿', '秉', '腻', '擒', '苑', '骆', '裳', '聋', '廖', '墅', '讳', '厕', '窟', '锤', '桨', '蚊', '钙', '礁', '悼', '悯', '珀', '脯', '迭', '鞘', '蟹', '吭', '靡', '铀', '筷', '婪', '扒', '埔', '衅', '悖', '粤', '唬', '诅', '龚', '唔', '疹', '涤', '砌', '侬', '靶', '诛', '梵', '炽', '迸', '嗨', '祠', '躇', '卉', '梧', '脓', '抨', '盎', '鞅', '祟', '攸', '堑', '曝', '蒜', '阙', '笋', '骼', '烹', '捻', '诣', '祁', '袄', '晖', '橄', '觑', '袅', '墩', '彝', '帧', '娼', '茧', '鹉', '拈', '痊', '亟', '帚', '冗', '闵', '淄', '韬', '婷', '蜒', '枷', '烬', '讪', '驹', '啧', '跷', '戟', '瞳', '瓢', '鬓', '髅', '蟋', '蹿', '釜', '撵', '珑', '佚', '甥', '寐', '攥', '祯', '蟆', '镯', '诩', '鸳', '筵', '壑', '笙', '迢', '鋆', '谩', '荼', '椰', '蘸', '邃', '皑', '鹳', '鸯', '胤', '斓', '荟', '虱', '龛', '髯', '灸', '蚤', '辍', '呷', '啾', '昵', '飙', '邙', '蚓', '撅', '斡', '赈', '徨', '翡', '缨', '娩', '濑', '馁', '匝', '铬', '靼', '椿', '祗', '镭', '驸', '牍', '婊', '鹄', '褛', '咛', '澹', '烯', '蟮', '蓟', '诿', '噼', '獾', '叵', '饕', '垠', '饨', '舐', '箕', '咝', '馕', '俑', '缜', '酚', '憩', '掸', '酯', '蚜', '扪', '蝮', '獭', '睨', '琥', '殓', '袂', '與', '祉', '诳', '饪', '恸', '迨', '龢', '荻', '诜', '視', '硼', '泅', '诮', '暹', '梏', '阈', '哂', '噘', '噔', '嗵', '胪', '茏', '郢', '弑', '翦', '裟', '铱', '阄', '祚', '泱', '陲', '铉', '桠', '硎', '煨', '馔', '秣', '蟪', '嬷', '錾', '祜', '掮', '庾', '圻', '镉', '螫', '颢', '開', '旎', '涫', '珈', '遴', '诂', '髁', '戬', '脍', '劬', '鲧', '矍', '觞', '菸', '腸', '婺', '螟', '菟', '邬', '殇', '愆', '袢', '莜', '阌', '圜', '赍', '裰', '逖', '讵', '菬', '垅', '蔺', '庥', '鹕', '髂', '槊', '跞', '蜍', '骠', '跹', '騔', '笸', '趸', '饴', '雱', '須', '诎', '嗌', '鞫', '獯', '疖', '掾', '圮', '廪', '笱', '匏', '椴', '箧', '愀', '鹨', '佶', '厍', '徉', '勰', '嵬', '仞', '轳', '蝼', '跆', '榇', '糅', '锩', '艉', '咴', '劢', '菔', '伥', '萘', '芤', '镛', '蘅', '缒', '荏', '唳', '檩', '骱', '颎', '荠', '醣', '疃', '蠛', '笄', '跣', '铍', '钭', '倬', '螬', '紅', '衽', '嫘', '钌', '裼', '锗', '醵', '扦', '镞', '侔', '薨', '狯', '铳', '缇', '煳', '泶', '瓠', '苊', '蛲', '銎', '噻', '呖', '肭', '鳙', '胙', '鬟', '鹪', '鞔', '組', '庹', '舾', '浼', '甯', '瑷', '磙', '鹮', '迓', '艚', '祢', '蟥', '砬', '酽', '锍', '鞲', '哏', '邳', '䜣', '荸', '镄', '艟', '跬', '僬', '眙', '訾', '俜', '爨', '谳', '脹', '遺', '锬', '镪', '绡', '荈', '歃', '燠', '陬', '镗', '艨', '佴', '黥', '霈', '顒', '蟲', '葳', '呙', '籤', '遠', '镝', '辋', '珉', '鶇', '趑', '繼', '镎', '翙', '腳', '柽', '撙', '缏', '邠', '棰', '蕻', '绁', '髮', '菥', '萏', '圉', '萜', '鄗', '哚', '髫', '椠', '赟', '疬', '赒', '镨', '觫', '拶', '際', '蓁', '郫', '辯', '菃', '喈', '釐', '柝', '摅', '讉', '鎯', '瞍', '蒐', '艖', '攉', '脞', '饾', '鲐', '貼', '橼', '埯', '馘', '廑', '譞', '絷', '郄', '瘵', '舄', '祂', '袆', '謴', '邾', '眊', '狃', '髆', '仝', '趽', '銧', '妤', '絁', '臅', '詾', '鐘', '貙', '䴘', '鎰', '骃', '猹', '鵳', '圬', '堠', '瘳', '騃', '腠', '铼', '豐', '邲', '駚', '篥', '箦', '菑', '蹟', '捃', '誖', '絽', '臜', '枧', '觌', '礞', '葰', '郇', '赇', '骕', '耱', '鋵', '螝', '贅', '鄬', '鮀', '郕', '镴', '韻', '鳁', '甍', '筍', '絼', '颥', '篚', '裈', '饋', '臏', '闅', '鶎', '祼', '鬛', '瞓', '礡', '硚', '禋', '翀', '龜', '碕', '鲣', '雔', '頠', '莾', '讝', '閷', '龤', '薿', '觝', '鲝', '睏', '蔸', '秵', '蝟', '耩', '筢', '躔', '貯', '韥', '麗', '篩', '绹', '葙', '祪', '菍', '髒', '緒', '菢', '跍', '跓', '鈨', '䝼', '艞', '鞓', '楱', '跼', '邆', '彡', '鞨', '觖', '麆', '镮', '睪', '贠', '跡', '韲', '鶺', '錏', '袃', '親', '鉄', '錆', '麨', '䴗', '脭', '眎', '籠', '肅', '鉏', '褧', '赗', '檑', '腙', '鹯', '簰', '蚢', '蓰', '錞', '䌷', '頍', '纘', '讞', '錫', '铽', '絺', '絿', '脦', '臋', '蟻', '酁', '霧', '韌', '頎', '顬', '譟', '綼', '閗', '迏', '睄', '腪', '苠', '骒', '铞', '耢', '綈', '蕝', '辌', '辒', '頵', '顝', '麉', '麊', '藬', '鞚', '絫', '脺', '蠶', '裀', '蹷', '盦', '祮', '胊', '襱', '鑟', '鶄', '糵', '笖', '罋', '罷', '螞', '覍', '訌', '諄', '遷', '鍛', '閯', '閺', '顆', '顪', '驘', '鶒', '鶗', '禜', '禬', '鮨', '眹', '薦', '鹓', '祦', '脝', '鷧', '脰', '苽', '藗', '譓', '跊', '邇', '邘', '脶', '颋', '鵀', '佧', '緌', '驙', '睠', '禃', '籐', '艐', '袿', '訝', '諆', '轝', '郵', '鍼', '镵', '闢', '陼', '骹', '萗', '驊', '綑', '臛', '錐', '銶', '繉', '脙', '腗', '艜', '袦', '詫', '詮', '誠', '蹱', '輩', '鎖', '駛', '騺', '鳛', '鴷', '鷷', '麎', '麡', '綟', '纑', '駹', '盕', '筽', '臮', '跘', '鞦', '鹐', '鴐', '謏', '脎', '蕌', '軉', '擗', '鬑', '祃', '繌', '脨', '莻', '蓾', '蚈', '蝝', '詯', '諓', '謪', '貤', '赪', '屺', '鏉', '雊', '騽', '鮾', '鶃', '矎', '礋', '纴', '罵', '鍸', '闚', '韗', '鬖', '鷇', '縩', '肙', '肞', '菭', '裩', '訆', '詨', '诇', '躘', '頞', '瞵', '駃', '駉', '鬚', '鬿', '鮌', '鷫', '稌', '臿', '蒟', '蹌', '蹹', '銑', '鐨', '騛', '磚', '繳', '迆', '鑄', '礱', '祿', '矟', '硣', '礀', '竷', '粶', '紋', '繚', '翑', '臄', '蛢', '覙', '詸', '諏', '貋', '贉', '鋭', '錃', '漭', '鐖', '镃', '閬', '鞖', '頤', '館', '饅', '騁', '鶆', '鷿', '䴓', '祅', '禡', '軷', '銦', '錣', '鑢', '鼊', '県', '顔', '萵', '覥', '饜', '裛', '鸴', '黿', '秹', '蚑', '霩', '頺', '籔', '鬶', '睧', '磃', '礮', '祘', '秌', '秙', '稬', '籜', '綶', '緄', '緗', '縁', '繬', '纒', '纗', '腨', '蒘', '鋕', '鎚', '鹒', '腣', '赲', '馻', '瞜', '巛', '飰', '痃', '駞', '睅', '礉', '筥', '羕', '艁', '艂', '衟', '褑', '諈', '豗', '貗', '賯', '迋', '逓', '鞄', '騧', '髽', '鴹', '鼪', '龔', '秊', '垲', '罇', '辢', '鑮', '驈', '㩳', '瞣', '磪', '禞', '秠', '穱', '紭', '罙', '羗', '翭', '肸', '艭', '蘪', '蝨', '蠏', '譌', '譸', '趝', '跾', '踸', '躛', '躩', '躶', '銌', '颩', '駋', '骻', '魫', '盓', '磣', '祤', '禩', '綹', '繖', '繴', '翈', '蒑', '蚿', '蠚', '裶', '裺', '赹', '鄑', '釪', '銒', '錗', '錥', '鎍', '鎘', '鐤', '鞪', '鬉', '鬸', '鵼', '鸍', '鸖', '禪', '綀', '缾', '艍', '葏', '鈕', '鏍', '鏽', '饝', '騇', '祙', '鄍', '羭', '衸', '謡', '閏', '眲', '睋', '礂', '礊', '禐', '秼', '笐', '箞', '簤', '簹', '紝', '緝', '繝', '罰', '聡', '聾', '脟', '脳', '臈', '艑', '艙', '菦', '葮', '訮', '謸', '讍', '讛', '貦', '賅', '軣', '逇', '邥', '醆', '銓', '銜', '錠', '鏈', '闌', '鞊', '顨', '饒', '騿', '驁', '驑', '鬀', '鳪', '鴴', '鵝', '鶈', '鶩', '鷴', '鼑', '禖', '禵', '秅', '粵', '蚡', '輨', '鎇', '绗', '鐷', '鷘', '笿', '翸', '臶', '輐', '䓖', '岍', '睉', '趌', '驛', '萢', '蓧', '蔄', '錋', '鎝', '礐', '葇', '蒪', '蟅', '銫', '関', '鵪', '鷦', '祩', '籋', '襘', '餫', '睱', '睻', '磠', '絣', '莕', '錧', '骣', '騊', '魿']
    print(f"Length of actual missing chars: {len(actual_missing_chars)}")

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
        if count == 5000: 
            break

    # Save the deck to a file
    package = genanki.Package(deck)
    # Add the font file to the package
    package.write_to_file('chinese_characters.apkg')
    print(f"Created deck with {len(char_data)} characters")
    print(f"Missing characters: {missing_chars}")

def main():
    create_char_deck()

if __name__ == "__main__":
    main()