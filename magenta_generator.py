import tkinter as tk
from tkinter import filedialog
import os
import magenta
import tensorflow as tf
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.music import midi_io
from magenta.music.protobuf import generator_pb2

# Initialize the Magenta Melody RNN model
def initialize_model(model_name, checkpoint):
    bundle = tf.io.gfile.GFile(checkpoint, 'rb').read()
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map[model_name]()
    melody_rnn.initialize(bundle)
    return melody_rnn

# Generate a melody
def generate_melody(melody_rnn, input_midi, output_folder, num_outputs, num_steps, temperature):
    # Check if the output folder exists, create it if not
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_sequence = midi_io.midi_file_to_note_sequence(input_midi)

    generator_options = generator_pb2.GeneratorOptions()
    generator_options.args['temperature'].float_value = temperature
    generator_options.generate_sections.add(start_time=0, end_time=num_steps)

    for i in range(num_outputs):
        generated_sequence = melody_rnn.generate(input_sequence, generator_options)
        output_midi = os.path.join(output_folder, f"output_{i+1}.mid")
        midi_io.note_sequence_to_midi_file(generated_sequence, output_midi)


# Function to handle the "Generate" button click
def on_generate():
    model_name = model_entry.get()
    checkpoint = checkpoint_entry.get()
    input_midi = input_midi_entry.get()
    output_folder = output_folder_entry.get()
    num_outputs = int(num_outputs_entry.get())
    num_steps = int(num_steps_entry.get())
    temperature = float(temperature_entry.get())

    melody_rnn = initialize_model(model_name, checkpoint)
    generate_melody(melody_rnn, input_midi, output_folder, num_outputs, num_steps, temperature)
    status_label.config(text=f"{num_outputs} Melodies Generated in {output_folder}")


# Function to open a file selection dialog
def open_file_dialog(entry):
    filename = filedialog.askopenfilename()
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

# Function to open a folder selection dialog
def select_folder(entry):
    foldername = filedialog.askdirectory()
    if foldername:
        entry.delete(0, tk.END)
        entry.insert(0, foldername)

# Create the UI
root = tk.Tk()
root.title("Magenta Melody Generator")

tk.Label(root, text="Model Checkpoint:").pack()
checkpoint_entry = tk.Entry(root)
checkpoint_entry.pack()
tk.Button(root, text="Browse", command=lambda: open_file_dialog(checkpoint_entry)).pack()

tk.Label(root, text="Input MIDI File:").pack()
input_midi_entry = tk.Entry(root)
input_midi_entry.pack()
tk.Button(root, text="Browse", command=lambda: open_file_dialog(input_midi_entry)).pack()

tk.Label(root, text="Destination Folder:").pack()
output_folder_entry = tk.Entry(root)
output_folder_entry.pack()
tk.Button(root, text="Browse", command=lambda: select_folder(output_folder_entry)).pack()

tk.Label(root, text="Number of Outputs:").pack()
num_outputs_entry = tk.Entry(root)
num_outputs_entry.insert(0, "1")  # Default value
num_outputs_entry.pack()

tk.Label(root, text="Number of Steps:").pack()
num_steps_entry = tk.Entry(root)
num_steps_entry.insert(0, "128")  # Default value
num_steps_entry.pack()

tk.Label(root, text="Temperature:").pack()
temperature_entry = tk.Entry(root)
temperature_entry.insert(0, "1.0")  # Default value
temperature_entry.pack()

generate_button = tk.Button(root, text="Generate Melody", command=on_generate)
generate_button.pack()

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()