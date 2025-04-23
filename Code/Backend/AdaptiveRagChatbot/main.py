from .create_graph import chatbot

# Run
user_input = input("Enter a question: ")
inputs = {
    "question": user_input
}

resp = chatbot.invoke(inputs)

print(resp["question"],resp["generation"])
