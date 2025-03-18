from create_graph import app

# from IPython.display import Image, display

# ##save the image to a file named graph.png
# image = Image(app.get_graph().draw_mermaid_png())

# with open("graph.png", "wb") as f:
#     f.write(image.data)

# Run
user_input = input("Enter a question: ")
inputs = {
    "question": user_input
}

resp = app.invoke(inputs)

print(resp["question"],resp["generation"])

# for output in app.stream(inputs):
#     for key, value in output.items():
#         # Node
#         print(f"Node '{key}':")
#     print("\n---\n")

# # Final generation
# print(value["generation"])