from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.routers.auth import get_current_user
from app.utils.time_utils import convert_date_to_iso_date, get_datetime, get_current_timestamp_utc
from app.database import data_collection
from datetime import timedelta

router = APIRouter(prefix="/api", tags=["Websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive filter configuration from the client
            filter_data = await websocket.receive_json()
            device_id = filter_data.get("device_id")
            start_date = filter_data.get("start_date")
            end_date = filter_data.get("end_date")
            print('start_date', start_date, end_date)

            match_condition = {
                "device_id": device_id,
            }            
            # Determine the date range
            if start_date and end_date:
                start_date = convert_date_to_iso_date(start_date)
                end_date = convert_date_to_iso_date(end_date)
                match_condition["timestamp"] = {"$gte": start_date, "$lt": end_date}                
                limit = None  # No limit for full range queries
            else:
                limit = 2  # Fetch only the latest document

            # Build the aggregation pipeline
            pipeline = [
                {
                    "$match": match_condition
                },
                {
                    "$project": {
                        "_id": 0,
                        "timestamp": 1,
                        "device_id": 1,
                        "tds": 1,
                        "tds_limit": 1,
                        "ph": 1,
                        "ph_limit": 1,
                        "orp": 1,
                        "orp_limit": 1,
                        "time_based_dose_start_seconds": 1,
                        "time_based_dose_stop_seconds": 1,
                        "ph_dose_type": 1
                    }
                },
                {
                    "$sort": {
                        "timestamp": -1
                    }
                },
            ]

            # Apply limit if fetching only the latest record
            if limit:
                pipeline.append({"$limit": limit})

            print("pipeline",pipeline)
            # Execute the aggregation pipeline
            data = data_collection.aggregate(pipeline).to_list(None)

            results = []
            counter = 0
            status = False
            for doc in data:
                if counter == 0:
                    time_difference = get_current_timestamp_utc().replace(tzinfo=None) - doc.get("timestamp")
                    print('time_difference', time_difference)
                    status = time_difference < timedelta(minutes=1, seconds=30)
                counter += 1

                if "timestamp" in doc:
                    doc["timestamp"] = doc["timestamp"].isoformat()

                results.append(doc)
            
            # Send the aggregated data to the client
            await websocket.send_json({
                "data": data,
                "status": status
            })
    except WebSocketDisconnect:
        print("WebSocket disconnected")
