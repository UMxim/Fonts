import os
import sys
from PIL import Image, ImageDraw, ImageFont


class BDFParser:
    def __init__(self, font_path, symbol_list):
        self.font_path = font_path
        self.symbol_list = symbol_list
        # Преобразуем символы в CP1251 коды для фильтрации
        self.symbol_cp1251_codes = set()
        for c in symbol_list:
            try:
                cp1251_bytes = c.encode('windows-1251')
                cp1251_code = cp1251_bytes[0]
                self.symbol_cp1251_codes.add(cp1251_code)
            except UnicodeEncodeError:
                # Если символ не кодируется в CP1251, пропускаем
                pass
        self.glyphs = []
        self.font_height = 0
        self.font_width = 0

    def unicode_to_cp1251(self, unicode_code):
        """Преобразует Unicode код в CP1251 код"""
        try:
            char = chr(unicode_code)
            cp1251_bytes = char.encode('windows-1251')
            return cp1251_bytes[0]
        except (UnicodeEncodeError, UnicodeDecodeError):
            return None

    def parse_glyph(self, lines, start_index):
        """Парсит один глиф из BDF файла"""
        glyph = {
            'encoding': -1,  # Unicode код
            'cp1251_code': -1,  # CP1251 код
            'width': 0,
            'height': 0,
            'bitmap': []  # hex строки данных
        }

        i = start_index
        in_bitmap = False

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith('ENCODING '):
                unicode_code = int(line.split()[1])
                glyph['encoding'] = unicode_code
                # Преобразуем в CP1251
                cp1251_code = self.unicode_to_cp1251(unicode_code)
                if cp1251_code is not None:
                    glyph['cp1251_code'] = cp1251_code

            elif line.startswith('BBX '):
                parts = line.split()
                glyph['width'] = int(parts[1])
                glyph['height'] = int(parts[2])

            elif line == 'BITMAP':
                in_bitmap = True
                glyph['bitmap'] = []

            elif line == 'ENDCHAR':
                if in_bitmap and glyph['encoding'] != -1:
                    return glyph, i + 1
                break
            elif in_bitmap:
                glyph['bitmap'].append(line)

            i += 1

        return None, i + 1

    def parse_font(self):
        """Парсит BDF файл и возвращает массив глифов для нужных символов"""
        try:
            with open(self.font_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Ищем размеры шрифта
            for line in lines:
                if line.startswith('FONTBOUNDINGBOX '):
                    parts = line.split()
                    self.font_width = int(parts[1])
                    self.font_height = int(parts[2])
                    break

            # Парсим глифы
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('STARTCHAR'):
                    glyph, next_i = self.parse_glyph(lines, i)
                    if glyph and glyph['encoding'] != -1 and glyph['cp1251_code'] != -1:
                        # Фильтруем по CP1251 кодам
                        if (not self.symbol_cp1251_codes or
                                glyph['cp1251_code'] in self.symbol_cp1251_codes):
                            self.glyphs.append(glyph)
                    i = next_i
                else:
                    i += 1

            return self.glyphs, self.font_height, self.font_width

        except Exception as e:
            print(f"Ошибка при парсинге BDF файла: {e}")
            return [], 0, 0


class FontGeneratorMenu:
    def __init__(self):
        self.fonts_dir = "fonts"
        self.selected_font = None
        self.settings = {
            'height': 8,
            'symbol_set': 1,  # по умолчанию только цифры
            'custom_symbols': ""  # для пользовательского набора
        }
        if not os.path.exists(self.fonts_dir):
            os.makedirs(self.fonts_dir)


    def scan_fonts_directory(self, directory=None):
        """Сканирует директорию на наличие BDF шрифтов и папок"""
        if directory is None:
            directory = self.fonts_dir

        items = []
        supported_extensions = ['.bdf']  # Только BDF файлы

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
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        types = {
            '.bdf': 'Bitmap Distribution Format'
        }
        return types.get(ext, 'Unknown')

    def show_main_menu(self):
        """Показывает главное меню"""
        while True:
            print("\n" + "=" * 50)
            print("МЕНЮ ГЕНЕРАТОРА ШРИФТОВ (только BDF)")
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
                print("Папка пуста или не содержит BDF файлов")
                return

            rel_path = os.path.relpath(current_dir, self.fonts_dir)
            if rel_path == '.':
                display_path = '.'
            else:
                display_path = rel_path

            print(f"\nСОДЕРЖИМОЕ: {display_path}")
            print("=" * 50)

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
                return

    def settings_menu(self):
        """Меню настроек"""
        while True:
            symbol_set_names = {
                1: "Только цифры",
                2: "Цифры и английские буквы",
                3: "Все символы (латиница + кириллица)",
                4: "Свой выбор"
            }

            # Определяем отображаемое имя набора символов
            if isinstance(self.settings['symbol_set'], int):
                symbol_set_display = symbol_set_names.get(self.settings['symbol_set'], "Не выбран")
            else:
                symbol_set_display = "Пользовательский"

            print("\nНАСТРОЙКИ ГЕНЕРАЦИИ")
            print("=" * 40)
            print(f"1. Высота шрифта: {self.settings['height']}px")
            print(f"2. Набор символов: {symbol_set_display}")
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
                if choice == 4:
                    symbols = input("Введите свой набор символов: ")
                    # Не используем strip() вообще, чтобы сохранить все пробелы
                    self.settings['symbol_set'] = symbols
                    self.settings['custom_symbols'] = symbols
                    print(f"Выбран набор длиной: {len(symbols)} символов")
                else:
                    self.settings['symbol_set'] = choice
                    self.settings['custom_symbols'] = ""
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

        # Определяем отображаемое имя набора символов
        if isinstance(self.settings['symbol_set'], int):
            symbol_set_display = symbol_set_names.get(self.settings['symbol_set'], "Не выбран")
        else:
            symbol_set_display = "Пользовательский"

        print("\nИНФОРМАЦИЯ О ШРИФТЕ")
        print("=" * 40)
        print(f"Имя файла: {self.selected_font['name']}")
        print(f"Путь: {self.selected_font['relative_path']}")
        print(f"Тип: {self.selected_font.get('font_type', 'Unknown')}")
        print(f"Высота: {self.settings['height']}px")
        print(f"Набор символов: {symbol_set_display}")
        if not isinstance(self.settings['symbol_set'], int) and self.settings['custom_symbols']:
            print(f"Пользовательский набор: {self.settings['custom_symbols']}")
        print("=" * 40)

    def get_symbol_list(self):
        """Возвращает список символов в зависимости от настроек"""
        if isinstance(self.settings['symbol_set'], int):
            pos = self.settings['symbol_set']
            if pos == 1:
                return [chr(i) for i in range(ord('0'), ord('9') + 1)]
            elif pos == 2:
                digits = [chr(i) for i in range(ord('0'), ord('9') + 1)]
                uppercase = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
                lowercase = [chr(i) for i in range(ord('a'), ord('z') + 1)]
                return digits + uppercase + lowercase
            elif pos == 3:
                digits = [chr(i) for i in range(ord('0'), ord('9') + 1)]
                uppercase = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
                lowercase = [chr(i) for i in range(ord('a'), ord('z') + 1)]
                cyrillic_upper = [chr(i) for i in range(ord('А'), ord('Я') + 1)]
                cyrillic_lower = [chr(i) for i in range(ord('а'), ord('я') + 1)]
                additional = ['Ё', 'ё']
                return digits + uppercase + lowercase + cyrillic_upper + cyrillic_lower + additional
            elif pos == 4:
                return list(self.settings['custom_symbols']) if self.settings['custom_symbols'] else []
        else:
            # Пользовательский набор
            symbols = self.settings['symbol_set']
            return list(symbols) if symbols else []  # list() преобразует строку в список символов
        return []

    def generate_font_bitmap(self, font_path, height):
        """Генерирует массив глифов из BDF файла"""
        # Получаем список нужных символов
        symbol_list = self.get_symbol_list()

        # Создаем парсер и парсим шрифт
        parser = BDFParser(font_path, symbol_list)
        glyphs, font_height, font_width = parser.parse_font()

        return glyphs, font_height, font_width

    def save_to_header_file(self, font_data, font_name, height):
        """Сохраняет шрифт в C header файл"""
        safe_font_name = "".join(c for c in font_name if c.isalnum() or c in "._-")
        filename = f"font_{safe_font_name}_{height}.h"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"// Font: {font_name}, Height: {height}px\n")
            f.write("// Generated by Python font rasterizer\n")
            f.write(f"// Total glyphs: {len(font_data)}\n\n")

            # Собираем все байты данных
            all_bytes = []
            offsets = []
            current_offset = 1  # начинаем с 1, так как 0 - высота шрифта

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

            # Записываем данные шрифта
            f.write("static const unsigned char font_data[] = {\n")
            f.write(f"    {height}")  # высота шрифта

            if all_bytes:  # если есть данные
                f.write(",\n")
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
            else:
                f.write("\n")
            f.write("};\n\n")

            # Записываем информацию о глифах
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

        # Определяем отображаемое имя набора символов
        if isinstance(self.settings['symbol_set'], int):
            symbol_set_display = symbol_set_names.get(self.settings['symbol_set'], "не выбран")
        else:
            symbol_set_display = "пользовательский"

        print(f"Набор символов: {symbol_set_display}")

        try:
            font_data = self.generate_font_bitmap(self.selected_font['path'], self.settings['height'])
            if font_data:
                # Определяем высоту для сохранения
                actual_height = self.settings['height']

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