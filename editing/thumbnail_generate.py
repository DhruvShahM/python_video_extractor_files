import tkinter as tk
from tkinter import filedialog, messagebox
import comtypes.client
import os
import tempfile
import time

def export_first_slide_to_image(pptx_path):
    powerpoint = comtypes.client.CreateObject("PowerPoint.Application")
    powerpoint.Visible = 1

    try:
        presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)

        # Create a safe temporary output file name
        timestamp = int(time.time())
        safe_filename = f"slide1_thumbnail_{timestamp}.png"
        safe_path = os.path.join(tempfile.gettempdir(), safe_filename)

        # Export the first slide
        presentation.Slides(1).Export(safe_path, "PNG")
        presentation.Close()
        powerpoint.Quit()

        return safe_path
    except Exception as e:
        powerpoint.Quit()
        raise e

def main():
    root = tk.Tk()
    root.withdraw()

    # Select the PowerPoint file
    pptx_path = filedialog.askopenfilename(
        title="Select PowerPoint File",
        filetypes=[("PowerPoint Files", "*.pptx")]
    )
    if not pptx_path:
        return

    try:
        # Export first slide to a safe location
        saved_path = export_first_slide_to_image(pptx_path)

        # Ask user where they want to save the PNG
        output_path = filedialog.asksaveasfilename(
            title="Save Thumbnail As",
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")]
        )
        if not output_path:
            return

        # Copy the temp PNG to the user-specified location
        with open(saved_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())

        messagebox.showinfo("Success", f"Thumbnail saved to:\n{output_path}")
        os.startfile(output_path)

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n\n{str(e)}")

if __name__ == "__main__":
    main()
