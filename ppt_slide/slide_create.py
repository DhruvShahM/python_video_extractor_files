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

    # Modify the first slide
    slide = ppt.slides[0]  # 0 means the first slide

    # Check if the slide has a title placeholder
    if slide.shapes.title:
        print("Enter title for the first slide:")
        slide.shapes.title.text = input()

    # Check for subtitle placeholder
    for shape in slide.shapes:
        if shape.placeholder_format.idx == 1:  # Subtitle placeholder typically has index 1
            print("Enter subtitle for the first slide:")
            shape.text = input()
            break

    # Ask for the number of new slides to create
    print("How many new slides do you want to create?")
    num_slides = int(input())

    for i in range(num_slides):
        # Create a new slide with title and content layout
        slide_layout = ppt.slide_layouts[1]  # Title and Content layout
        new_slide = ppt.slides.add_slide(slide_layout)

        # Set title and content for the new slide
        if new_slide.shapes.title:
            print(f"Enter title for slide {i + 2}:")
            new_slide.shapes.title.text = input()
        
        for shape in new_slide.shapes:
            if shape.placeholder_format.idx == 1:  # Content placeholder typically has index 1
                print(f"Enter content for slide {i + 2}:")
                shape.text = input()
                break

    # Save the modified PowerPoint file
    output_file = "updated_presentation.pptx"
    ppt.save(output_file)

    print(f"Presentation updated successfully! Saved as {output_file}")
