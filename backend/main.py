from common.utils import *
from __init__ import __init__
# Create an instance of the FastAPI class
app = FastAPI()

# Define a route for the home endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}

os.makedirs("uploads", exist_ok=True)

# Mount static folder
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(__init__)