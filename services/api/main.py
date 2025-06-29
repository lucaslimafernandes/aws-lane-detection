from fastapi import FastAPI, UploadFile, File, HTTPException
from aws_utils import (
    list_buckets, 
    upload_file_to_bucket,
    send_message_to_queue
)

from settings import (
    EXT_FILES,
    BUCKET_NAME, 
    ENDPOINT_URL,
)


app = FastAPI()

@app.get("/")
def hello():
    return {
        "status": "healthy",
    }

@app.get("/buckets")
def get_buckets():
    buckets = list_buckets()
    return {"buckets": [b["Name"] for b in buckets]}

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(EXT_FILES):
        raise HTTPException(
            status_code=400, 
            detail="error: the file is not a valid video."
        )

    success = upload_file_to_bucket(
        file_obj=file.file, 
        filename=file.filename
    )
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="error: erro uploading."
        )
    
    object_url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{file.filename}"

    msg = {
        "bucket": BUCKET_NAME,
        "filename": file.filename,
        "url": object_url,
        "event": "UPLOAD_VIDEO"
    }
    send_message_to_queue(msg)
    
    return {
        "message": f"{file.filename} uploaded successfully.",
        "s3_url": object_url,
    }


