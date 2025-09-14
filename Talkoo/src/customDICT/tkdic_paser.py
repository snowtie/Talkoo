from utils.logger import info, debug, error

def parse_tkdic(file_path):
    final_results = []
    current_entry = {}
    is_reading_word = False
    main_fuzzy_value = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip() 
            if is_reading_word:
                info("word 객체를 읽는중..")
                if line.endswith(']'):
                    debug(f"읽어온 라인 : {line}")
                    content = line[:-1]
                    debug(f"최종 단어 : {content}")
                    current_entry['word'] += content
                    is_reading_word = False
                else:
                    info("word 객체를 읽고있지 않음")
                    current_entry['word'] += line + ' '
                    debug(f"읽어온 라인 : {line}")

            else:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('main_fuzzy['):
                    main_fuzzy_value = int(parse_tag_value(line))
                
                elif line.startswith('word['):
                    if current_entry and 'word' in current_entry:
                        final_results.append(current_entry)
                    current_entry = {}

                    current_entry['word'] = parse_tag_value(line)

                    if not line.endswith(']'):
                        current_entry['word'] += ' '
                        is_reading_word = True

                elif line.startswith('kor['):
                    current_entry['kor'] = parse_tag_value(line)

                elif line.startswith('fuzzy['):
                    current_entry['fuzzy'] = int(parse_tag_value(line))
                    
        if current_entry:
            final_results.append(current_entry)

        info(f"{main_fuzzy_value}, {final_results}")
        return main_fuzzy_value, final_results
                     
                    
    return final_results

def parse_tag_value(line: str) -> str:
    try:
        start = line.find('[') + 1 
        end = line.rfind(']')
        
        if end == -1:
            return line[start:]
        else:
            return line[start:end]
    except:
        return ""
        