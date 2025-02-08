import tkinter as tk
from tkinter import Label, messagebox
from PIL import Image, ImageTk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import imageio
import threading
import pygame 

# Initialize pygame mixer
pygame.mixer.init()

# Load sounds
click_sound1 = pygame.mixer.Sound("buttonclick.mp3")
click_sound2 = pygame.mixer.Sound("buttonclick.mp3")
bg_music = pygame.mixer.Sound(r"C:\Users\aksha\OneDrive\Documents\wise project\akshithawise.mp3")

def play_sound1():
    click_sound1.play()

def play_sound2():
    click_sound2.play()

def play_background_music():
    pygame.mixer.music.load(r"C:\Users\aksha\OneDrive\Documents\wise project\akshithawise.mp3")
    pygame.mixer.music.play(-1) 

# Function to play video
def play_video(label):
    video_path = r"C:\Users\aksha\OneDrive\Documents\wise project\WhatsApp Video 2024-05-30 at 16.21.05_ec781b86.mp4"
    try:
        video = imageio.get_reader(video_path)
        for frame in video.iter_data():
            frame_image = ImageTk.PhotoImage(Image.fromarray(frame).resize((700, 600)))
            label.config(image=frame_image)
            label.image = frame_image
            label.update()
    except ValueError as e:
        messagebox.showerror("Video Error", f"An error occurred while playing the video: {e}")
    except Exception as e:
        messagebox.showerror("Unknown Error", f"An unknown error occurred: {e}")

# Function to open node pairs window
def open_node_pairs_window():
    global node_pairs_window, entry_node_pairs
    play_sound1()
    node_pairs_window = tk.Toplevel(input_win)
    node_pairs_window.title("Node Pairs")

    label_node_pairs = tk.Label(node_pairs_window, text="Enter node pairs :", bg='#f0f0f0', font=("Arial", 12))
    label_node_pairs.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    entry_node_pairs = tk.Text(node_pairs_window, height=8, width=25, font=("Arial", 11), bg='#fff', fg='#000')
    entry_node_pairs.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    button_submit = tk.Button(node_pairs_window, text="Submit", command=close_node_pairs_window, font=("Arial", 12, "bold"), bg='#4CAF50', fg='#fff', width=20)
    button_submit.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

# Function to close node pairs window and get data
def close_node_pairs_window():
    global nodes
    node_pairs_data = entry_node_pairs.get("1.0", "end-1c").strip()
    try:
        nodes = [list(map(int, node.split())) for node in node_pairs_data.split('\n') if node]
        node_pairs_window.destroy()
    except ValueError:
        play_sound2()
        messagebox.showerror("Input Error", "Please enter valid node pairs.")

# Function to draw tree in a hierarchical layout
def draw_tree(nodes):
    input_win.withdraw()  # Hide the input window

    G = nx.DiGraph()
    for index, node in enumerate(nodes):
        num_children = node[0]
        children = node[1:num_children+1]
        parent = index + 1
        for child in children:
            G.add_edge(parent, child)

    pos = hierarchy_pos(G, 1)  # Generate positions using a hierarchical layout

    # Create a new window for the tree visualization
    tree_win = tk.Toplevel()
    tree_win.title("Tree Visualization")

    def on_tree_win_close():
        tree_win.destroy()
        input_win.deiconify()  # Show the input window again

    tree_win.protocol("WM_DELETE_WINDOW", on_tree_win_close)

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True, ax=ax)

    def on_node_click(event):
        for node in G.nodes:
            if event.xdata - 0.03 <= pos[node][0] <= event.xdata + 0.03 and event.ydata - 0.03 <= pos[node][1] <= event.ydata + 0.03:
                node_data = nodes[node - 1]
                x, y = node_data[1], node_data[2]
                quality = calculate_quality(node - 1)
                messagebox.showinfo("Node Information", f"Node: {node}\nX: {x}\nY: {y}\nQuality: {quality}")

    plt.gcf().canvas.mpl_connect('button_press_event', on_node_click)
    plt.title("Tree Visualization")

    # Embed the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=tree_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

def hierarchy_pos(G, root):
    pos = nx.spring_layout(G)
    pos = _hierarchy_pos(G, root, pos=pos, level=0, width=1.0)
    return pos

def _hierarchy_pos(G, root, pos, level=0, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
    neighbors = list(G.neighbors(root))
    if not neighbors:
        pos[root] = (xcenter, vert_loc)
    else:
        dx = width / len(neighbors)
        nextx = xcenter - width / 2 - dx / 2
        for neighbor in neighbors:
            nextx += dx
            pos = _hierarchy_pos(G, neighbor, pos=pos, level=level+1, width=dx, vert_gap=vert_gap, vert_loc=vert_loc-vert_gap, xcenter=nextx)
    pos[root] = (xcenter, vert_loc)
    return pos

# Function to calculate quality
def calculate_quality(i): 
    k = nodes[i][0]
    children = nodes[i][1:]
    quality = 0
    if k == 0:
        x, y = children
        quality += x ** 2 + y ** 2
        return quality
    for child in children:
        if node_quality.get(child) is None:
            node_quality[child] = calculate_quality(child - 1)
    max_node = max(children, key=lambda x: node_quality[x])
    x, y = 0, 0
    for child in children:
        if child == max_node:
            x += nodes[child - 1][1]
            y += nodes[child - 1][2]
        else:
            x -= nodes[child - 1][1]
            y -= nodes[child - 1][2]
    nodes[i] = [0, x, y]
    return calculate_quality(i)

# Function to handle button click
def calculate_and_show():
    global nodes, node_quality
    node_quality = {i + 1: None for i in range(len(nodes))}
    try:
        n = int(entry_n.get())
        if n != len(nodes):
            messagebox.showerror("Input Error", "Number of nodes does not match the node pairs provided.")
            return
        win_quality = calculate_quality(0)
        result_label.config(text="Winning quality: " + str(win_quality))
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of nodes.")

# Function to open the input window
def open_input_window():
    root.withdraw()  # Hide the initial window

    global input_win, entry_n, result_label, image_label
    input_win = tk.Toplevel()
    input_win.title("Input Window")
    input_win.configure(bg='#f0f0f0')

    # Centering widgets by using column configuration
    input_win.grid_columnconfigure(0, weight=1)  # Make the column in the middle expandable
    input_win.grid_columnconfigure(1, weight=1)  # Make the column in the middle expandable

    font_label = ("Arial", 15)
    font_entry = ("Arial", 18)
    font_button = ("Arial", 20, "bold")

    # Load and display image
    image_path = r"298917789_407036761526746_1635864118885478525_n.png"
    img = Image.open(image_path)
    img = img.resize((600, 500))
    img = ImageTk.PhotoImage(img)
    image_label = tk.Label(input_win, image=img, bg='#CD4C46')
    image_label.image = img
    image_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

    # Labels and Entries for taking input
    label_n = tk.Label(input_win, text="Number of Nodes:", font=font_label, bg='#f0f0f0')
    label_n.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_n = tk.Entry(input_win, font=font_entry, bg='#fff', fg='#000')
    entry_n.grid(row=1, column=1, padx=10, pady=5, sticky='w')

    # Button to open node pairs window
    button_node_pairs = tk.Button(input_win, font=font_button, text="Enter Node Pairs", command=open_node_pairs_window, bg='#2196F3', fg='#fff', width=20)
    button_node_pairs.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    # Button to calculate
    calculate_button = tk.Button(input_win, text="Calculate", font=font_button, command=calculate_and_show, bg='#4CAF50', fg='#fff', width=20)
    calculate_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

    # Label to display result
    result_label = tk.Label(input_win, text="", font=font_label, bg='#f0f0f0')
    result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

    # Create a frame to hold buttons at the bottom
    button_frame = tk.Frame(input_win, bg='#f0f0f0')
    button_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

    # Configure column expansion in button_frame
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    # Button to draw tree
    draw_tree_button = tk.Button(button_frame, text="Draw Tree", font=font_button, command=lambda: draw_tree(nodes), bg='#FF9800', fg='#fff', width=20)
    draw_tree_button.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

    # Button to exit
    exit_button = tk.Button(button_frame, text="Exit", font=font_button, command=exit_application, bg='#f44336', fg='#fff', width=20)
    exit_button.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

    def on_closing():
        root.destroy()
        input_win.destroy()

    input_win.protocol("WM_DELETE_WINDOW", on_closing)

def exit_application():
    play_sound1()
    messagebox.showinfo("Tournament Ended", "The tournament has ended.")
    root.quit()

root = tk.Tk()
root.title("Node Quality Calculator")
root.configure(bg='#f0f0f0')
font_button = ("Arial", 20, "bold")

# Configure grid layout for the main window
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

video_label = Label(root, bg='#A80000')
video_label.grid(row=0, column=0, sticky="nsew")

video_thread = threading.Thread(target=play_video, args=(video_label,))
video_thread.start()

button_open_input = tk.Button(root, text="Open Input Screen", font=font_button, command=open_input_window, bg='#2196F3', fg='#fff', width=20)
button_open_input.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
play_background_music()
root.mainloop()