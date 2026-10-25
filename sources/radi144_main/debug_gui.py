import tkinter as tk
import time

def get_contrast_color(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "#000000"
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    return "#000000" if luminance > 128 else "#FFFFFF"

class HarmonizerWindow:
    def __init__(self, matrices, palette_map):
        self.matrices = matrices
        self.palette = palette_map
        self.current_matrix_idx = 0
        
        self.root = tk.Tk()
        self.root.title("Debug GUI")
        self.root.geometry("800x800")
        self.root.configure(bg='black')
        
        self.canvas_size = 600
        self.canvas = tk.Canvas(
            self.root, 
            width=self.canvas_size, 
            height=self.canvas_size, 
            bg='black', 
            highlightthickness=0
        )
        self.canvas.pack(expand=True)
        
        self.draw_matrix(self.matrices[0])
        
    def draw_matrix(self, matrix):
        print(f"Drawing matrix with palette keys: {list(self.palette.keys())}")
        print(f"Matrix val type: {type(matrix[0][0])}")
        
        self.canvas.delete("all")
        cell_size = self.canvas_size / 12
        font_size = int(cell_size * 0.5)
        
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                x1 = c * cell_size
                y1 = r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # key check
                if val not in self.palette:
                    print(f"WARNING: val {val} (type {type(val)}) not in palette!")
                
                hex_color = self.palette.get(val, "#FFFFFF")
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline=hex_color)
                
                text_color = get_contrast_color(hex_color)
                
                center_x = x1 + (cell_size / 2)
                center_y = y1 + (cell_size / 2)
                self.canvas.create_text(
                    center_x, 
                    center_y, 
                    text=str(val), 
                    fill=text_color, 
                    font=("Arial", font_size, "bold")
                )
                
    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Test Data similar to real app
    test_matrix = [[(r + c) % 10 for c in range(12)] for r in range(12)]
    
    # Int keys palette
    test_palette = {
        0: "#FFFFFF", 1: "#FF0000", 2: "#FF7F00", 3: "#FFFF00", 
        4: "#00FF00", 5: "#00FFFF", 6: "#0000FF", 7: "#8B00FF", 
        8: "#FF00FF", 9: "#FFD700"
    }
    
    print("Starting Debug GUI...")
    app = HarmonizerWindow([test_matrix], test_palette)
    app.start()
