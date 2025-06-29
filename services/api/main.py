from fastapi import FastAPI, UploadFile, File, HTTPException
from aws_utils import list_buckets, upload_file_to_bucket

from settings import EXT_FILES

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

@app.post("/upload/{bucket_name}")
async def upload_video(bucket_name: str, file: UploadFile = File(...)):

    if not file.filename.lower().endswith(EXT_FILES):
        raise HTTPException(
            status_code=400, 
            detail="error: the file is not a valid video."
        )

    success = upload_file_to_bucket(
        bucket_name=bucket_name, 
        file_obj=file.file, 
        filename=file.filename
    )
    if not success:
        raise HTTPException(
            status_code=500, 
            detail="error: erro uploading."
        )
    
    return {"message": f"{file.filename} uploaded to bucket {bucket_name} successfully."}


