import boto3
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from io import StringIO
import uvicorn

BUCKET_NAME = "smmbucket-345-ueia-so"
FILE_KEY = "datos_usuarios.csv"

class UserData(BaseModel):
	nombre: str
	edad: int
	altura: float

app = FastAPI()
s3_client = boto3.client('s3')

@app.get("/")
def read_root():
	return {"mensaje": "API de Sistemas Operativos funcionanddo"}

@app.post("/save-data/")
async def save_data(data: UserData):
	try:
		try:
			obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
			csv_content = obj['Body'].read().decode('utf-8')
			df = pd.read_csv(StringIO(csv_content))
		except s3_client.exceptions.NoSuchKey:
			df = pd.DataFrame(columns=['nombre','edad','altura'])
		new_data_df = pd.DataFrame([data.dict()])
		df = pd.concat([df, new_data_df], ignore_index=True)

		csv_buffer = StringIO()
		df.to_csv(csv_buffer, index=False)
		csv_string = csv_buffer.getvalue()

		s3_client.put_object(Bucket=BUCKET_NAME, Key=FILE_KEY, Body=csv_string)
		return {
			"mensaje": "Saved data/succesfully updated in S3", 
			"total rows": len(df)
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Management error with S3: {str(e)}")

@app.get("/count-rows/")
async def count_rows():
	try:
		obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
		csv_content = obj['Body'].read().decode('utf-8')

		df = pd.read_csv(StringIO(csv_content))
		num_filas = len(df)
		return {"row_number": num_filas}
	except s3_client.exceptions.NoSuchKey:
		return {"row_number": 0}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Reading Error S3: {str(e)}")

if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=8000)
