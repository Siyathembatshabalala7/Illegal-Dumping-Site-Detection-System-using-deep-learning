import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk ,ImageEnhance
import cv2
import threading
import time
import os
from ultralytics import YOLO
import itertools

MODEL_PATH = "C:/Users/Admin/Downloads/NCSP730 Test 2 (83% Accuracy)/best.pt"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

model = YOLO(MODEL_PATH)


BG = "#0e1117"
PANEL_BG = "#161a23"
ACCENT = "#00bfa5"
ALERT_RED = "#ff4d4d"
SAFE_GREEN = "#00ff88"
TEXT = "#ffffff"


def upload_image():
    global uploaded_img_path
    uploaded_img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if uploaded_img_path:
        show_image(uploaded_img_path, lbl_original)
        lbl_detected.config(image="", text="Detection result will appear here", fg="#888")
        lbl_count.config(text="Detected Sites: -", bg=PANEL_BG)
        lbl_status.config(text="Image loaded ✅", fg=ACCENT)
    else:
        messagebox.showwarning("Warning", "Please select an image file.")


def show_image(path, label):
    img = Image.open(path).resize((420, 420))
    img_tk = ImageTk.PhotoImage(img)
    label.config(image=img_tk, text="")
    label.image = img_tk


def start_detection():
    if not uploaded_img_path:
        messagebox.showwarning("Warning", "Please upload an image first.")
        return
    lbl_status.config(text="Detecting... please wait", fg="#cccccc")
    lbl_count.config(text="Detecting...", bg=PANEL_BG)
    start_spinner()
    threading.Thread(target=detect_waste, daemon=True).start()


def detect_waste():
    global spinner_running
    try:
        img = cv2.imread(uploaded_img_path)
        results = model(img)

        detected_img = results[0].plot()
        detected_img = cv2.cvtColor(detected_img, cv2.COLOR_BGR2RGB)
        detected_pil = Image.fromarray(detected_img).resize((420, 420))
        detected_tk = ImageTk.PhotoImage(detected_pil)

        lbl_detected.after(0, lambda: update_result(detected_tk, len(results[0].boxes)))

    except Exception as e:
        lbl_status.config(text=f"Error: {e}", fg=ALERT_RED)
    finally:
        spinner_running = False


def update_result(detected_img, count):
    lbl_detected.config(image=detected_img, text="")
    lbl_detected.image = detected_img

    lbl_status.config(text="Detection complete ✅", fg=ACCENT)
    lbl_count.config(text=f"Detected Waste Sites: {count}")

    if count > 0:
        flash_label(lbl_count, ALERT_RED)
    else:
        flash_label(lbl_count, SAFE_GREEN)


def flash_label(label, color):
    def animate():
        for _ in range(30):
            label.config(bg=color)
            time.sleep(0.3)
            label.config(bg=PANEL_BG)
            time.sleep(0.3)
    threading.Thread(target=animate, daemon=True).start()

spinner_running = False
def start_spinner():
    global spinner_running
    spinner_running = True
    threading.Thread(target=animate_spinner, daemon=True).start()

def animate_spinner():
    spinner_cycle = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while spinner_running:
        lbl_status.config(text=f"Detecting... {next(spinner_cycle)}", fg="#cccccc")
        time.sleep(0.1)

root = tk.Tk()
root.title("Illegal Waste Detection System")
root.configure(bg=BG)
root.attributes('-fullscreen', True)
root.bind("<Escape>", lambda e: root.attributes('-fullscreen', False))

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

bg_path = "C:/Users/Admin/OneDrive/Documents/Third Year 2025/NCSP730 CAPSTONE PROJECT/Illegal Dump.webp"
bg_image = Image.open(bg_path)
bg_image = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
bg_image = ImageEnhance.Brightness(bg_image).enhance(0.3)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.image = bg_photo
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

header = tk.Label(
    root, text="🌍 Illegal Waste Detection System",
    font=("Helvetica", 22, "bold"), bg=BG, fg=ACCENT
)
header.pack(pady=15)

button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=10)

btn_upload = tk.Button(
    button_frame, text="📸 Upload Image", command=upload_image,
    font=("Arial", 14, "bold"), bg=ACCENT, fg="white", relief="flat", width=15
)
btn_upload.grid(row=0, column=0, padx=15)

btn_detect = tk.Button(
    button_frame, text="🚀 Run Detection", command=start_detection,
    font=("Arial", 14, "bold"), bg="#ff8800", fg="white", relief="flat", width=15
)
btn_detect.grid(row=0, column=1, padx=15)

main_frame = tk.Frame(root, bg=BG)
main_frame.pack(pady=20)

frame_original = tk.LabelFrame(main_frame, text="📥 Uploaded Image", font=("Arial", 14, "bold"),
                               bg=PANEL_BG, fg="white", labelanchor="n", width=450, height=450)
frame_original.grid(row=0, column=0, padx=20)
frame_original.grid_propagate(False)



lbl_original = tk.Label(frame_original, text="Upload image to display", font=("Arial", 12),
                        fg="#888", bg=PANEL_BG)
lbl_original.pack(expand=True)

frame_detected = tk.LabelFrame(main_frame, text="📤 Detected Image", font=("Arial", 14, "bold"),
                               bg=PANEL_BG, fg="white", labelanchor="n", width=450, height=450)
frame_detected.grid(row=0, column=1, padx=20)
frame_detected.grid_propagate(False)

lbl_detected = tk.Label(frame_detected, text="Detection result will appear here",
                        font=("Arial", 12), fg="#888", bg=PANEL_BG)
lbl_detected.pack(expand=True)

lbl_count = tk.Label(root, text="Detected Sites: -", font=("Arial", 18, "bold"),
                     bg=PANEL_BG, fg="white", width=40)
lbl_count.pack(pady=15)

lbl_status = tk.Label(root, text="", font=("Arial", 13, "italic"), bg=BG, fg="#ccc")
lbl_status.pack(pady=5)

uploaded_img_path = None
root.mainloop()
