import tkinter as tk
from tkinter import filedialog, ttk
import os
import configparser
import magenta
import tensorflow as tf
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.music import midi_io
from magenta.music.protobuf import generator_pb2
import traceback

# Read settings from config file
config = configparser.ConfigParser()
config.read('config.ini')
default_output_folder = os.path.abspath(config.get('Paths', 'OutputFolder', fallback='./output'))
checkpoints_folder = os.path.abspath(config.get('Paths', 'CheckpointsFolder', fallback='./checkpoints'))
default_num_steps = config.getint('Defaults', 'NumSteps', fallback=1024)
default_num_outputs = config.getint('Defaults', 'NumOutputs', fallback=10)
default_temperature = config.getfloat('Defaults', 'Temperature', fallback=1.0)

# Debug print for paths
print(f"Default output folder: {default_output_folder}")
print(f"Checkpoints folder: {checkpoints_folder}")

# Function to get list of .mag files
def get_mag_files(folder):
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.mag')]
        print(f"Found .mag files: {files}")
        return files
    except FileNotFoundError:
        print(f"Directory not found: {folder}")
        return []

# Initialize the Magenta Melody RNN model
def initialize_model(bundle_file):
    print(f"Initializing model with bundle file: {bundle_file}")
    if not os.path.isfile(bundle_file):
        raise FileNotFoundError(f"Bundle file not found: {bundle_file}")

    bundle = tf.io.gfile.GFile(bundle_file, 'rb').read()
    config_id = os.path.splitext(os.path.basename(bundle_file))[0]
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    
    melody_rnn = generator_map[config_id]()
    melody_rnn.initialize(bundle)
    return melody_rnn

# Generate a melody
def generate_melody(melody_rnn, primer_midi, output_folder, num_outputs, num_steps, temperature):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_sequence = midi_io.midi_file_to_note_sequence(primer_midi)

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generator_options.generate_sections.add(start_time=0, end_time=num_steps)

    for i in range(num_outputs):
        generated_sequence = melody_rnn.generate(input_sequence, generator_options)
        output_midi = os.path.join(output_folder, f"output_{i+1}.mid")
        midi_io.note_sequence_to_midi_file(generated_sequence, output_midi)

# Function to handle the "Generate" button click
def on_generate():
    selected_checkpoint_file = bundle_file_var.get()
    bundle_file_path = os.path.join(checkpoints_folder, selected_checkpoint_file)
    print(f"Selected checkpoint file: {bundle_file_path}")

    primer_midi = primer_midi_var.get()
    output_folder = output_folder_var.get() or default_output_folder
    num_outputs = int(num_outputs_var.get() or default_num_outputs)
    num_steps = int(num_steps_var.get() or default_num_steps)
    temperature = float(temperature_var.get() or default_temperature)

    try:
        melody_rnn = initialize_model(bundle_file_path)
        generate_melody(melody_rnn, primer_midi, output_folder, num_outputs, num_steps, temperature)
        status_label.config(text=f"{num_outputs} Melodies Generated in {output_folder}")
    except Exception as e:
        traceback.print_exc()  # This will print the full traceback
        status_label.config(text=f"Error: {e}")

# Helper functions for file dialogs
def open_file_dialog(entry):
    filename = filedialog.askopenfilename()
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def select_folder(entry):
    foldername = filedialog.askdirectory()
    if foldername:
        entry.delete(0, tk.END)
        entry.insert(0, foldername)


# UI Setup
root = tk.Tk()
root.title("Magenta Melody Generator")

# Bundle File Selection Dropdown
tk.Label(root, text="Bundle File:").pack()
bundle_file_var = tk.StringVar()
bundle_file_dropdown = ttk.Combobox(root, textvariable=bundle_file_var, values=get_mag_files(checkpoints_folder))
bundle_file_dropdown.pack()

# Primer MIDI File Selection
tk.Label(root, text="Primer MIDI File:").pack()
primer_midi_var = tk.StringVar()
primer_midi_entry = tk.Entry(root, textvariable=primer_midi_var)
primer_midi_entry.pack()
tk.Button(root, text="Browse", command=lambda: open_file_dialog(primer_midi_entry)).pack()

# Output Folder Selection
tk.Label(root, text="Output Folder:").pack()
output_folder_var = tk.StringVar(value=default_output_folder)
output_folder_entry = tk.Entry(root, textvariable=output_folder_var)
output_folder_entry.pack()
tk.Button(root, text="Browse", command=lambda: select_folder(output_folder_entry)).pack()

# Number of Outputs
tk.Label(root, text="Number of Outputs:").pack()
num_outputs_var = tk.StringVar(value=str(default_num_outputs))
num_outputs_entry = tk.Entry(root, textvariable=num_outputs_var)
num_outputs_entry.pack()

# Number of Steps
tk.Label(root, text="Number of Steps:").pack()
num_steps_var = tk.StringVar(value=str(default_num_steps))
num_steps_entry = tk.Entry(root, textvariable=num_steps_var)
num_steps_entry.pack()

# Temperature
tk.Label(root, text="Temperature:").pack()
temperature_var = tk.StringVar(value=str(default_temperature))
temperature_entry = tk.Entry(root, textvariable=temperature_var)
temperature_entry.pack()

# Generate Button
generate_button = tk.Button(root, text="Generate Melody", command=on_generate)
generate_button.pack()

# Status Label
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()

