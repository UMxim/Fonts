import os
import sys
from PIL import Image, ImageDraw, ImageFont

class FontGeneratorMenu:
    def __init__(self):
        self.fonts_dir = "fonts"
        self.selected_font = None
        self.settings = {
            'height': 16,
            'include_cyrillic': True,
            'output_format': 'header',
            'page_size': 128
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
        ext = filename.lower()
        types = {
            '.ttf': 'TrueType',
            '.otf': 'OpenType',
            '.bdf': 'Bitmap',
            '.pcf': 'Bitmap',
            '.fon': 'Windows'
        }
        return types.get(ext, 'Unknown')
    
    def show_main_menu(self):
        """Показывает главное меню"""
        while True:
            print("\n" + "="*50)
            print("МЕНЮ ГЕНЕРАТОРА ШРИФТОВ")
            print("="*50)
            print("1. Выбрать шрифт")
            print("2. Настройки генерации")
            print("3. Информация о шрифте")
            print("4. Сгенерировать")
            print("5. Выход")
            print("-"*50)
            
            choice = input("Выберите пункт меню (1-5): ").strip()
            
            if choice == '1':
                self.select_font_menu()
            elif choice == '2':
                self.select_symbol_set()
            elif choice == '3':
                self.show_font_info()
            elif choice == '4':
                self.generate_font()
            elif choice == '5':
                print("До свидания!")
                sys.exit(0)
            else:
                print("Неверный выбор!")
    
    def select_font_menu(self):
        """Меню выбора шрифта"""
        while True:
            print("\nВЫБОР ШРИФТА")
            print("="*30)
            print("1. Из списка доступных")
            print("2. Указать путь вручную")
            print("3. Назад")
            print("-"*30)
            
            choice = input("Выберите способ (1-3): ").strip()
            
            if choice == '1':
                self.select_from_list()
                break
            elif choice == '2':
                self.select_manual_path()
                break
            elif choice == '3':
                break
            else:
                print("Неверный выбор!")
    
    def select_from_list(self):
        """Выбор шрифта из списка с навигацией по папкам"""
        current_dir = self.fonts_dir
        while True:
            items = self.scan_fonts_directory(current_dir)
            
            if not items:
                print("Папка пуста")
                return
            
            print(f"\nСОДЕРЖИМОЕ: {os.path.relpath(current_dir, self.fonts_dir) or '.'}")
            print("="*50)
            
            # Показать путь навигации
            if current_dir != self.fonts_dir:
                print("0. .. (на уровень выше)")
            
            for i, item in enumerate(items, 1):
                if item['type'] == 'directory':
                    print(f"{i}. [Папка] {item['name']}/")
                else:
                    print(f"{i}. {item['name']} ({item['font_type']})")
            
            print("="*50)
            
            try:
                choice = input("Выберите пункт (0-{} или 'b' для возврата): ".format(len(items))).strip()
                
                if choice.lower() == 'b':
                    return
                
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
                    print("Неверный номер!")
            except ValueError:
                print("Неверный ввод!")
    
    def select_manual_path(self):
        """Выбор шрифта по пути вручную"""
        path = input("Введите путь к файлу шрифта: ").strip()
        
        if os.path.exists(path) and os.path.isfile(path):
            filename = os.path.basename(path)
            self.selected_font = {
                'name': filename,
                'path': path,
                'relative_path': path,
                'type': 'file',
                'font_type': self.get_font_type(filename)
            }
            print(f"Выбран шрифт: {self.selected_font['name']}")
        else:
            print("Файл не найден!")
    
    def settings_menu(self):
        """Меню настроек"""
        while True:
            print("\nНАСТРОЙКИ ГЕНЕРАЦИИ")
            print("="*30)
            print(f"1. Высота шрифта: {self.settings['height']}px")
            print(f"2. Включить кириллицу: {'Да' if self.settings['include_cyrillic'] else 'Нет'}")
            print(f"3. Размер страницы: {self.settings['page_size']} байт")
            print("4. Назад")
            print("-"*30)
            
            choice = input("Выберите настройку (1-4): ").strip()
            
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
                self.settings['include_cyrillic'] = not self.settings['include_cyrillic']
            elif choice == '3':
                try:
                    size = int(input("Введите размер страницы (64-1024): ").strip())
                    if 64 <= size <= 1024:
                        self.settings['page_size'] = size
                    else:
                        print("Размер должен быть от 64 до 1024!")
                except ValueError:
                    print("Неверный ввод!")
            elif choice == '4':
                break
            else:
                print("Неверный выбор!")
    
    def show_font_info(self):
        """Показ информации о шрифте"""
        if not self.selected_font:
            print("Шрифт не выбран!")
            return
        
        print("\nИНФОРМАЦИЯ О ШРИФТЕ")
        print("="*40)
        print(f"Имя файла: {self.selected_font['name']}")
        print(f"Путь: {self.selected_font['relative_path']}")
        print(f"Тип: {self.selected_font.get('font_type', 'Unknown')}")
        print(f"Высота: {self.settings['height']}px")
        print("="*40)
    
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
    
    def generate_font_bitmap(self, font_path, height):
        """Генерирует bitmap данных шрифта"""
        try:
            font = ImageFont.truetype(font_path, height)
        except:
            # Если TTF не работает, пробуем другие методы
            print("Не удалось загрузить шрифт как TrueType")
            return None

        chars = []
        
        # ASCII символы (32-126)
        for i in range(32, 127):
            chars.append(chr(i))
        
        # Русские буквы если включены
        if self.settings['include_cyrillic']:
            for i in range(ord('А'), ord('я') + 1):
                chars.append(chr(i))
            additional_chars = ['Ё', 'ё']
            chars.extend(additional_chars)

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
        
        try:
            font_data = self.generate_font_bitmap(self.selected_font['path'], self.settings['height'])
            if font_data:
                font_name = os.path.splitext(self.selected_font['name'])[0]
                self.save_to_header_file(font_data, font_name, self.settings['height'])
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