import tkinter as tk
import time
import math
import struct
import winsound
import threading

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
    def __init__(self, matrices, palette_map, pulse_sec, pause_sec, duration_factor, client_name, use_audio=False, frequency=432.0):
        self.matrices = matrices
        self.palette = palette_map
        self.pulse_ms = int(pulse_sec * 1000)
        self.pause_ms = int(pause_sec * 1000)
        self.total_duration_sec = duration_factor * 21 * 60
        self.start_time = time.time()
        self.client_name = client_name
        self.use_audio = use_audio
        self.frequency = max(37.0, min(frequency, 3000.0)) 
        
        self.current_matrix_idx = 0
        self.is_blank = False
        self.running = True
        
        self.root = tk.Tk()
        self.root.title(f"Harmonisierung - {client_name}")
        self.root.geometry("1000x900") 
        self.root.configure(bg='black')
        
        self.root.bind("<Escape>", lambda e: self.close())
        
        self.info_label = tk.Label(
            self.root, 
            text="Initialisiere...", 
            font=("Arial", 12), 
            fg="#444444", 
            bg="black"
        )
        self.info_label.pack(side="bottom", pady=20)
        
        self.canvas_size = 750 
        self.canvas = tk.Canvas(
            self.root, 
            width=self.canvas_size, 
            height=self.canvas_size, 
            bg='black', 
            highlightthickness=0
        )
        self.canvas.pack(expand=True)
        
        # Pre-generate Audio Buffer
        self.wav_data = None
        if self.use_audio:
            self.wav_data = self.generate_sine_wave(self.frequency)

        # Start
        self.draw_matrix(self.matrices[0])
        if self.use_audio and self.wav_data:
             print("Starting audio...")
             winsound.PlaySound(self.wav_data, winsound.SND_MEMORY | winsound.SND_LOOP | winsound.SND_ASYNC)
        
        self.root.after(self.pulse_ms, self.cycle_step)
        

    def close(self):
        self.running = False
        if self.use_audio:
            winsound.PlaySound(None, winsound.SND_PURGE)
        self.root.destroy()

    def generate_sine_wave(self, frequency, duration=1.0, sample_rate=44100, amplitude=0.2):
        K = max(1, int(round(frequency * duration)))
        n_samples = int((K / frequency) * sample_rate)
        corrected_freq = (K * sample_rate) / n_samples
        
        header = b'RIFF' + struct.pack('<I', 36 + n_samples * 2) + b'WAVE' + b'fmt ' + struct.pack('<I', 16) + \
                 struct.pack('<H', 1) + struct.pack('<H', 1) + struct.pack('<I', sample_rate) + \
                 struct.pack('<I', sample_rate * 2) + struct.pack('<H', 2) + struct.pack('<H', 16) + \
                 b'data' + struct.pack('<I', n_samples * 2)
        
        data = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            value = int(amplitude * 32767.0 * math.sin(2.0 * math.pi * corrected_freq * t))
            data.extend(struct.pack('<h', value))
        return header + data

    def draw_matrix(self, matrix):
        print("Drawing matrix...")
        self.canvas.delete("all")
        cell_size = self.canvas_size / 12
        font_size = int(cell_size * 0.5)
        
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                try:
                    val_int = int(val)
                except:
                    val_int = 0
                    
                x1 = c * cell_size
                y1 = r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                hex_color = self.palette.get(val_int, "#FFFFFF")
                
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

    def update_info(self):
        if not self.running: return False
        elapsed = time.time() - self.start_time
        remaining = self.total_duration_sec - elapsed
        if remaining <= 0:
            self.close()
            return False
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        mode_str = f" | Audio: {int(self.frequency)}Hz" if self.use_audio else ""
        state = "PAUSE" if self.is_blank else f"IMPULS (Matrix {self.current_matrix_idx + 1}/{len(self.matrices)})"
        try:
            self.info_label.config(text=f"{self.client_name} | {state} | Verbleibend: {mins:02d}:{secs:02d}{mode_str}")
        except:
            pass 
        return True

    def cycle_step(self):
        if not self.running: return
        if not self.update_info(): return

        if self.is_blank:
            self.is_blank = False
            self.current_matrix_idx = (self.current_matrix_idx + 1) % len(self.matrices)
            self.draw_matrix(self.matrices[self.current_matrix_idx])
            if self.use_audio and self.wav_data:
                winsound.PlaySound(self.wav_data, winsound.SND_MEMORY | winsound.SND_LOOP | winsound.SND_ASYNC)
            self.root.after(self.pulse_ms, self.cycle_step)
        else:
            self.is_blank = True
            self.canvas.delete("all")
            if self.use_audio:
                winsound.PlaySound(None, winsound.SND_PURGE)
            self.root.after(self.pause_ms, self.cycle_step)
            
    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Test Data
    test_matrix = [[(r + c) % 10 for c in range(12)] for r in range(12)]
    
    # Palette
    test_palette = {
        0: "#FFFFFF", 1: "#FF0000", 2: "#FF7F00", 3: "#FFFF00", 
        4: "#00FF00", 5: "#00FFFF", 6: "#0000FF", 7: "#8B00FF", 
        8: "#FF00FF", 9: "#FFD700"
    }
    
    print("Launching test...")
    app = HarmonizerWindow(
        [test_matrix], 
        test_palette, 
        pulse_sec=2.0, 
        pause_sec=1.0, 
        duration_factor=0.01, 
        client_name="Test User",
        use_audio=True,
        frequency=432.0
    )
    app.start()
