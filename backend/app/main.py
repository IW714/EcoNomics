from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .services.auth import verify_token

app = FastAPI()

# Configure CROS
origins = [
    "http://localhost:5173", # React frontend
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods
    allow_headers=["*"],    # Allow all HTTP headers
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

# Ex of protected route
@app.get("/protected")
def protected_route(user=Depends(verify_token)):
    return {"message": f"Hello, {user['uid']}"}
