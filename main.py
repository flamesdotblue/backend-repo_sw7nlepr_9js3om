import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Contributor, PickupRequest, WasteStat

app = FastAPI(title="Smart Waste Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Smart Waste Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", "") or "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:60]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:60]}"
    return response


# Public API: Impact stats for the website
@app.get("/stats", response_model=WasteStat)
def get_stats():
    """Return latest impact statistics. Falls back to defaults if none exist."""
    try:
        docs = get_documents("wastestat", limit=1)
        if docs:
            doc = docs[-1]
            return WasteStat(
                tons_recycled=int(doc.get("tons_recycled", 2000)),
                biogas_kg=int(doc.get("biogas_kg", 10000)),
                landfill_reduction_pct=int(doc.get("landfill_reduction_pct", 15)),
            )
    except Exception:
        # If DB not configured, serve defaults
        pass
    return WasteStat(tons_recycled=2000, biogas_kg=10000, landfill_reduction_pct=15)


# Contributor onboarding
@app.post("/contributors")
def create_contributor(payload: Contributor):
    try:
        inserted_id = create_document("contributor", payload)
        return {"id": inserted_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ContributorsQuery(BaseModel):
    type: Optional[str] = None
    city: Optional[str] = None
    limit: Optional[int] = 50


@app.post("/contributors/search")
def search_contributors(query: ContributorsQuery):
    try:
        filt = {}
        if query.type:
            filt["type"] = query.type
        if query.city:
            filt["city"] = query.city
        docs = get_documents("contributor", filter_dict=filt, limit=query.limit or 50)
        for d in docs:
            d["_id"] = str(d.get("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Pickup requests
@app.post("/pickups")
def create_pickup(payload: PickupRequest):
    try:
        inserted_id = create_document("pickuprequest", payload)
        return {"id": inserted_id, "status": "scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
