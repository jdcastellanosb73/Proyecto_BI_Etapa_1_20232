import io
import joblib
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

pipe = joblib.load('pipeline.joblib')

templates = Jinja2Templates(directory="templates")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict/")
async def predict(file: UploadFile = File(None), text_input: str = Form(None)):
    try:
        if file:
            if not file.filename.endswith('.xlsx'):
                return JSONResponse(content={"error": "El archivo debe tener formato .xlsx"}, status_code=400)

            data = pd.read_excel(io.BytesIO(file.file.read()), engine='openpyxl')

        elif text_input:
            data = pd.DataFrame({'Textos_espanol': [text_input]})
        else:
            return JSONResponse(content={"error": "El texto no puede ser vacio"}, status_code=400)
        predictions = pipe.predict(data)
        if file:
            predictions_list = predictions.tolist()
            return JSONResponse(content={"predictions": predictions_list}, status_code=200)
        else:
            output = pd.DataFrame({'Textos_espanol': data['Textos_espanol'], 'sdg': predictions})
            excel_output = io.BytesIO()
            output.to_excel(excel_output, index=False)
            return FileResponse(excel_output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename='predictions.xlsx')

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
