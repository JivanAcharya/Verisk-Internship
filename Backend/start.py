import multiprocessing

def start_app():
    import uvicorn
    from dotenv import load_dotenv, dotenv_values
    load_dotenv()

    env_vars = dotenv_values()

    # Get number of CPU cores
    num_cores = multiprocessing.cpu_count()

    # Decide whether to use reload mode (only for non-production)
    is_reload = (env_vars.get("DEPLOYMENT") or "DEV").upper() != "PROD"
    print("Is_reload: ", is_reload)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(env_vars.get("PORT", 8000)),
        reload=is_reload,
        workers=None if is_reload else num_cores  # `reload` and `workers` cannot be used together
    )

if __name__ == "__main__":
    start_app()



# def start_app():
#     import uvicorn
#     from dotenv import load_dotenv, dotenv_values
#     load_dotenv()

#     env_vars = dotenv_values()
#     # print(int(env_vars.get("PORT", 8000)),(env_vars.get("DEPLOYMENT") or "DEV"))
#     uvicorn.run(
#         "app.main:app",
#         host = "0.0.0.0",
#         port = int(env_vars.get("PORT", 8000)),
#         reload = True if (env_vars.get("DEPLOYMENT") or "DEV").upper()!= "PROD" else False

#     )
    
# if __name__ == "__main__":
#     start_app()