import sys
import string

def is_visible_printable(c: str) -> bool:
    """Проверяет, является ли символ печатаемым и видимым (без \n, \t и т.п.)"""
    if c == ' ':
        return True
    if c in string.printable:
        if c in '\n\t\r\x0b\x0c':
            return False
        return True
    # Поддержка кириллицы
    return 'а' <= c <= 'я' or 'А' <= c <= 'Я' or c in 'ёЁ'

def get_visible_chars_sorted(text: str) -> str:
    """Возвращает уникальные печатаемые символы, отсортированные по коду"""
    unique_chars = {c for c in text if is_visible_printable(c)}
    return ''.join(sorted(unique_chars, key=ord))

def show_help():
    print("Использование:")
    print("  python unique_chars.py <файл>          # прочитать текст из файла")
    print("  python unique_chars.py строка1 строка2  # обработать переданную строку")
    print()
    print("Примеры:")
    print("  python unique_chars.py menu.txt")
    print("  python unique_chars.py \"Часы -Часы 22\"")

def main():
    if len(sys.argv) == 1:
        show_help()
        return

    # Один аргумент → файл
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Ошибка: не удалось прочитать файл '{filename}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Несколько аргументов → объединяем в строку
        text = ' '.join(sys.argv[1:])

    result = get_visible_chars_sorted(text)
    print(result)

if __name__ == "__main__":
    main()