from pptx import Presentation
import tkinter as tk
from tkinter import filedialog

# Open file dialog to select the PowerPoint file
root = tk.Tk()
root.withdraw()  # Hide the main Tkinter window

file_path = filedialog.askopenfilename(
    title="Select a PowerPoint Template",
    filetypes=[("PowerPoint Files", "*.pptx")]
)

# Check if file is selected
if not file_path:
    print("No file selected. Exiting...")
else:
    # Load the existing PowerPoint presentation
    ppt = Presentation(file_path)

    # Ensure the first slide remains unchanged
    slide = ppt.slides[0]  # 0 means the first slide

    # Check if the slide has a title placeholder
    if slide.shapes.title:
        slide.shapes.title.text = "Demo of the title placeholder"

    # Check for subtitle placeholder
    for shape in slide.shapes:
        if shape.placeholder_format.idx == 1:  # Subtitle placeholder typically has index 1
            shape.text = "Demo of the subtitle placeholder"
            break

    # Create a new slide with title and content layout
    slide_layout = ppt.slide_layouts[1]  # Title and Content layout
    new_slide = ppt.slides.add_slide(slide_layout)

    # Set title and content for the new slide
    if new_slide.shapes.title:
        new_slide.shapes.title.text = "New Slide Title"
    
    for shape in new_slide.shapes:
        if shape.placeholder_format.idx == 1:  # Content placeholder typically has index 1
            shape.text = "This is the content of the new slide."
            break

    # Save the modified PowerPoint file
    output_file = "updated_presentation.pptx"
    ppt.save(output_file)

    print(f"Presentation updated successfully! Saved as {output_file}")