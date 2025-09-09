import re
import sys

def escape_hyphen(text):
    """Экранирует только дефис для регулярных выражений"""
    return text.replace('-', r'\-')

def parse_hex_array(content, array_name):
    """Парсит массив hex значений из C кода"""
    escaped_name = escape_hyphen(array_name)
    # Ищем начало массива
    start_pattern = f'static const unsigned char {escaped_name}\\s*\\[\\s*\\]\\s*=\\s*\\{{'
    start_match = re.search(start_pattern, content, re.DOTALL)
    if not start_match:
        return None
    
    # Находим начало данных (после открывающей скобки)
    start_pos = start_match.end()
    # Ищем соответствующую закрывающую скобку
    brace_count = 1
    pos = start_pos
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count != 0:
        return None
    
    # Извлекаем данные между скобками
    data_str = content[start_pos:pos-1]
    # Извлекаем hex значения
    hex_values = re.findall(r'0x[0-9A-Fa-f]{2}', data_str)
    return [int(x, 16) for x in hex_values]

def parse_glyphs_array(content, array_name):
    """Парсит массив глифов из C кода"""
    escaped_name = escape_hyphen(array_name)
    # Ищем начало массива
    start_pattern = f'static const glyphs_t\\s+{escaped_name}\\s*\\[\\s*\\]\\s*=\\s*\\{{'
    start_match = re.search(start_pattern, content, re.DOTALL)
    if not start_match:
        print(f"DEBUG: Pattern not found. Looking for pattern: {start_pattern}")
        return None
    
    # Находим начало данных (после открывающей скобки)
    start_pos = start_match.end()
    # Ищем соответствующую закрывающую скобку
    brace_count = 1
    pos = start_pos
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count != 0:
        return None
    
    # Извлекаем данные между скобками
    data_str = content[start_pos:pos-1]
    glyphs = []
    
    # Ищем все структуры { код, ширина, смещение }
    pattern_glyph = r'\{\s*0x([0-9A-Fa-f]{2})\s*,\s*(\d+)\s*,\s*(\d+)\s*\}'
    matches = re.findall(pattern_glyph, data_str)
    
    for match in matches:
        ascii_code = int(match[0], 16)
        width = int(match[1])
        bit_offset = int(match[2])
        glyphs.append({
            'ascii_code': ascii_code,
            'width': width,
            'bit_offset': bit_offset
        })
    
    return glyphs

def parse_font_descriptor(content, descriptor_name):
    """Парсит дескриптор шрифта"""
    escaped_name = escape_hyphen(descriptor_name)
    # Ищем начало структуры
    start_pattern = f'static const font_descriptor_t\\s+{escaped_name}\\s*=\\s*\\{{'
    start_match = re.search(start_pattern, content, re.DOTALL)
    if not start_match:
        return None
    
    # Находим начало данных (после открывающей скобки)
    start_pos = start_match.end()
    # Ищем соответствующую закрывающую скобку
    brace_count = 1
    pos = start_pos
    while pos < len(content) and brace_count > 0:
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1
    
    if brace_count != 0:
        return None
    
    # Извлекаем данные между скобками
    data_str = content[start_pos:pos-1]
    
    # Извлекаем все числа
    numbers = re.findall(r'(\d+)', data_str)
    
    if len(numbers) >= 3:
        return {
            'font_data_size': int(numbers[-3]),
            'glyphs_num': int(numbers[-2]),
            'font_height': int(numbers[-1])
        }
    return None
    
def get_bit(bitmap_data, bit_index):
    """Получает значение бита по индексу из массива байтов"""
    byte_index = bit_index // 8
    bit_position = bit_index % 8
    
    if byte_index >= len(bitmap_data):
        return 0
    
    return (bitmap_data[byte_index] >> bit_position) & 1

def visualize_glyph(font_data, glyph, height):
    """Визуализирует глиф в консоли"""
    try:
        char_display = chr(glyph['ascii_code'])
        if not (32 <= glyph['ascii_code'] <= 126):
            char_display = '<?>'
    except:
        char_display = '<?>'
        
    print(f"Character '{char_display}' (ASCII: {glyph['ascii_code']}, CP1251: 0x{glyph['ascii_code']:02X})")
    print(f"Width: {glyph['width']}, Bit offset: {glyph['bit_offset']}")
    
    for row in range(height):
        line = ""
        for col in range(glyph['width']):
            bit_index = glyph['bit_offset'] + row * glyph['width'] + col
            bit_value = get_bit(font_data, bit_index)
            line += "█" if bit_value else "."
        print(line)
    print()

def main():
    if len(sys.argv) != 2:
        print("Usage: python font_check.py <font_header_file.h>")
        return
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Извлекаем имя шрифта из имени файла
    import os
    font_name = os.path.splitext(os.path.basename(filename))[0]
    if font_name.startswith('font_'):
        font_name = font_name[5:]  # убираем 'font_'
    
    # Находим высоту из имени файла (последняя часть после _)
    parts = font_name.split('_')
    if len(parts) > 1 and parts[-1].isdigit():
        height = int(parts[-1])
        font_name_without_height = '_'.join(parts[:-1])
    else:
        height = 8  # значение по умолчанию
        font_name_without_height = font_name
    
    # Имена переменных без высоты
    font_data_var = f"font_data_{font_name_without_height}"
    glyphs_var = f"glyphs_{font_name_without_height}"
    descriptor_var = f"font_{font_name_without_height}"
    
    print(f"Parsing arrays: {font_data_var}, {glyphs_var}, {descriptor_var}")
    
    # Парсим данные
    font_data = parse_hex_array(content, font_data_var)
    glyphs = parse_glyphs_array(content, glyphs_var)
    descriptor = parse_font_descriptor(content, descriptor_var)
    height = descriptor['font_height']
    if font_data is None:
        print(f"Error: Could not parse font data array '{font_data_var}'")
        return
    
    if glyphs is None:
        print(f"Error: Could not parse glyphs array '{glyphs_var}'")
        return
    
    if descriptor is None:
        print(f"Warning: Could not parse font descriptor '{descriptor_var}'")
    
    print(f"Font file: {filename}")
    print(f"Font name: {font_name_without_height}")
    print(f"Height: {height}")
    print(f"Font data size: {len(font_data)} bytes")
    print(f"Number of glyphs: {len(glyphs)}")
    if descriptor:
        print(f"Descriptor - Data size: {descriptor['font_data_size']}, Glyphs: {descriptor['glyphs_num']}, Height: {descriptor['font_height']}")
    print("=" * 50)
    
    # Визуализируем несколько первых глифов
    num_to_show = min(10, len(glyphs))
    print(f"Showing first {num_to_show} glyphs:")
    print()
    
    for i in range(num_to_show):
        visualize_glyph(font_data, glyphs[i], height)
    
    # Показываем последние несколько глифов
    if len(glyphs) > num_to_show:
        print("..." )
        print("Showing last few glyphs:")
        for i in range(max(0, len(glyphs) - 3), len(glyphs)):
            visualize_glyph(font_data, glyphs[i], height)

if __name__ == "__main__":
    main()