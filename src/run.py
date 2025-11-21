from src.main.server.fast_api.server import create_fast_api_app
import uvicorn


app = create_fast_api_app()



if __name__ == "__main__":
    uvicorn.run(
         app,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )