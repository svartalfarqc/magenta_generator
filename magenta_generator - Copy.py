import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import configparser
import os
import glob

# Read settings from config file and convert to absolute paths
config = configparser.ConfigParser()
config.read('config.ini')
defaults = config['Defaults']

# Define a function to ensure paths are absolute
def get_absolute_path(path):
    return os.path.abspath(os.path.expanduser(path))

# Function to run the melody_rnn_generate command
def run_melody_rnn_generate(config, bundle_file, num_outputs, num_steps, primer_midi):
    # Use the default output directory from the config file
    output_dir = output_dir_default

    # Convert all paths to absolute paths
    bundle_file = get_absolute_path(bundle_file)
    primer_midi = get_absolute_path(primer_midi)

    command = [
        "melody_rnn_generate",
        "--config=" + config,
        "--bundle_file=" + bundle_file,
        "--output_dir=" + output_dir,
        "--num_outputs=" + str(num_outputs),
        "--num_steps=" + str(num_steps),
        "--primer_midi=" + primer_midi
    ]

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)

    # Output the result
    if result.returncode != 0:
        output_text.set("Error: " + result.stderr)
    else:
        output_text.set("Success: " + result.stdout)

# Function to browse for MIDI file
def browse_midi_file():
    filename = filedialog.askopenfilename(
        initialdir=os.path.dirname(primer_midi_default),
        title="Select a MIDI file",
        filetypes=(("MIDI files", "*.mid"), ("All files", "*.*")))
    if filename:
        primer_midi_entry.set(filename)

# Get absolute paths from the configuration
bundle_file_default = get_absolute_path(defaults.get('BundleFile', './attention_rnn.mag'))
output_dir_default = get_absolute_path(defaults.get('OutputDir', './output'))
primer_midi_default = get_absolute_path(defaults.get('PrimerMidi', './duke_melody.mid'))

# Populate dropdown list for bundle files
bundle_files_path = get_absolute_path(defaults.get('CheckpointsFolder', './checkpoints'))
bundle_files = glob.glob(os.path.join(bundle_files_path, '*.mag'))

# Create the UI
root = tk.Tk()
root.title("Magenta Melody Generator")

# Bundle file dropdown
tk.Label(root, text="Bundle File:").pack()
bundle_file_var = tk.StringVar()
bundle_file_dropdown = ttk.Combobox(root, textvariable=bundle_file_var, values=bundle_files)
bundle_file_dropdown.set(bundle_file_default)
bundle_file_dropdown.pack()

# Number of outputs entry (using default from config)
tk.Label(root, text="Number of Outputs:").pack()
num_outputs_entry = tk.Entry(root)
num_outputs_entry.insert(0, defaults.get('NumOutputs', '10'))
num_outputs_entry.pack()

# Number of steps entry (using default from config)
tk.Label(root, text="Number of Steps:").pack()
num_steps_entry = tk.Entry(root)
num_steps_entry.insert(0, defaults.get('NumSteps', '1024'))
num_steps_entry.pack()

# Primer MIDI file browse
tk.Label(root, text="Primer MIDI File:").pack()
primer_midi_entry = tk.StringVar()
primer_midi_entry.set(primer_midi_default)
tk.Entry(root, textvariable=primer_midi_entry, state='readonly').pack()
browse_button = tk.Button(root, text="Browse", command=browse_midi_file)
browse_button.pack()

# Generate button
generate_button = tk.Button(root, text="Generate Melody", command=lambda: run_melody_rnn_generate(
    "attention_rnn",  # Assuming a fixed configuration
    bundle_file_var.get(),
    num_outputs_entry.get(),
    num_steps_entry.get(),
    primer_midi_entry.get()
))
generate_button.pack()

# Output label
output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text)
output_label.pack()

root.mainloop()
