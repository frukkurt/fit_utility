from __future__ import annotations

from datetime import date
from typing import Optional, Dict, Any, Literal, List

from pydantic import BaseModel, Field, EmailStr, field_validator


GoalType = Literal[
    "weight_loss",
    "muscle_gain",
    "health",
    "competition",
    "performance",
    "aggressive_cut",
]

SexType = Literal["male", "female"]

ActivityLevelType = Literal[
    "sedentary",
    "light",
    "moderate",
    "very_active",
    "athlete",
]


class UserProfileInput(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "line_user_id": "U1234567890",
                "email": "user@example.com",
                "first_name": "Fluke",
                "last_name": "Kurt",
                "nickname": "Fluke",
                "weight_kg": 95,
                "sex": "male",
                "height_cm": 180,
                "birth_date": "2000-01-01",
                "body_fat_percent": 25,
                "know_your_bmr": None,
                "meals_per_day": 3,
                "activity_level": "moderate",
                "goal": "weight_loss",
                "concern": "แพ้อาหารทะเล",
                "favorite": "ชอบไก่",
                "tdee_override": None,
            }
        }
    }

    line_user_id: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None

    weight_kg: float = Field(..., gt=0)
    sex: SexType
    height_cm: int = Field(..., gt=0)
    birth_date: date

    body_fat_percent: Optional[float] = None
    know_your_bmr: Optional[float] = None

    meals_per_day: int = Field(default=3, gt=0)
    activity_level: ActivityLevelType = "moderate"
    goal: GoalType = "health"

    concern: Optional[str] = None
    favorite: Optional[str] = None
    tdee_override: Optional[float] = None

    @field_validator("body_fat_percent")
    @classmethod
    def validate_body_fat(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (3 <= v <= 70):
            raise ValueError("body_fat_percent should be between 3 and 70")
        return v

    @field_validator("know_your_bmr")
    @classmethod
    def validate_bmr(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("know_your_bmr must be > 0")
        return v

    @field_validator("tdee_override")
    @classmethod
    def validate_tdee(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("tdee_override must be > 0")
        return v

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("birth_date cannot be in the future")
        return v


class UserProfileResponse(BaseModel):
    line_user_id: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None

    weight_kg: float
    sex: SexType
    height_cm: int
    birth_date: date
    body_fat_percent: Optional[float] = None

    meals_per_day: int
    activity_level: ActivityLevelType
    goal: GoalType

    concern: Optional[str] = None
    favorite: Optional[str] = None

    age: int
    bmr: int
    bmr_method: str
    tdee: int
    tdee_method: str
    goal_calorie_adjustment: int
    daily_calories_intake: int

    protein_g_per_kg_range: List[float]
    fat_g_per_kg_range: List[float]
    protein_g_per_kg_selected: float
    fat_g_per_kg_selected: float

    protein_g_per_day: int
    carb_g_per_day: int
    fat_g_per_day: int
    fiber_g_per_day: int
    sodium_mg_per_day: int

    protein_kcal_per_day: int
    carb_kcal_per_day: int
    fat_kcal_per_day: int

    protein_g_per_meal: int
    carb_g_per_meal: int
    fat_g_per_meal: int
    fiber_g_per_meal: int
    sodium_mg_per_meal: int

    calories_per_meal: int
    protein_kcal_per_meal: int
    carb_kcal_per_meal: int
    fat_kcal_per_meal: int


def calculate_age(birth_date: date, today: Optional[date] = None) -> int:
    today = today or date.today()
    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def calculate_bmr_mifflin_st_jeor(
    sex: SexType,
    weight_kg: float,
    height_cm: int,
    age: int,
) -> float:
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)

    if sex == "male":
        return base + 5

    return base - 161


def calculate_bmr_katch_mcardle(
    weight_kg: float,
    body_fat_percent: float,
) -> float:
    lean_body_mass = weight_kg * (1 - body_fat_percent / 100)
    return 370 + (21.6 * lean_body_mass)


def activity_multiplier(activity_level: ActivityLevelType) -> float:
    mapping = {
        "sedentary": 1.20,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "athlete": 1.90,
    }
    return mapping[activity_level]


def recommended_goal_calorie_adjustment(goal: GoalType) -> int:
    mapping = {
        "weight_loss": -500,
        "aggressive_cut": -700,
        "muscle_gain": 250,
        "health": 0,
        "performance": 150,
        "competition": 200,
    }
    return mapping[goal]


def protein_range_g_per_kg(
    goal: GoalType,
    activity_level: ActivityLevelType,
) -> tuple[float, float]:
    if goal == "aggressive_cut":
        return (2.2, 2.6)

    if goal == "competition":
        return (2.2, 3.0)

    if goal == "weight_loss":
        return (2.0, 2.4)

    if goal in {"muscle_gain", "performance"}:
        return (1.6, 2.2)

    if activity_level == "sedentary":
        return (0.8, 1.0)

    if activity_level == "light":
        return (1.2, 1.6)

    return (1.2, 1.8)


def fat_range_g_per_kg(
    goal: GoalType,
    activity_level: ActivityLevelType,
) -> tuple[float, float]:
    if goal == "aggressive_cut":
        return (0.5, 0.6)

    if goal in {"weight_loss", "muscle_gain", "competition"}:
        return (0.6, 0.8)

    if goal == "performance":
        return (0.6, 0.9)

    if activity_level == "sedentary":
        return (0.8, 1.0)

    return (0.6, 0.8)


def choose_midpoint(low: float, high: float) -> float:
    return (low + high) / 2


def estimate_fiber_g_per_day(target_calories: float, sex: SexType) -> int:
    base = round((target_calories / 1000) * 14)
    floor = 30 if sex == "male" else 25
    return max(base, floor)


def estimate_sodium_mg_per_day(
    goal: GoalType,
    activity_level: ActivityLevelType,
) -> int:
    if goal in {"competition", "performance"}:
        return 2300

    if activity_level in {"very_active", "athlete"}:
        return 2300

    return 2000


def build_user_nutrition_profile(profile: UserProfileInput) -> Dict[str, Any]:
    age = calculate_age(profile.birth_date)

    if profile.know_your_bmr is not None:
        bmr = float(profile.know_your_bmr)
        bmr_method = "user_override"

    elif profile.body_fat_percent is not None:
        bmr = calculate_bmr_katch_mcardle(
            weight_kg=profile.weight_kg,
            body_fat_percent=profile.body_fat_percent,
        )
        bmr_method = "katch_mcardle"

    else:
        bmr = calculate_bmr_mifflin_st_jeor(
            sex=profile.sex,
            weight_kg=profile.weight_kg,
            height_cm=profile.height_cm,
            age=age,
        )
        bmr_method = "mifflin_st_jeor"

    if profile.tdee_override is not None:
        tdee = float(profile.tdee_override)
        tdee_method = "user_override"
    else:
        tdee = bmr * activity_multiplier(profile.activity_level)
        tdee_method = "bmr_x_activity_multiplier"

    calorie_adjustment = recommended_goal_calorie_adjustment(profile.goal)
    target_calories = tdee + calorie_adjustment

    if profile.sex == "male":
        target_calories = max(target_calories, 1200)
    else:
        target_calories = max(target_calories, 1000)

    p_low, p_high = protein_range_g_per_kg(
        goal=profile.goal,
        activity_level=profile.activity_level,
    )

    f_low, f_high = fat_range_g_per_kg(
        goal=profile.goal,
        activity_level=profile.activity_level,
    )

    protein_g_per_kg = choose_midpoint(p_low, p_high)
    fat_g_per_kg = choose_midpoint(f_low, f_high)

    protein_g_day = round(profile.weight_kg * protein_g_per_kg)
    fat_g_day = round(profile.weight_kg * fat_g_per_kg)

    protein_kcal_day = protein_g_day * 4
    fat_kcal_day = fat_g_day * 9

    remaining_kcal = target_calories - protein_kcal_day - fat_kcal_day
    carb_g_day = max(round(remaining_kcal / 4), 0)
    carb_kcal_day = carb_g_day * 4

    fiber_g_day = estimate_fiber_g_per_day(
        target_calories=target_calories,
        sex=profile.sex,
    )

    sodium_mg_day = estimate_sodium_mg_per_day(
        goal=profile.goal,
        activity_level=profile.activity_level,
    )

    meals = profile.meals_per_day

    protein_g_per_meal = round(protein_g_day / meals)
    carb_g_per_meal = round(carb_g_day / meals)
    fat_g_per_meal = round(fat_g_day / meals)
    fiber_g_per_meal = round(fiber_g_day / meals)
    sodium_mg_per_meal = round(sodium_mg_day / meals)

    return {
        "line_user_id": profile.line_user_id,
        "email": profile.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "nickname": profile.nickname,

        "weight_kg": profile.weight_kg,
        "sex": profile.sex,
        "height_cm": profile.height_cm,
        "birth_date": profile.birth_date,
        "body_fat_percent": profile.body_fat_percent,

        "meals_per_day": profile.meals_per_day,
        "activity_level": profile.activity_level,
        "goal": profile.goal,

        "concern": profile.concern,
        "favorite": profile.favorite,

        "age": age,
        "bmr": round(bmr),
        "bmr_method": bmr_method,
        "tdee": round(tdee),
        "tdee_method": tdee_method,
        "goal_calorie_adjustment": calorie_adjustment,
        "daily_calories_intake": round(target_calories),

        "protein_g_per_kg_range": [p_low, p_high],
        "fat_g_per_kg_range": [f_low, f_high],
        "protein_g_per_kg_selected": protein_g_per_kg,
        "fat_g_per_kg_selected": fat_g_per_kg,

        "protein_g_per_day": protein_g_day,
        "carb_g_per_day": carb_g_day,
        "fat_g_per_day": fat_g_day,
        "fiber_g_per_day": fiber_g_day,
        "sodium_mg_per_day": sodium_mg_day,

        "protein_kcal_per_day": protein_kcal_day,
        "carb_kcal_per_day": carb_kcal_day,
        "fat_kcal_per_day": fat_kcal_day,

        "protein_g_per_meal": protein_g_per_meal,
        "carb_g_per_meal": carb_g_per_meal,
        "fat_g_per_meal": fat_g_per_meal,
        "fiber_g_per_meal": fiber_g_per_meal,
        "sodium_mg_per_meal": sodium_mg_per_meal,

        "calories_per_meal": round(target_calories / meals),
        "protein_kcal_per_meal": protein_g_per_meal * 4,
        "carb_kcal_per_meal": carb_g_per_meal * 4,
        "fat_kcal_per_meal": fat_g_per_meal * 9,
    }
