import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Path as FastAPIPath, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

# -----------------------------
# File Path
# -----------------------------
BASE_DIR = Path(__file__).parent
FILE_PATH = BASE_DIR / "patients.json"

# -----------------------------
# Pydantic Model
# -----------------------------
class Patient(BaseModel):
    id: str = Field(..., example="P007")
    name: str = Field(..., min_length=2)
    city: str
    age: int = Field(..., gt=0)
    gender: Literal["Male", "Female"]
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    bmi: float


# -----------------------------
# Helper Functions
# -----------------------------
def load_data():
    if not FILE_PATH.exists():
        with open(FILE_PATH, "w") as f:
            json.dump({}, f)

    with open(FILE_PATH, "r") as f:
        return json.load(f)


def save_data(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {"message": "Patient Management System API"}


@app.get("/about")
def about():
    return {
        "message": "A fully functional API to manage patient records."
    }


# -----------------------------
# View All Patients
# -----------------------------
@app.get("/view")
def view_all():
    return load_data()


# -----------------------------
# View Single Patient
# -----------------------------
@app.get("/patient/{patient_id}")
def view_patient(
    patient_id: str = FastAPIPath(
        ...,
        description="Patient ID",
        example="P001"
    )
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return data[patient_id]


# -----------------------------
# Sort Patients
# -----------------------------
@app.get("/sort")
def sort_patients(
    sort_by: str = Query(...),
    order: str = Query("asc")
):
    valid_fields = ["height", "weight", "bmi"]

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Valid fields are {valid_fields}"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be asc or desc"
        )

    data = load_data()

    reverse = True if order == "desc" else False

    sorted_data = sorted(
        data.values(),
        key=lambda x: x.get(sort_by),
        reverse=reverse,
    )

    return sorted_data


# -----------------------------
# Create Patient
# -----------------------------
@app.post("/create")
def create_patient(patient: Patient):

    data = load_data()

    if patient.id in data:
        raise HTTPException(
            status_code=400,
            detail=f"Patient with ID {patient.id} already exists"
        )

    data[patient.id] = patient.model_dump(exclude={"id"})

    save_data(data)

    return JSONResponse(
        status_code=201,
        content={
            "message": f"Patient with ID {patient.id} created successfully"
        },
    )


# -----------------------------
# Update Patient
# -----------------------------
@app.put("/update/{patient_id}")
def update_patient(
    patient_id: str,
    patient: Patient
):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    data[patient_id] = patient.model_dump(exclude={"id"})

    save_data(data)

    return {
        "message": f"Patient {patient_id} updated successfully"
    }


# -----------------------------
# Delete Patient
# -----------------------------
@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    del data[patient_id]

    save_data(data)

    return {
        "message": f"Patient {patient_id} deleted successfully"
    }