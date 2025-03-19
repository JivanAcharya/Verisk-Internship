import argparse
from create_graph import app
from IPython.display import Image

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate and save a graph image.")
parser.add_argument("filename", type=str, help="Output image filename (e.g., graph.png)")
args = parser.parse_args()

# Generate graph image
image = Image(app.get_graph().draw_mermaid_png())

# Save image with the provided filename
with open(f"graph_images/{args.filename}", "wb") as f:
    f.write(image.data)

print(f"Graph image saved as {args.filename}")
