import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess

class ScriptUI:
    def __init__(self, root):
        self.root = root
        root.title("Script Runner")

        # Input file selection
        tk.Label(root, text="Select Input File:").pack()
        self.input_file_entry = tk.Entry(root, width=50)
        self.input_file_entry.pack()
        tk.Button(root, text="Browse", command=self.browse_input_file).pack()

        # Output folder selection
        tk.Label(root, text="Select Output Folder:").pack()
        self.output_folder_entry = tk.Entry(root, width=50)
        self.output_folder_entry.pack()
        tk.Button(root, text="Browse", command=self.browse_output_folder).pack()

        # TTS option selection
        tk.Label(root, text="TTS Options:").pack()
        self.tts_options = ttk.Combobox(root, values=["azure", "openai"])
        self.tts_options.pack()

        # Voice name selection
        tk.Label(root, text="Voice Options:").pack()
        self.voice_options = ttk.Combobox(root, values=["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
        self.voice_options.pack()

        # Run button
        tk.Button(root, text="Run Script", command=self.run_script).pack()

    def browse_input_file(self):
        file = filedialog.askopenfilename()
        self.input_file_entry.delete(0, tk.END)
        self.input_file_entry.insert(0, file)

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, folder)

    def run_script(self):
        input_file = self.input_file_entry.get()
        output_folder = self.output_folder_entry.get()
        tts = self.tts_options.get()
        voice_name = self.voice_options.get()

        command = ['python3', 'main.py', input_file, output_folder]

        if tts:
            command += ['--tts', tts]
        if voice_name:
            command += ['--voice_name', voice_name]

        subprocess.run(command)
        messagebox.showinfo("Script Runner", "Script executed successfully.")

root = tk.Tk()
app = ScriptUI(root)
root.mainloop()
