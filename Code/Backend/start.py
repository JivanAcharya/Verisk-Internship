def start_app():
    import uvicorn
    from dotenv import load_dotenv, dotenv_values
    load_dotenv()

    env_vars = dotenv_values()
    # print(int(env_vars.get("PORT", 8000)),(env_vars.get("DEPLOYMENT") or "DEV"))
    uvicorn.run(
        "app.main:app",
        host = "0.0.0.0",
        port = int(env_vars.get("PORT", 8000)),
        reload = True if (env_vars.get("DEPLOYMENT") or "DEV").upper()!= "PROD" else False
    )
    
if __name__ == "__main__":
    start_app()