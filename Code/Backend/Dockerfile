
# Use a lightweight Python base image suitable for your Python version
FROM python:3.12.10

# Set the working directory inside the container
WORKDIR /app

# --- Copy Project Files ---
COPY ./requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN --mount=type=cache,target=/root/.cache \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"


COPY start.py /app/
COPY . .


# Copy the .env file (for local testing/build; use platform secrets for production)
COPY .env /app/.env

# --- ChromaDB Persistence Hint ---
VOLUME /app/Backend/chroma_db

# --- Application Configuration ---
EXPOSE 8080

# --- Startup Command ---
CMD ["python", "start.py"]