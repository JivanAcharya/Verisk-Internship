from .create_graph import chatbot

# Run
user_input = input("What are the scholarships available in MIT ?")
inputs = {
    "question": user_input
}

resp = chatbot.invoke(inputs)

print(resp["question"],resp["generation"])
