from typing import Any

from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

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

### Read a shipment by id
### `id` has no {placeholder} in the path, so it is a query parameter:
### GET /shipment?id=12701 — a non-integer gets rejected with a 422
@app.get("/shipment")
def get_shipment(id: int) -> dict[str, Any]:
    # Check for shipment with given id
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!",
        )

    return shipments[id]

### Create a new shipment with content and weight
### Note these are scalars (str/float), so FastAPI reads them from the query
### string rather than the JSON body: POST /shipment?content=socks&weight=1.2
@app.post("/shipment")
def submit_shipment(content: str, weight: float) -> dict[str, int]:
    # Validate weight
    if weight > 25:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum weight limit is 25 kgs",
        )
    # Create and assign shipment a new id
    new_id = max(shipments.keys()) + 1
    # Add to shipments dict
    shipments[new_id] = {
        "content": content,
        "weight": weight,
        "status": "placed",
    }
    # Return id for later use
    return {"id": new_id}

### Update fields of a shipment
### PATCH is a partial update — dict[str, Any] makes `body` come from the JSON
### body, and .update() merges only the keys the caller actually sent
@app.patch("/shipment")
def update_shipment(id: int, body: dict[str, Any]) -> dict[str, Any]:
    # Update data with given fields
    shipments[id].update(body)
    return shipments[id]

### PUT is a full replacement — every field is required, so omitting one
### wipes it. Contrast with the PATCH above, which merges.
### Careful: the `status` parameter shadows the `status` imported from fastapi,
### so status.HTTP_* is unusable inside this function
@app.put("/shipment")
def shipment_update(
    id: int, content: str, weight: float, status: str
) -> dict[str, Any]:
    shipments[id] = {
        "content": content,
        "weight": weight,
        "status": status,
    }
    return shipments[id]


### Patch method using query params
### UNREACHABLE: update_shipment above already claims PATCH /shipment, and
### FastAPI matches the first registered route for a method+path pair.
### Rename the path (or delete update_shipment) to reach this one.
### Optional query params: giving them `= None` defaults makes them optional,
### so the caller sends only the fields they want changed
@app.patch("/shipment")
def patch_shipment(
    # required
    id: int,
    # not required
    content: str | None = None,
    weight: float | None = None,
    status: str | None = None,
):
    shipment = shipments[id]

    # Update the provided fields
    if content:
        shipment["content"] = content
    if weight:
        shipment["weight"] = weight
    if status:
        shipment["status"] = status

    # Reflect changes in datastore
    shipments[id] = shipment
    return shipment


### Patch method using request body
### Different url as same method exists
@app.patch("/shipment_field")
def patch_shipment_with_req_body(id: int, body: dict[str, Any]) -> dict[str, Any]:
    # Update data with given fields
    shipments[id].update(body)
    return shipments[id]


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