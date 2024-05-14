def import_ascii_art(file_path):
    with open(file_path, "r") as file:
        return file.read()
    
def title():
    ascii_art_file = "ascii_art.txt"
    ascii_title = import_ascii_art(ascii_art_file)
    print(ascii_title)

