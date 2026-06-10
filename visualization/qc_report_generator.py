"""
Bundles all PNG figures in a folder into a single multi-page PDF report,
resizing images to a common size. Used to compile QC figures (e.g. from
qc_figure_generator.py) into one shareable document.
"""

from PIL import Image
import os

# Folder containing PNGs
input_folder = 'path/to/VELMA_Watersheds/Skokomish/Analysis/3April'
output_pdf = f'{input_folder}/Skokomish_3April.pdf'

# Get all PNG files and sort them
png_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.png')])

# Load and convert to RGB
images = [Image.open(os.path.join(input_folder, f)).convert('RGB') for f in png_files]

# Find the smallest image size (width, height)
min_size = min((img.size for img in images), key=lambda x: x[0] * x[1])

resized_images = [img.resize(min_size, Image.Resampling.LANCZOS) for img in images]

# Save to PDF
if resized_images:
    resized_images[0].save(
        os.path.join(input_folder, output_pdf),
        save_all=True,
        append_images=resized_images[1:]
    )
    print(f"Saved {len(resized_images)} resized images to {output_pdf}")
else:
    print("No PNG files found.")
