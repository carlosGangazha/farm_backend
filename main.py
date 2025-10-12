from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User, Crop, Livestock, Field, Inventory,Task
from schemas import (
    UserCreate, UserLogin, Token, 
    CropResponse, CropCreate, 
    LivestockResponse, LivestockCreate,
    Coordinate, FieldCreate, FieldResponse,InventoryCreate,InventoryResponse,TaskResponse,TaskCreate
)
from auth import hash_password, verify_password, create_access_token
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Polygon
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Farm Management")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://ruth-project-64ut.vercel.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin"],
    expose_headers=["*"],
    max_age=3600,
)

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Farm Management API"}

# Authentication endpoints
@app.post("/signup", response_model=Token)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = (
        db.query(User)
        .filter((User.email == user.email) | (User.username == user.username))
        .first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.email}, new_user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email}, db_user.username)
    return {"access_token": token, "token_type": "bearer"}

# Crop endpoints
@app.post("/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(crop: CropCreate, db: Session = Depends(get_db)):
    new_crop = Crop(
        name=crop.name,
        area=crop.area,
        planting_date=crop.planting_date,
        harvest_date=crop.harvest_date
    )
    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)
    return new_crop

@app.get("/crops", response_model=list[CropResponse])
def get_crops(db: Session = Depends(get_db)):
    return db.query(Crop).all()

@app.get("/crops/{crop_id}", response_model=CropResponse)
def get_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return crop

@app.put("/crops/{crop_id}", response_model=CropResponse)
def update_crop(crop_id: int, crop_data: CropCreate, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    crop.name = crop_data.name
    crop.area = crop_data.area
    crop.planting_date = crop_data.planting_date
    crop.harvest_date = crop_data.harvest_date
    db.commit()
    db.refresh(crop)
    return crop

@app.delete("/crops/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    db.delete(crop)
    db.commit()
    return {"message": "Crop deleted successfully"}

# Livestock endpoints
@app.post("/livestock", response_model=LivestockResponse, status_code=status.HTTP_201_CREATED)
def create_livestock(livestock: LivestockCreate, db: Session = Depends(get_db)):
    new_livestock = Livestock(
        type=livestock.type,
        breed=livestock.breed,
        count=livestock.count,
        notes=livestock.notes
    )
    db.add(new_livestock)
    db.commit()
    db.refresh(new_livestock)
    return new_livestock

@app.get("/livestock", response_model=list[LivestockResponse])
def get_livestock(db: Session = Depends(get_db)):
    return db.query(Livestock).all()

@app.get("/livestock/{livestock_id}", response_model=LivestockResponse)
def get_single_livestock(livestock_id: int, db: Session = Depends(get_db)):
    livestock = db.query(Livestock).filter(Livestock.id == livestock_id).first()
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")
    return livestock

@app.put("/livestock/{livestock_id}", response_model=LivestockResponse)
def update_livestock(livestock_id: int, livestock_data: LivestockCreate, db: Session = Depends(get_db)):
    livestock = db.query(Livestock).filter(Livestock.id == livestock_id).first()
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")

    livestock.type = livestock_data.type
    livestock.breed = livestock_data.breed
    livestock.count = livestock_data.count
    livestock.notes = livestock_data.notes
    db.commit()
    db.refresh(livestock)
    return livestock

@app.delete("/livestock/{livestock_id}")
def delete_livestock(livestock_id: int, db: Session = Depends(get_db)):
    livestock = db.query(Livestock).filter(Livestock.id == livestock_id).first()
    if not livestock:
        raise HTTPException(status_code=404, detail="Livestock not found")

    db.delete(livestock)
    db.commit()
    return {"message": "Livestock deleted successfully"}

# Field endpoints
@app.post("/fields", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
def create_field(field: FieldCreate, db: Session = Depends(get_db)):
    coords = [(coord.lng, coord.lat) for coord in field.coordinates]
    polygon = Polygon(coords)
    center = polygon.centroid
    
    new_field = Field(
        name=field.name,
        area=field.area,
        ndvi=field.ndvi,
        geometry=from_shape(polygon, srid=4326),
        center_lat=center.y,
        center_lng=center.x,
        last_updated=datetime.utcnow()
    )
    
    db.add(new_field)
    db.commit()
    db.refresh(new_field)
    
    geom = to_shape(new_field.geometry)
    coordinates = [Coordinate(lat=lat, lng=lng) for lng, lat in geom.exterior.coords[:-1]]
    
    return FieldResponse(
        id=new_field.id,
        name=new_field.name,
        coordinates=coordinates,
        center=Coordinate(lat=new_field.center_lat, lng=new_field.center_lng),
        area=new_field.area,
        ndvi=new_field.ndvi,
        last_updated=new_field.last_updated or datetime.utcnow()
    )

@app.get("/fields", response_model=list[FieldResponse])
def get_fields(db: Session = Depends(get_db)):
    fields = db.query(Field).all()
    result = []
    
    for field in fields:
        geom = to_shape(field.geometry)
        coordinates = [Coordinate(lat=lat, lng=lng) for lng, lat in geom.exterior.coords[:-1]]
        result.append(FieldResponse(
            id=field.id,
            name=field.name,
            coordinates=coordinates,
            center=Coordinate(lat=field.center_lat, lng=field.center_lng),
            area=field.area,
            ndvi=field.ndvi,
            last_updated=field.last_updated or datetime.utcnow()
        ))
    
    return result

@app.get("/fields/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    geom = to_shape(field.geometry)
    coordinates = [Coordinate(lat=lat, lng=lng) for lng, lat in geom.exterior.coords[:-1]]
    
    return FieldResponse(
        id=field.id,
        name=field.name,
        coordinates=coordinates,
        center=Coordinate(lat=field.center_lat, lng=field.center_lng),
        area=field.area,
        ndvi=field.ndvi,
        last_updated=field.last_updated or datetime.utcnow()
    )

@app.put("/fields/{field_id}", response_model=FieldResponse)
def update_field(field_id: int, field_data: FieldCreate, db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    
    coords = [(coord.lng, coord.lat) for coord in field_data.coordinates]
    polygon = Polygon(coords)
    center = polygon.centroid
    
    field.name = field_data.name
    field.area = field_data.area
    field.ndvi = field_data.ndvi
    field.geometry = from_shape(polygon, srid=4326)
    field.center_lat = center.y
    field.center_lng = center.x
    
    db.commit()
    db.refresh(field)
    
    geom = to_shape(field.geometry)
    coordinates = [Coordinate(lat=lat, lng=lng) for lng, lat in geom.exterior.coords[:-1]]
    
    return FieldResponse(
        id=field.id,
        name=field.name,
        coordinates=coordinates,
        center=Coordinate(lat=field.center_lat, lng=field.center_lng),
        area=field.area,
        ndvi=field.ndvi,
        last_updated=field.last_updated or datetime.utcnow()
    )

@app.delete("/fields/{field_id}")
def delete_field(field_id: int, db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    db.delete(field)
    db.commit()
    return {"message": "Field deleted successfully"}

# Inventory endpoints
@app.post("/inventory", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(item: InventoryCreate, db: Session = Depends(get_db)):
    new_item = Inventory(
        name=item.name,
        quantity=item.quantity,
        unit=item.unit,
        min_stock=item.min_stock
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/inventory", response_model=list[InventoryResponse])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(Inventory).all()

@app.get("/inventory/{item_id}", response_model=InventoryResponse)
def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@app.put("/inventory/{item_id}", response_model=InventoryResponse)
def update_inventory_item(item_id: int, item_data: InventoryCreate, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item.name = item_data.name
    item.quantity = item_data.quantity
    item.unit = item_data.unit
    item.min_stock = item_data.min_stock
    db.commit()
    db.refresh(item)
    return item

@app.delete("/inventory/{item_id}")
def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    db.delete(item)
    db.commit()
    return {"message": "Inventory item deleted successfully"}

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        priority=task.priority,
        due_date=task.due_date,
        assigned_to=task.assigned_to,
        status="Pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = task_data.title
    task.priority = task_data.priority
    task.due_date = task_data.due_date
    task.assigned_to = task_data.assigned_to
    db.commit()
    db.refresh(task)
    return task

@app.patch("/tasks/{task_id}/toggle", response_model=TaskResponse)
def toggle_task_status(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "Completed" if task.status == "Pending" else "Pending"
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}