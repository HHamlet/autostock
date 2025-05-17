import uvicorn
from fastapi import FastAPI

from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.car import router as car_router
from app.api.v1.endpoints.categories import router as cat_router
from app.api.v1.endpoints.manufacturers import router as man_router
from app.api.v1.endpoints.warehouses import router as ware_router
from app.api.v1.endpoints.parts import router as part_router


app = FastAPI(title="Auto Parts Stock ...",
              description="An API for managing an auto parts and Stock/Warehouse ",
              version="0.1")

app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(car_router,  prefix="/api/v1/cars", tags=["cars"])
app.include_router(cat_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(man_router, prefix="/api/v1/manufacturers", tags=["manufacturer"])
app.include_router(ware_router, prefix="/api/v1/warehouses", tags=["warehouse"])
app.include_router(part_router, prefix="/api/v1/parts", tags=["parts"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
