'''API to host our model'''

import json
from typing import Literal, List, Union
from pickle import load
import pandas as pd
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title='Car Rental Price Prediction')

class Car(BaseModel):
    '''input data class'''
    model_key: Literal['Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
       'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
       'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
       'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT',
       'Subaru', 'Suzuki', 'Toyota', 'Yamaha']
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: Literal['diesel', 'petrol', 'hybrid_petrol', 'electro']
    paint_color: Literal['black', 'grey', 'white', 'red', 'silver', 'blue', 'orange',
       'beige', 'brown', 'green']
    car_type: Literal['convertible', 'coupe', 'estate', 'hatchback', 'sedan',
       'subcompact', 'suv', 'van']
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

with open("model.pkl", "rb") as f:
    model = load(f)
with open("preprocessor.pkl", "rb") as f:
    preprocessor = load(f)

@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url='/docs')
    return response

@app.post("/predict")
async def predict(cars: List[Car]):
    cars_data = preprocessor.transform(pd.DataFrame(jsonable_encoder(cars)))
    prediction = model.predict(cars_data)
    response = json.dumps({'prediction' : prediction.tolist()})
    return response

# Define webserver to host our API
if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
