import re
import os


def parse_h_file(filename):
    """Парсит .h файл и извлекает данные шрифта"""
    with open(filename, 'r') as f:
        content = f.read()

    # Извлекаем данные font_data
    font_data_match = re.search(r'static const unsigned char font_data\[\] = \{([^}]+)\}', content, re.DOTALL)
    if not font_data_match:
        raise ValueError("Не найден массив font_data в файле")

    font_data_str = font_data_match.group(1)
    # Извлекаем числа из массива
    numbers = re.findall(r'0x[0-9A-Fa-f]+|\d+', font_data_str)
    font_data = [int(num, 16) if 'x' in num else int(num) for num in numbers]

    # Извлекаем данные glyphs
    glyphs_match = re.search(r'static const struct \{[^}]+\} glyphs\[\] = \{(.+?)\};', content, re.DOTALL)
    if not glyphs_match:
        # Попробуем другой вариант поиска
        glyphs_match = re.search(r'glyphs\[\] = \{(.+?)\};', content, re.DOTALL)
        if not glyphs_match:
            raise ValueError("Не найден массив glyphs в файле")

    glyphs_str = glyphs_match.group(1)
    print(f"DEBUG: glyphs_str = {repr(glyphs_str)}")  # Для отладки

    # Извлекаем записи glyphs - более гибкое регулярное выражение
    glyph_matches = re.findall(r'\{\s*([^,}]+?)\s*,\s*([^,}]+?)\s*,\s*([^,}]+?)\s*\}', glyphs_str)

    glyphs = []
    for match in glyph_matches:
        # Очищаем значения от комментариев и лишних символов
        ascii_code_str = match[0].split()[0].strip()
        width_str = match[1].split()[0].strip()
        bit_offset_str = match[2].split()[0].strip()

        ascii_code = int(ascii_code_str, 16) if 'x' in ascii_code_str.lower() else int(ascii_code_str)
        width = int(width_str, 16) if 'x' in width_str.lower() else int(width_str)
        bit_offset = int(bit_offset_str, 16) if 'x' in bit_offset_str.lower() else int(bit_offset_str)

        glyphs.append({
            'ascii_code': ascii_code,
            'width': width,
            'bit_offset': bit_offset
        })

    return font_data, glyphs


def get_bit(data, bit_index):
    """Получает значение бита по индексу из массива байтов"""
    byte_index = bit_index // 8
    bit_position = bit_index % 8
    if byte_index >= len(data):
        return 0
    return (data[byte_index] >> bit_position) & 1


def display_glyph(font_data, glyph):
    """Отображает символ в консоли"""
    height = font_data[0]  # Первый байт - высота
    #font_bits = font_data[1:]  # Остальные байты - битовый поток

    char_display = chr(glyph['ascii_code']) if 32 <= glyph['ascii_code'] <= 126 else f"\\x{glyph['ascii_code']:02X}"
    print(f"Символ: {char_display} (ASCII: {glyph['ascii_code']})")
    print(f"Размер: {glyph['width']}x{height}")
    print("Изображение:")

    for y in range(height):
        line = ""
        for x in range(glyph['width']):
            bit_index = glyph['bit_offset'] + y * glyph['width'] + x
            bit_value = get_bit(font_data, bit_index)
            line += "@" if bit_value == 1 else "."
        print(line)
    print()


def list_h_files(directory="."):
    """Список всех .h файлов в директории"""
    h_files = [f for f in os.listdir(directory) if f.endswith('.h')]
    return h_files


def main():
    print("Просмотр шрифтов")
    print("=" * 50)

    # Выбор директории
    current_dir = "."

    while True:
        # Список .h файлов
        h_files = list_h_files(current_dir)

        if not h_files:
            print("В текущей директории не найдено .h файлов")
            return

        print("\nДоступные файлы:")
        for i, filename in enumerate(h_files):
            print(f"{i + 1}. {filename}")
        print("0. Выход")

        try:
            choice = input("\nВыберите файл (номер): ").strip()
            if choice == "0":
                break

            choice = int(choice)
            if 1 <= choice <= len(h_files):
                filename = h_files[choice - 1]

                try:
                    # Парсим файл
                    font_data, glyphs = parse_h_file(filename)
                    print(f"\nЗагружен файл: {filename}")
                    print(f"Высота шрифта: {font_data[0]} пикселей")
                    print(f"Количество символов: {len(glyphs)}")

                    if len(glyphs) == 0:
                        print("WARNING: Не найдено символов!")
                        print("Попробуйте проверить формат файла")

                    while True:
                        print("\nДоступные символы:")
                        for i, glyph in enumerate(glyphs):
                            char = chr(glyph['ascii_code']) if 32 <= glyph[
                                'ascii_code'] <= 126 else f"\\x{glyph['ascii_code']:02X}"
                            print(f"{i + 1}. {char} (ASCII {glyph['ascii_code']})")
                        print("0. Назад к выбору файла")

                        glyph_choice = input("\nВыберите символ для отображения (номер): ").strip()
                        if glyph_choice == "0":
                            break

                        try:
                            glyph_choice = int(glyph_choice)
                            if 1 <= glyph_choice <= len(glyphs):
                                display_glyph(font_data, glyphs[glyph_choice - 1])
                                input("Нажмите Enter для продолжения...")
                            else:
                                print("Неверный выбор символа")
                        except ValueError:
                            print("Пожалуйста, введите число")
                except Exception as e:
                    print(f"Ошибка при чтении файла: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Неверный выбор файла")
        except ValueError:
            print("Пожалуйста, введите число")
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()