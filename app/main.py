from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, dashboard, products, orders, categories, offers, reports, users, cart, wholesale
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TruMix E-Commerce API",
    description="Complete backend API for TruMix online store with admin panel. Features include authentication, product catalog, order management with server-side financial calculations, shopping cart, payments with COD support, coupon management, and comprehensive admin dashboard.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Mount static files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
origins = [
    "http://localhost",
    "http://localhost:3000", # React default
    "https://www.trumix.co.in",
    "https://trumix.co.in",
    "https://www.trumix.co.in/",
    "https://trumix.co.in/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)
app.include_router(offers.router)
app.include_router(reports.router)
app.include_router(cart.router)
app.include_router(wholesale.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to TruMix Admin API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
