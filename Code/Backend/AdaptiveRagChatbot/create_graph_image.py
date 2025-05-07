import argparse
from .create_graph import chatbot
from IPython.display import Image

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate and save a graph image.")
parser.add_argument("filename", type=str, help="Output image filename (e.g., graph.png)")
args = parser.parse_args()

# Generate graph image
image = Image(chatbot.get_graph().draw_mermaid_png())

# Save image with the provided filename
with open(f"AdaptiveRagChatbot/graph_images/{args.filename}", "wb") as f:
    f.write(image.data)

print(f"Graph image saved as {args.filename}")
