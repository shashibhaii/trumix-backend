from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/api/v1/settings",
    tags=["Settings"]
)

@router.get("/", response_model=List[schemas.SettingResponse])
def get_settings(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db.query(models.GlobalSetting).all()

@router.put("/", response_model=Dict[str, str])
def update_settings(
    settings_update: schemas.SettingsUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    for key, value in settings_update.settings.items():
        db_setting = db.query(models.GlobalSetting).filter(models.GlobalSetting.key == key).first()
        if db_setting:
            db_setting.value = value
        else:
            new_setting = models.GlobalSetting(key=key, value=value)
            db.add(new_setting)
    
    db.commit()
    return {"status": "success", "message": "Settings updated successfully"}

@router.get("/{key}", response_model=schemas.SettingResponse)
def get_setting(
    key: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    setting = db.query(models.GlobalSetting).filter(models.GlobalSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting {key} not found")
    
    return setting
