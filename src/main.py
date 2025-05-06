from fastapi import FastAPI
from src.entrypoints.rest import router
import uvicorn
from dependencies import get_prod_container


def create_app():
    app = FastAPI()
    app.state.container = get_prod_container()
    app.include_router(router=router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3002, reload=True)
