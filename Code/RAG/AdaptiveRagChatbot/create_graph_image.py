from create_graph import app

from IPython.display import Image, display

##save the image to a file named graph.png
image = Image(app.get_graph().draw_mermaid_png())

with open("graph.png", "wb") as f:
    f.write(image.data)