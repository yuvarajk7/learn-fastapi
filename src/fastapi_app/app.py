from typing import Any

from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

from fastapi_app.schemas import ShipmentCreate, ShipmentRead, ShipmentUpdate

# The ASGI app uvicorn serves: `fastapi dev app.py`
app = FastAPI()

### Shipments datastore as dict
### In-memory only, so every edit is lost when the server reloads
shipments: dict[int, dict[str, Any]] = {
    12701: {"weight": 0.6, "content": "rubber ducks", "status": "placed"},
    12702: {"weight": 2.3, "content": "magic wands", "status": "shipped"},
    12703: {"weight": 1.1, "content": "unicorn horns", "status": "delivered"},
    12704: {"weight": 3.5, "content": "dragon eggs", "status": "in transit"},
    12705: {"weight": 0.9, "content": "wizard hats", "status": "returned"},
}

###  a shipment by id
@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int) -> dict[str, Any]:
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    return shipments[id]


@app.post("/shipment", response_model=None)
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:
    # Create and assign shipment a new id
    new_id = max(shipments.keys()) + 1
    # Add to shipments dict
    shipments[new_id] = {
        **shipment.model_dump(),
        "status": "placed",
    }
    # Return id for later use
    return {"id": new_id}


@app.patch("/shipment", response_model=ShipmentRead)
def update_shipment(id: int,  body: ShipmentUpdate) -> dict[str, Any]:
    # Update data with given fields
    shipments[id].update(body.model_dump(exclude_none=True))
    return shipments[id]


# @app.put("/shipment")
# def shipment_update(
#     id: int, content: str, weight: float, status: str
# ) -> dict[str, Any]:
#     shipments[id] = {
#         "content": content,
#         "weight": weight,
#         "status": status,
#     }
#     return shipments[id]


# ### Patch method using request body
# ### Different url as same method exists
# @app.patch("/shipment_field")
# def patch_shipment_with_req_body(id: int, body: dict[str, Any]) -> dict[str, Any]:
#     # Update data with given fields
#     shipments[id].update(body)
#     return shipments[id]


### Delete a shipment by id
### No existence check, so deleting an unknown id raises KeyError -> 500
### instead of a clean 404. shipments.pop(id, None) would silence it.
@app.delete("/shipment")
def delete_shipment(id: int) -> dict[str, str]:
    # Remove from datastore
    shipments.pop(id)

    return {"detail": f"Shipment with id #{id} is deleted!"}

### Scalar API Documentation
### Renders the auto-generated /openapi.json; include_in_schema=False keeps
### this route out of the docs it serves
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )