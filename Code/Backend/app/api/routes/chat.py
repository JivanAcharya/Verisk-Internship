

# API endpoint
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        response = generate_response(request.query, request.thread_id)
        store_chat_history(request.thread_id, request.query, response)
        return {"response": response, "session_id": request.thread_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
