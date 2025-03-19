from pptx import Presentation
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Initialize Tkinter
root = tk.Tk()
root.withdraw()  # Hide the main Tkinter window

# Open file dialog to select the PowerPoint file
file_path = filedialog.askopenfilename(
    title="Select a PowerPoint Template",
    filetypes=[("PowerPoint Files", "*.pptx")]
)

# Check if file is selected
if not file_path:
    messagebox.showwarning("No file selected", "You didn't select a file. Exiting...")
    exit()

# Load the existing PowerPoint presentation
ppt = Presentation(file_path)

# Modify the first slide
slide = ppt.slides[0]  # 0 means the first slide

# Check if the slide has a title placeholder
if slide.shapes.title:
    title = simpledialog.askstring("Slide Title", "Enter title for the first slide:")
    slide.shapes.title.text = title if title else "Default Title"

# Check for subtitle placeholder
for shape in slide.shapes:
    if hasattr(shape, "placeholder_format") and shape.placeholder_format.idx == 1:
        subtitle = simpledialog.askstring("Slide Subtitle", "Enter subtitle for the first slide:")
        shape.text = subtitle if subtitle else "Default Subtitle"
        break

# Ask for the number of new slides
num_slides = simpledialog.askinteger("Slide Count", "How many new slides do you want to create?", minvalue=1)

for i in range(num_slides):
    # Create a new slide with title and content layout
    slide_layout = ppt.slide_layouts[1]  # Title and Content layout
    new_slide = ppt.slides.add_slide(slide_layout)

    # Set title and content for the new slide
    if new_slide.shapes.title:
        title = simpledialog.askstring(f"Slide {i + 2} Title", f"Enter title for slide {i + 2}:")
        new_slide.shapes.title.text = title if title else f"Slide {i + 2} Title"

    for shape in new_slide.shapes:
        if hasattr(shape, "placeholder_format") and shape.placeholder_format.idx == 1:
            content = simpledialog.askstring(f"Slide {i + 2} Content", f"Enter content for slide {i + 2}:")
            shape.text = content if content else f"Content for slide {i + 2}"
            break

# Save the modified PowerPoint file
output_file = filedialog.asksaveasfilename(
    title="Save Updated Presentation",
    defaultextension=".pptx",
    filetypes=[("PowerPoint Files", "*.pptx")]
)

if output_file:
    ppt.save(output_file)
    messagebox.showinfo("Success", f"Presentation updated successfully!\nSaved as {output_file}")
else:
    messagebox.showwarning("Save Cancelled", "The file was not saved.")
