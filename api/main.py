from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import base64
import logging
import qrcode
import boto3
import os
from io import BytesIO
from typing import Optional

from pydantic import BaseModel, HttpUrl

# Loading Environment variable (AWS Access Key and Secret Key)
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 Configuration
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
bucket_name = os.getenv("AWS_BUCKET_NAME")
aws_region = os.getenv("AWS_REGION")
s3 = None

if aws_access_key and aws_secret_key and bucket_name:
    client_kwargs = {
        'aws_access_key_id': aws_access_key,
        'aws_secret_access_key': aws_secret_key,
    }

    if aws_region:
        client_kwargs['region_name'] = aws_region

    s3 = boto3.client('s3', **client_kwargs)

class QRRequest(BaseModel):
    url: HttpUrl


class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


_ITEMS = [
    Item(id=1, name="QR Code Generator", description="Service status endpoint."),
    Item(id=2, name="Generate QR", description="POST /generate-qr/ to create codes."),
]

@app.get("/")
async def healthcheck():
    return {"status": "ok"}

@app.post("/generate-qr/")
async def generate_qr(
    payload: Optional[QRRequest] = Body(default=None),
    url_query: Optional[HttpUrl] = Query(default=None, alias="url")
):
    url = None
    if payload and payload.url:
        url = str(payload.url)
    elif url_query:
        url = str(url_query)

    if not url:
        raise HTTPException(status_code=422, detail="A valid URL is required.")

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate file name for S3
    file_name = f"qr_codes/{url.split('//')[-1]}.png"

    upload_error: Optional[str] = None
    if s3:
        try:
            img_byte_arr.seek(0)
            # Upload to S3
            put_kwargs = {
                "Bucket": bucket_name,
                "Key": file_name,
                "Body": img_byte_arr,
                "ContentType": "image/png",
            }

            if os.getenv("AWS_S3_SKIP_ACL", "").lower() not in {"1", "true", "yes"}:
                put_kwargs["ACL"] = "public-read"

            s3.put_object(**put_kwargs)

            # Generate the S3 URL
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            return {"qr_code_url": s3_url, "storage": "s3"}
        except Exception as exc:
            upload_error = str(exc)

    # Fallback to returning the QR code as a base64 data URI
    img_byte_arr.seek(0)
    encoded_qr = base64.b64encode(img_byte_arr.read()).decode("ascii")
    data_uri = f"data:image/png;base64,{encoded_qr}"

    response = {"qr_code_url": data_uri, "storage": "inline"}
    if upload_error:
        warning_msg = f"S3 upload failed: {upload_error}"
        logger.error(warning_msg)
        response["warning"] = warning_msg

    return response


@app.get("/items", response_model=list[Item])
async def list_items():
    return _ITEMS
