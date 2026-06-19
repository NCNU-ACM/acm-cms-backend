from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import LoginRequest, LoginResponse
from auth import login
from routers import groups, events, members, showcase, announcements

app = FastAPI(title="NCNU ACM CMS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router)
app.include_router(events.router)
app.include_router(members.router)
app.include_router(showcase.router)
app.include_router(announcements.router)


@app.post("/auth/login", response_model=LoginResponse)
def auth_login(req: LoginRequest):
    token = login(req.username, req.password)
    return {"token": token}


@app.get("/")
def root():
    return {"status": "ok", "message": "NCNU ACM CMS API"}