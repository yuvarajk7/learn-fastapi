from typing import Any

from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

# The ASGI application uvicorn looks for: `fastapi dev main.py`
app = FastAPI()

# Stands in for a database — resets every time the server reloads
shipments: dict[int, dict[str, str | float]] = {
    12701: {"weight": 0.6, "content": "glassware", "status": "placed"},
    12702: {"weight": 2.3, "content": "books", "status": "shipped"},
    12703: {"weight": 1.1, "content": "electronics", "status": "delivered"},
    12704: {"weight": 3.5, "content": "furniture", "status": "in transit"},
    12705: {"weight": 0.9, "content": "clothing", "status": "returned"},
    12706: {"weight": 4.0, "content": "appliances", "status": "processing"},
    12707: {"weight": 1.8, "content": "toys", "status": "placed"},
}

# Query parameter: `id` is not in the path, so FastAPI reads it from the
# query string (/shipment?id=12701) and rejects non-integers with a 422
@app.get("/shipment")
def get_shipment(id: int) -> dict[str, Any]:
    # Raising HTTPException is how you return an error status on purpose;
    # anything uncaught becomes a 500 instead
    if id not in shipments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesn't exist!"
        )
    
    shipment = shipments[id]
    return shipment


# Path and query parameters together: `field` matches the {field} placeholder,
# while `id` has no placeholder so it still comes from the query string
@app.get("/shipment/{field}")
def get_shipment_field(field: str, id: int) -> Any:
    # No existence check here, so a bad id or field raises a KeyError -> 500
    return shipments[id][field]


# Request body: parameters annotated with a dict (or a Pydantic model) are read
# from the JSON body, scalars like str/int/float are read from the query string.
# Careful: `Any` counts as non-scalar, so query_param lands in the body too
@app.post("/shipment")
def submit_shipment(query_param: Any, req_body: dict[str, Any]) -> dict[str, int]:
    print(f"\nQuery Param: {query_param}\n")
    # Extract fields from request body
    content = req_body["content"]
    weight = req_body["weight"]
    # Validate weight
    if weight > 25:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Maximum weight limit is 25 kgs"
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

# @app.post("/shipment")
# def submit_shipment(content: str, weight: float) -> dict[str, int]:
#     # Validate weight
#     if weight > 25:
#         raise HTTPException(
#             status_code=status.HTTP_406_NOT_ACCEPTABLE,
#             detail="Maximum weight limit is 25 kgs"
#         )
#     # Create and assign shipment a new id
#     new_id = max(shipments.keys()) + 1

#     shipments[new_id] = {
#         "content": content,
#         "weight": weight,
#         "status": "placed",
#     }
#     # Return id for later use
#     return {"id": new_id}

# Serves the Scalar docs UI from the auto-generated schema at /openapi.json.
# include_in_schema=False keeps this route out of the docs it renders
@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="My API",
    )