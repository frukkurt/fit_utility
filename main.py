from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from fit_utils.build_user_nutrition_profile import (
    UserProfileInput,
    UserProfileResponse,
    build_user_nutrition_profile,
)
from line_utils.generate_item_order_flex import (generate_order_flex,OrderFlexRequest)

app = FastAPI(
    title="FIT UTILITY API",
    version="1.0.0",
    description="API สำหรับ FIT และ LINE",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {
        "message": "FIT UTILITY API is running",
    }

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}



@app.post(
    "/calculate-profile",
    response_model=UserProfileResponse,
    summary="Calculate nutrition profile",
)
def calculate_profile(payload: UserProfileInput) -> UserProfileResponse:
    try:
        result = build_user_nutrition_profile(payload)
        return UserProfileResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-order-flex")
def create_order_flex(payload: OrderFlexRequest):
    try:
        flex_json = generate_order_flex(
            items=[item.model_dump() for item in payload.items],
            total_items=payload.total_items,
            total_price=payload.total_price,
            transport_price=payload.transport_price,
            sum_total=payload.sum_total,
            order_id=payload.order_id,
            address=payload.address,
            store_name=payload.store_name,
            store_address=payload.store_address,
            button_url=payload.button_url,
            button_label=payload.button_label,
        )
        # return_json = json.dumps(flex_json, ensure_ascii=False)
        return flex_json         
        # return return_json   

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))