import tkinter as tk
from tkinter import filedialog, messagebox
import re

class Display:
    def __init__(self, canvas, scale=4):
        self.width = 128
        self.height = 64
        self.scale = scale
        self.canvas = canvas
        self.buffer = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.clear()
    
    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = 0
        self.canvas.delete("all")
        self.draw_grid()
    
    def draw_grid(self):
        """Рисует сетку пикселей"""
        # Вертикальные линии
        for x in range(0, self.width + 1):
            self.canvas.create_line(
                x * self.scale, 0,
                x * self.scale, self.height * self.scale,
                fill="lightgray", width=1, tags="grid"
            )
        
        # Горизонтальные линии
        for y in range(0, self.height + 1):
            self.canvas.create_line(
                0, y * self.scale,
                self.width * self.scale, y * self.scale,
                fill="lightgray", width=1, tags="grid"
            )
    
    def draw_pixel(self, x, y, color=1):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = color
    
    def render(self):
        self.canvas.delete("pixel")  # Удаляем только пиксели, сетка остается
        for y in range(self.height):
            for x in range(self.width):
                if self.buffer[y][x]:
                    self.canvas.create_rectangle(
                        x * self.scale, y * self.scale,
                        (x + 1) * self.scale, (y + 1) * self.scale,
                        fill="black", outline="", tags="pixel"
                    )

class Font:
    def __init__(self, font_data, glyphs):
        self.font_data = font_data
        self.glyphs = {g[0]: {'width': g[1], 'offset': g[2]} for g in glyphs}
        self.height = font_data[0]
    
    def _read_bits(self, data, start_bit, bit_count):
        """Читает bit_count бит начиная с start_bit из массива байт"""
        bits = []
        for i in range(bit_count):
            bit_pos = start_bit + i
            byte_index = bit_pos // 8
            bit_index = 7 - (bit_pos % 8)  # старший бит = левый пиксель
            if byte_index < len(data):
                bit = (data[byte_index] >> bit_index) & 1
                bits.append(bit)
            else:
                bits.append(0)
        return bits
    
    def get_glyph_bitmap(self, char_code):
        """Возвращает битмап символа"""
        if char_code not in self.glyphs:
            return None
            
        glyph = self.glyphs[char_code]
        width = glyph['width']
        offset = glyph['offset']
        
        # Вычисляем количество бит данных
        total_bits = width * self.height
        # Читаем биты из font_data
        bits = self._read_bits(self.font_data, offset * 8, total_bits)
        
        # Преобразуем в 2D массив
        bitmap = []
        for row in range(self.height):
            row_bits = bits[row * width:(row + 1) * width]
            bitmap.append(row_bits)
        
        return bitmap
    
    def render_char(self, display, char_code, x, y):
        """Рендерит символ на экран в позицию (x, y)"""
        bitmap = self.get_glyph_bitmap(char_code)
        if bitmap is None:
            return 0  # ширина символа если не найден
        
        width = len(bitmap[0]) if bitmap else 0
        
        for row in range(len(bitmap)):
            for col in range(len(bitmap[row])):
                if y + row < display.height and x + col < display.width:
                    if bitmap[row][col]:
                        display.draw_pixel(x + col, y + row, 1)
        
        return width

class FontRendererApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Font Renderer")
        self.root.geometry("600x400")
        
        self.font = None
        self.display = None
        
        self.setup_ui()
        self.load_default_font()  # Загружаем встроенный шрифт при запуске
        
    def setup_ui(self):
        # Панель управления
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопка выбора шрифта
        self.font_button = tk.Button(control_frame, text="Выбрать шрифт", command=self.load_font)
        self.font_button.pack(side=tk.LEFT)
        
        # Поле ввода текста
        tk.Label(control_frame, text="Текст:").pack(side=tk.LEFT, padx=(10, 5))
        self.text_entry = tk.Entry(control_frame)
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.text_entry.bind('<KeyRelease>', self.on_text_change)
        
        # Кнопка очистки
        self.clear_button = tk.Button(control_frame, text="Очистить", command=self.clear_display)
        self.clear_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Canvas для отображения
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, width=512, height=256, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Инициализация дисплея
        self.display = Display(self.canvas, scale=4)
        
    def load_default_font(self):
        """Загружает встроенный шрифт"""
        # Font: Arial, Height: 16px
        # Generated by Python font rasterizer
        # Total glyphs: 15

        font_data = [
            16,  # height
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x10, 0x08, 0x3F, 0x82, 0x01, 0x00, 0x80, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60,
            0x00, 0x00, 0x00, 0x03, 0x82, 0x23, 0x19, 0x04, 0x82, 0x41, 0x20, 0x90, 0x48, 0x26, 0x31, 0x10, 0x70, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x80, 0xC0, 0xE0, 0x90, 0x08, 0x04, 0x02, 0x01, 0x00, 0x80, 0x40, 0x20, 0x10, 0x00,
            0x00, 0x00, 0x00, 0x07, 0x86, 0x22, 0x18, 0x04, 0x06, 0x02, 0x03, 0x03, 0x03, 0x03, 0x03, 0x01, 0xFC, 0x00,
            0x00, 0x00, 0x00, 0x03, 0x86, 0x62, 0x18, 0x0C, 0x0C, 0x0E, 0x01, 0x80, 0x40, 0x24, 0x33, 0x10, 0xF0, 0x00,
            0x00, 0x00, 0x00, 0x00, 0xC0, 0xE0, 0x70, 0x78, 0x6C, 0x26, 0x33, 0x11, 0x9F, 0xE0, 0x60, 0x30, 0x18, 0x00,
            0x00, 0x00, 0x00, 0x07, 0xE2, 0x01, 0x01, 0x80, 0xF8, 0x63, 0x01, 0x80, 0x40, 0x24, 0x33, 0x10, 0xF0, 0x00,
            0x00, 0x00, 0x00, 0x03, 0x82, 0x23, 0x19, 0x00, 0xB8, 0x62, 0x21, 0x90, 0x48, 0x26, 0x31, 0x10, 0x70, 0x00,
            0x00, 0x00, 0x00, 0x0F, 0xE0, 0x30, 0x30, 0x10, 0x18, 0x08, 0x0C, 0x06, 0x02, 0x01, 0x00, 0x80, 0xC0, 0x00,
            0x00, 0x00, 0x00, 0x03, 0x82, 0x23, 0x19, 0x8C, 0x44, 0x3E, 0x31, 0x90, 0x48, 0x24, 0x13, 0x18, 0xF0, 0x00,
            0x00, 0x00, 0x00, 0x03, 0x86, 0x22, 0x19, 0x04, 0x82, 0x43, 0x31, 0x8F, 0x40, 0x24, 0x33, 0x30, 0xF0, 0x00,
            0x00, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0x60,
            0x00, 0x00, 0x00, 0x00, 0x3F, 0x86, 0x18, 0xC1, 0x18, 0x23, 0x08, 0x7F, 0x8C, 0x31, 0x83, 0x30, 0x66, 0x0C, 0xC3, 0x1F, 0xC0, 0x00
        ]

        glyphs = [
            [43, 9, 1],   # '+'
            [45, 5, 19],  # '-'
            [46, 4, 29],  # '.'
            [48, 9, 37],  # '0'
            [49, 9, 55],  # '1'
            [50, 9, 73],  # '2'
            [51, 9, 91],  # '3'
            [52, 9, 109], # '4'
            [53, 9, 127], # '5'
            [54, 9, 145], # '6'
            [55, 9, 163], # '7'
            [56, 9, 181], # '8'
            [57, 9, 199], # '9'
            [58, 4, 217], # ':'
            [194, 11, 225] # 'В'
        ]
        
        self.font = Font(font_data, glyphs)
        print(f"Встроенный шрифт загружен: высота={font_data[0]}, символов={len(glyphs)}")
    
    def parse_header_file(self, content):
        """Парсит содержимое .h файла и извлекает font_data и glyphs"""
        try:
            # Простой парсинг - ищем массивы по ключевым словам
            lines = content.split('\n')
            
            # Ищем font_data
            font_data = []
            in_font_data = False
            
            for line in lines:
                if 'font_data[]' in line and '=' in line:
                    in_font_data = True
                    continue
                if in_font_data:
                    if '};' in line:
                        break
                    # Извлекаем числа из строки
                    numbers = re.findall(r'(?:0x[0-9A-Fa-f]+|\d+)', line)
                    for num in numbers:
                        if num.startswith('0x'):
                            font_data.append(int(num, 16))
                        else:
                            font_data.append(int(num))
            
            if not font_data:
                raise ValueError("Не удалось найти данные шрифта")
            
            # Ищем glyphs
            glyphs = []
            in_glyphs = False
            
            for line in lines:
                if 'glyphs[]' in line and '=' in line:
                    in_glyphs = True
                    continue
                if in_glyphs:
                    if '};' in line:
                        break
                    # Ищем тройки чисел в формате {x, y, z}
                    tuples = re.findall(r'\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}', line)
                    for ascii_code, width, offset in tuples:
                        glyphs.append([int(ascii_code), int(width), int(offset)])
            
            if not glyphs:
                raise ValueError("Не удалось найти данные глифов")
                
            return font_data, glyphs
            
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            raise
    
    def load_font(self):
        """Загрузка шрифта из файла .h"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл шрифта",
            filetypes=[("Header files", "*.h"), ("All files", "*.*")],
            initialdir="."  # Текущая директория
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            font_data, glyphs = self.parse_header_file(content)
            self.font = Font(font_data, glyphs)
            
            print(f"Шрифт загружен из файла: высота={font_data[0]}, символов={len(glyphs)}")
            
            self.render_text()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить шрифт:\n{str(e)}")
            print(f"Ошибка загрузки шрифта: {e}")
            # Возвращаем встроенный шрифт
            self.load_default_font()
            self.render_text()
    
    def on_text_change(self, event=None):
        self.render_text()
    
    def clear_display(self):
        if self.display:
            self.display.clear()
            self.display.render()
    
    def render_text(self):
        if not self.font or not self.display:
            return
            
        self.display.clear()
        
        text = self.text_entry.get()
        x, y = 0, 0
        
        for char in text:
            char_code = ord(char)
            
            if char_code in self.font.glyphs:
                width = self.font.render_char(self.display, char_code, x, y)
                x += width + 1  # +1 пиксель пробел между символами
            else:
                # Если символ не найден, рисуем прямоугольник как placeholder
                for i in range(8):
                    for j in range(16):
                        if (i == 0 or i == 7 or j == 0 or j == 15):
                            self.display.draw_pixel(x + i, y + j, 1)
                x += 8 + 1
        
        self.display.render()

if __name__ == "__main__":
    root = tk.Tk()
    app = FontRendererApp(root)
    root.mainloop()