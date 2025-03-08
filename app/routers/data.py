from fastapi import APIRouter, Depends
import pandas as pd
from app.database import data_collection
from app.routers.auth import get_current_user
from app.schemas import SensorDataRequest, WaterQualityData
from fastapi.responses import StreamingResponse
from app.utils.time_utils import get_current_timestamp_utc

router = APIRouter(prefix="/api/data", tags=["Data"])

@router.post("/")
async def receive_data(data: SensorDataRequest):
    timestamp = get_current_timestamp_utc()
    data_to_insert = data.dict()
    data_to_insert["timestamp"] = timestamp
    data = data_collection.insert_one(data_to_insert)
    return {"message": "Data saved successfully"}

@router.get("/export")
def export_data(user=Depends(get_current_user)):
    data = data_collection.find({"device_id": user["device_id"]}).to_list(1000)
    df = pd.DataFrame(data)
    return StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=data_export.csv"}
    )

@router.post("/example")
async def receive_water_quality(data: WaterQualityData):
    print(f"Received water quality data - pH: {data.pH}, TDS: {data.TDS}, ORP: {data.ORP}")
    return {"message": "Data received successfully"}