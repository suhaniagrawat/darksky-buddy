from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from app.schemas import CommentOut
from app.services.supabase_client import supabase
import uuid
import shutil

router = APIRouter(prefix="/spots", tags=["Stargazing spots"])


@router.post("/spots")
async def add_spot(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    photo_url: str = Form(None),
    photo_file: UploadFile = File(None),
):
    
    keywords = {
        "desert": ["desert", "dune"],
        "mountain": ["mountain", "peak", "himalaya"],
        "beach": ["beach", "coast"],
        "forest": ["forest", "woods"],
        "lake": ["lake", "pond"],
        "sky": ["milky way", "stars", "sky"]
    }

    category = "general"
    content = f"{title} {description}".lower()
    for key, terms in keywords.items():
        if any(term in content for term in terms):
            category = key
            break

    # Handle file upload
    final_photo_url = photo_url
    if photo_file:
        file_location = f"static/uploads/{uuid.uuid4().hex}_{photo_file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(photo_file.file, buffer)
        final_photo_url = f"/{file_location}"

    # Insert spot
    data = {
        "title": title,
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "photo_url": final_photo_url,
        "upvotes": 0,
        "category": category
    }

    try:
        supabase.table("spots").insert(data).execute()
        return {"message": f"Spot added successfully under category '{category}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spots")
async def get_spots(search: str = Query(default=None, description="Search term for title or description")):
    try:
        if search:
            response = supabase.table("spots").select("*").ilike("title", f"%{search}%").execute()
            if not response.data:
                response = supabase.table("spots").select("*").ilike("description", f"%{search}%").execute()
        else:
            response = supabase.table("spots").select("*").execute()
        return {"spots": response.data}
    except Exception as e:
        return {"error": str(e)}


@router.post("/upvote_by_category")
def upvote_spot_by_category(category: str = Form(...), user_id: str = Form(...)):
    spot_result = supabase.table("spots").select("*").ilike("category", category).execute()
    if not spot_result.data:
        raise HTTPException(404, "No spot found for this category")

    spot = spot_result.data[0]
    spot_id = spot["id"]

    existing = supabase.table("upvotes").select("*").eq("spot_id", spot_id).eq("user_id", user_id).execute()
    if existing.data:
        raise HTTPException(400, "Already upvoted")

    supabase.table("upvotes").insert({"spot_id": spot_id, "user_id": user_id}).execute()
    new_count = spot["upvotes"] + 1
    supabase.table("spots").update({"upvotes": new_count}).eq("id", spot_id).execute()

    return {"message": f"Upvoted spot '{spot['title']}' in category '{category}' successfully"}


@router.post("/comments/by_category", response_model=CommentOut)
def add_comment_by_category(
    category: str = Form(...),
    user_id: str = Form(...),
    username: str = Form(...),
    text: str = Form(...)
):
    spot_result = supabase.table("spots").select("*").ilike("category", category).execute()
    if not spot_result.data:
        raise HTTPException(404, "No spot found for this category")

    spot = spot_result.data[0]
    spot_id = spot["id"]

    result = supabase.table("comments").insert({
        "spot_id": spot_id,
        "user_id": user_id,
        "username": username,
        "comment": text  
    }).execute()

    return result.data[0]


@router.get("/comments/by_category")
def get_comments_by_category(category: str):
    spot_result = supabase.table("spots").select("*").ilike("category", category).execute()
    if not spot_result.data:
        raise HTTPException(404, "No spot found for this category")

    spot = spot_result.data[0]
    spot_id = spot["id"]

    result = (
        supabase.table("comments")
        .select("*")
        .eq("spot_id", spot_id)
        .order("created_at")
        .execute()
    )

    return result.data
