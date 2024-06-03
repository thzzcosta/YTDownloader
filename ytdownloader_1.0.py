import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pytube import YouTube
from ttkthemes import ThemedTk
import configparser
from pydub import AudioSegment

def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists('settings.ini'):
        config.read('settings.ini')
    return config

def save_settings(download_path):
    config = configparser.ConfigParser()
    config['Settings'] = {'download_path': download_path}
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)

def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    progress_var.set(percentage)
    progress_bar.update()
    stats_label.config(text=f"Baixando: {percentage:.2f}%")

def download_video():
    download_media(is_audio=False)

def download_audio():
    download_media(is_audio=True)

def download_media(is_audio):
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erro", "Por favor, insira um link do YouTube.")
        return

    try:
        yt = YouTube(url, on_progress_callback=progress_callback)
        stream = yt.streams.filter(only_audio=True).first() if is_audio else yt.streams.get_highest_resolution()
        save_path = save_path_var.get()

        if not save_path:
            messagebox.showerror("Erro", "Por favor, escolha uma pasta de destino.")
            return

        stats_label.config(text="Iniciando o download...")
        downloaded_file = stream.download(output_path=save_path)

        if is_audio:
            base, ext = os.path.splitext(downloaded_file)
            new_file = base + '.mp3'
            audio = AudioSegment.from_file(downloaded_file)
            audio.export(new_file, format='mp3')
            os.remove(downloaded_file)
            stats_label.config(text="Download do áudio concluído!")
        else:
            stats_label.config(text="Download do vídeo concluído!")

        messagebox.showinfo("Sucesso", "Mídia baixada com sucesso!")
    except Exception as e:
        stats_label.config(text="Erro no download.")
        messagebox.showerror("Erro", f"Falha ao baixar a mídia: {e}")

def choose_save_path():
    save_path = filedialog.askdirectory()
    if save_path:
        save_path_var.set(save_path)
        save_settings(save_path)

config = load_settings()
initial_save_path = config.get('Settings', 'download_path', fallback='')

root = ThemedTk(theme="breeze-dark")
root.title("YouTube para MP3 e MP4")

tk.Label(root, text="Link do YouTube:").grid(row=0, column=0, padx=10, pady=10)
url_entry = ttk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Pasta de destino:").grid(row=1, column=0, padx=10, pady=10)
save_path_var = tk.StringVar(value=initial_save_path)
save_path_entry = ttk.Entry(root, textvariable=save_path_var, width=40, state='readonly')
save_path_entry.grid(row=1, column=1, padx=10, pady=10)
choose_path_button = ttk.Button(root, text="Escolher...", command=choose_save_path)
choose_path_button.grid(row=1, column=2, padx=10, pady=10)

download_video_button = ttk.Button(root, text="Baixar Vídeo (MP4)", command=download_video)
download_video_button.grid(row=2, column=0, padx=10, pady=20)
download_audio_button = ttk.Button(root, text="Baixar Áudio (MP3)", command=download_audio)
download_audio_button.grid(row=2, column=2, padx=10, pady=20)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
stats_label = ttk.Label(root, text="Pronto para baixar")
stats_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()