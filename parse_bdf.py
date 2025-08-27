import os
import sys
from PIL import Image, ImageDraw, ImageFont


class FontGeneratorMenu:
    def __init__(self):
        self.fonts_dir = "fonts"
        self.selected_font = None
        self.settings = {
            'height': 8,
            'symbol_set': 3,  # 1-цифры, 2-латиница, 3-кириллица, 4-свой выбор
            'custom_symbols': ''
        }
        self.setup_fonts_directory()

    def setup_fonts_directory(self):
        """Создает директорию fonts если её нет"""
        if not os.path.exists(self.fonts_dir):
            os.makedirs(self.fonts_dir)

    def scan_fonts_directory(self, directory=None):
        """Сканирует директорию на наличие шрифтов и папок"""
        if directory is None:
            directory = self.fonts_dir

        items = []
        supported_extensions = ['.ttf', '.otf', '.bdf', '.pcf', '.fon']

        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                relative_path = os.path.relpath(full_path, self.fonts_dir)

                if os.path.isdir(full_path):
                    items.append({
                        'type': 'directory',
                        'name': item,
                        'path': full_path,
                        'relative_path': relative_path
                    })
                elif os.path.isfile(full_path):
                    if any(item.lower().endswith(ext) for ext in supported_extensions):
                        items.append({
                            'type': 'file',
                            'name': item,
                            'path': full_path,
                            'relative_path': relative_path,
                            'font_type': self.get_font_type(item)
                        })
        except Exception as e:
            print(f"Ошибка сканирования директории: {e}")
            return []

        return sorted(items, key=lambda x: (x['type'], x['name']))

    def get_font_type(self, filename):
        """Определяет тип шрифта по расширению"""
        # Получаем расширение файла
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        types = {
            '.ttf': 'TrueType',
            '.otf': 'OpenType',
            '.bdf': 'Bitmap Distribution Format',
            '.pcf': 'Portable Compiled Format',
            '.fon': 'Windows Font'
        }
        return types.get(ext, 'Unknown')

    def show_main_menu(self):
        """Показывает главное меню"""
        while True:
            print("\n" + "=" * 50)
            print("МЕНЮ ГЕНЕРАТОРА ШРИФТОВ")
            print("=" * 50)
            print("1. Выбрать шрифт")
            print("2. Настройки генерации")
            print("3. Информация о шрифте")
            print("4. Сгенерировать")
            print("5. Выход")
            print("-" * 50)

            choice = input("Выберите пункт меню (1-5): ").strip()

            if choice == '1':
                self.select_font()
            elif choice == '2':
                self.settings_menu()
            elif choice == '3':
                self.show_font_info()
            elif choice == '4':
                self.generate_font()
            elif choice == '5':
                print("До свидания!")
                sys.exit(0)
            else:
                print("Неверный выбор!")

    def select_font(self):
        """Выбор шрифта с навигацией по папкам"""
        current_dir = self.fonts_dir
        while True:
            items = self.scan_fonts_directory(current_dir)

            if not items:
                print("Папка пуста")
                return

            # Показываем относительный путь от fonts или "." если в корне fonts
            rel_path = os.path.relpath(current_dir, self.fonts_dir)
            if rel_path == '.':
                display_path = '.'
            else:
                display_path = rel_path

            print(f"\nСОДЕРЖИМОЕ: {display_path}")
            print("=" * 50)

            # Показать путь навигации
            if current_dir != self.fonts_dir:
                print("0. .. (на уровень выше)")

            for i, item in enumerate(items, 1):
                if item['type'] == 'directory':
                    print(f"{i}. [Папка] {item['name']}/")
                else:
                    print(f"{i}. {item['name']} ({item['font_type']})")

            print("=" * 50)
            print("Введите номер для выбора или другое для возврата в главное меню")

            try:
                choice = input("Выберите пункт: ").strip()


                if choice == '0' and current_dir != self.fonts_dir:
                    current_dir = os.path.dirname(current_dir)
                    continue

                index = int(choice) - 1
                if 0 <= index < len(items):
                    item = items[index]
                    if item['type'] == 'directory':
                        current_dir = item['path']
                    else:
                        self.selected_font = item
                        print(f"Выбран шрифт: {self.selected_font['name']}")
                        return
                else:
                    return
            except ValueError:
                print("Неверный ввод!")

    def settings_menu(self):
        """Меню настроек"""
        while True:
            symbol_set_names = {
                1: "Только цифры",
                2: "Цифры и английские буквы",
                3: "Все символы (латиница + кириллица)",
                4: "Свой выбор"
            }

            print("\nНАСТРОЙКИ ГЕНЕРАЦИИ")
            print("=" * 40)
            print(f"1. Высота шрифта: {self.settings['height']}px")
            print(f"2. Набор символов: {symbol_set_names[self.settings['symbol_set']]}")
            if self.settings['symbol_set'] == 4:
                print(
                    f"   Текущий набор: {self.settings['custom_symbols'] if self.settings['custom_symbols'] else '(не задан)'}")
            print("3. Назад")
            print("-" * 40)

            choice = input("Выберите настройку (1-3): ").strip()

            if choice == '1':
                try:
                    height = int(input("Введите высоту шрифта (8-64): ").strip())
                    if 8 <= height <= 64:
                        self.settings['height'] = height
                    else:
                        print("Высота должна быть от 8 до 64!")
                except ValueError:
                    print("Неверный ввод!")
            elif choice == '2':
                self.select_symbol_set()
            elif choice == '3':
                break
            else:
                print("Неверный выбор!")

    def select_symbol_set(self):
        """Выбор набора символов"""
        print("\nВЫБОР НАБОРА СИМВОЛОВ")
        print("=" * 30)
        print("1. Только цифры (0-9)")
        print("2. Цифры и английские буквы (0-9, A-Z, a-z)")
        print("3. Все символы (0-9, A-Z, a-z, А-Я, а-я, Ё, ё)")
        print("4. Свой выбор")
        print("-" * 30)

        try:
            choice = int(input("Выберите вариант (1-4): ").strip())
            if 1 <= choice <= 4:
                self.settings['symbol_set'] = choice
                if choice == 4:
                    symbols = input("Введите свой набор символов: ").strip()
                    self.settings['custom_symbols'] = symbols
            else:
                print("Неверный выбор!")
        except ValueError:
            print("Неверный ввод!")

    def show_font_info(self):
        """Показ информации о шрифте"""
        if not self.selected_font:
            print("Шрифт не выбран!")
            return

        symbol_set_names = {
            1: "Только цифры",
            2: "Цифры и английские буквы",
            3: "Все символы (латиница + кириллица)",
            4: "Свой выбор"
        }

        print("\nИНФОРМАЦИЯ О ШРИФТЕ")
        print("=" * 40)
        print(f"Имя файла: {self.selected_font['name']}")
        print(f"Путь: {self.selected_font['relative_path']}")
        print(f"Тип: {self.selected_font.get('font_type', 'Unknown')}")
        print(f"Высота: {self.settings['height']}px")
        print(f"Набор символов: {symbol_set_names[self.settings['symbol_set']]}")
        if self.settings['symbol_set'] == 4 and self.settings['custom_symbols']:
            print(f"Пользовательский набор: {self.settings['custom_symbols']}")
        print("=" * 40)

    def parse_bdf_glyph(self, lines, start_index):
        """Парсит один глиф из BDF файла"""
        glyph = {
            'encoding': -1,
            'width': 0,
            'height': 0,
            'bitmap': []
        }

        i = start_index
        in_bitmap = False
        bitmap_rows = []

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('ENCODING '):
                glyph['encoding'] = int(line.split()[1])
            elif line.startswith('BBX '):
                parts = line.split()
                glyph['width'] = int(parts[1])
                glyph['height'] = int(parts[2])
            elif line == 'BITMAP':
                in_bitmap = True
                bitmap_rows = []
            elif line == 'ENDCHAR':
                if in_bitmap and glyph['encoding'] != -1:
                    # Преобразуем hex строки в битовый массив
                    bitmap = []
                    for hex_row in bitmap_rows:
                        if hex_row:
                            hex_val = int(hex_row, 16)
                            row_bits = []
                            width = glyph['width']
                            # Младший бит = левый пиксель
                            for bit_pos in range(width):
                                bit_val = (hex_val >> bit_pos) & 1
                                row_bits.append(bit_val)
                            bitmap.append(row_bits)

                    glyph['bitmap'] = bitmap

                    # Преобразуем в байты
                    bitmap_bytes = []
                    for row in bitmap:
                        byte_row = []
                        for j in range(0, len(row), 8):
                            byte_val = 0
                            for k in range(min(8, len(row) - j)):
                                if row[j + k]:
                                    byte_val |= (1 << k)  # младший бит = левый пиксель
                            byte_row.append(byte_val)
                        bitmap_bytes.append(byte_row)

                    glyph['bitmap'] = bitmap_bytes
                    return glyph, i + 1
                break
            elif in_bitmap:
                bitmap_rows.append(line)

            i += 1

        return None, i + 1

    def parse_bdf_font(self, bdf_path):
        """Парсит BDF файл и возвращает данные шрифта"""
        try:
            with open(bdf_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            font_data = {}

            # Ищем высоту шрифта
            font_height = 16  # значение по умолчанию
            for line in lines:
                if line.startswith('FONTBOUNDINGBOX '):
                    parts = line.split()
                    font_height = int(parts[2])
                    break

            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('STARTCHAR'):
                    glyph, next_i = self.parse_bdf_glyph(lines, i)
                    if glyph and glyph['encoding'] != -1:
                        font_data[glyph['encoding']] = {
                            'bitmap': glyph['bitmap'],
                            'width': glyph['width'],
                            'height': len(glyph['bitmap']),
                            'char': chr(glyph['encoding']) if glyph['encoding'] < 128 else f'\\u{glyph["encoding"]:04x}'
                        }
                    i = next_i
                else:
                    i += 1

            return font_data, font_height

        except Exception as e:
            print(f"Ошибка при парсинге BDF файла: {e}")
            return None, 16

    def char_to_bitmap(self, char, font, height):
        """Преобразует символ в bitmap"""
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        if char_width == 0:
            char_width = height // 2

        img_width = char_width
        img_height = height
        img = Image.new("1", (img_width, img_height), color=0)
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, font=font, fill=1)

        pixels = list(img.getdata())
        width, height = img.size
        bitmap = []

        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[y * width + x]
                row.append(1 if pixel else 0)

            byte_row = []
            for i in range(0, len(row), 8):
                byte_val = 0
                for j in range(min(8, len(row) - i)):
                    if row[i + j]:
                        byte_val |= (1 << j)  # младший бит = левый пиксель
                byte_row.append(byte_val)
            bitmap.append(byte_row)

        return bitmap, width, height

    def get_symbol_list(self):
        """Возвращает список символов в зависимости от настроек"""
        if self.settings['symbol_set'] == 1:
            # Только цифры
            return [chr(i) for i in range(ord('0'), ord('9') + 1)]
        elif self.settings['symbol_set'] == 2:
            # Цифры и английские буквы
            digits = [chr(i) for i in range(ord('0'), ord('9') + 1)]
            uppercase = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
            lowercase = [chr(i) for i in range(ord('a'), ord('z') + 1)]
            return digits + uppercase + lowercase
        elif self.settings['symbol_set'] == 3:
            # Все символы (латиница + кириллица)
            digits = [chr(i) for i in range(ord('0'), ord('9') + 1)]
            uppercase = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
            lowercase = [chr(i) for i in range(ord('a'), ord('z') + 1)]
            cyrillic_upper = [chr(i) for i in range(ord('А'), ord('Я') + 1)]
            cyrillic_lower = [chr(i) for i in range(ord('а'), ord('я') + 1)]
            additional = ['Ё', 'ё']
            return digits + uppercase + lowercase + cyrillic_upper + cyrillic_lower + additional
        elif self.settings['symbol_set'] == 4:
            # Свой выбор
            return list(self.settings['custom_symbols'])
        return []

    def generate_font_bitmap(self, font_path, height):
        """Генерирует bitmap данных шрифта"""
        # Проверяем тип файла по расширению
        _, ext = os.path.splitext(font_path)
        ext = ext.lower()

        if ext == '.bdf':
            # Для BDF файлов используем парсинг
            font_data, actual_height = self.parse_bdf_font(font_path)
            # Фильтруем только нужные символы
            chars = self.get_symbol_list()
            chars_set = set(ord(c) for c in chars)
            filtered_font_data = {k: v for k, v in font_data.items() if k in chars_set}
            return filtered_font_data
        else:
            # Для других файлов используем PIL
            try:
                font = ImageFont.truetype(font_path, height)
            except:
                print("Не удалось загрузить шрифт")
                return None

            chars = self.get_symbol_list()
            font_data = {}

            for char in chars:
                try:
                    bitmap, width, height = self.char_to_bitmap(char, font, height)
                    font_data[ord(char)] = {
                        'bitmap': bitmap,
                        'width': width,
                        'height': height,
                        'char': char
                    }
                except Exception as e:
                    print(f"Ошибка при обработке символа '{char}': {e}")
                    continue

            return font_data

    def save_to_header_file(self, font_data, font_name, height):
        """Сохраняет шрифт в C header файл"""
        safe_font_name = "".join(c for c in font_name if c.isalnum() or c in "._-")
        filename = f"font_{safe_font_name}_{height}.h"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"// Font: {font_name}, Height: {height}px\n")
            f.write("// Generated by Python font rasterizer\n")
            f.write(f"// Total glyphs: {len(font_data)}\n\n")

            f.write("static const unsigned char font_data[] = {\n")
            f.write(f"    {height},  // height\n")

            all_bytes = []
            offsets = []
            current_offset = 1

            sorted_chars = sorted(font_data.keys())

            for char_code in sorted_chars:
                glyph = font_data[char_code]
                data = glyph['bitmap']
                flat_bytes = []
                for row in data:
                    flat_bytes.extend(row)

                offsets.append(current_offset)
                all_bytes.extend(flat_bytes)
                current_offset += len(flat_bytes)

            for i, byte in enumerate(all_bytes):
                if (i + 1) % 16 == 1:
                    f.write("    ")
                f.write(f"0x{byte:02X}")
                if i < len(all_bytes) - 1:
                    f.write(", ")
                if (i + 1) % 16 == 0:
                    f.write("\n")
            if len(all_bytes) % 16 != 0:
                f.write("\n")
            f.write("};\n\n")

            f.write("static const struct {\n")
            f.write("    unsigned char ascii_code;\n")
            f.write("    unsigned char width;\n")
            f.write("    unsigned short offset;\n")
            f.write("} glyphs[] = {\n")

            for i, char_code in enumerate(sorted_chars):
                glyph = font_data[char_code]
                width = glyph['width']
                offset = offsets[i]

                char_display = glyph['char']
                if char_display == '\\':
                    char_display = '\\\\'
                elif char_display == '"':
                    char_display = '\\"'
                elif char_display == "'":
                    char_display = "\\'"
                elif char_display == '\n':
                    char_display = '\\n'
                elif char_display == '\t':
                    char_display = '\\t'

                f.write(f"    {{ {char_code}, {width}, {offset} }}, // '{char_display}'\n")
            f.write("};\n")

        print(f"Файл {filename} успешно создан!")
        print(f"Всего символов: {len(font_data)}")
        return filename

    def generate_font(self):
        """Генерация шрифта"""
        if not self.selected_font:
            print("Шрифт не выбран!")
            return

        if self.selected_font['type'] != 'file':
            print("Выбран не файл шрифта!")
            return

        print(f"Генерация шрифта: {self.selected_font['name']}")
        print(f"Высота: {self.settings['height']}px")

        symbol_set_names = {
            1: "только цифры",
            2: "цифры и английские буквы",
            3: "все символы",
            4: "пользовательский набор"
        }
        print(f"Набор символов: {symbol_set_names[self.settings['symbol_set']]}")

        try:
            font_data = self.generate_font_bitmap(self.selected_font['path'], self.settings['height'])
            if font_data:
                # Определяем высоту для сохранения
                sample_glyph = next(iter(font_data.values()))
                actual_height = sample_glyph['height'] if font_data else self.settings['height']

                font_name = os.path.splitext(self.selected_font['name'])[0]
                self.save_to_header_file(font_data, font_name, actual_height)
                print("Генерация завершена!")
            else:
                print("Ошибка генерации шрифта!")
        except Exception as e:
            print(f"Ошибка генерации: {e}")


def main():
    menu = FontGeneratorMenu()
    menu.show_main_menu()


if __name__ == "__main__":
    main()