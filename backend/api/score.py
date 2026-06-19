"""Scoring API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union, List

from core.logger import logger


def _to_hex(color) -> str:
    """Convert get_valid_color result to CSS hex. Handles both hex strings and RGB lists/tuples."""
    if isinstance(color, str):
        return color
    if isinstance(color, (list, tuple)) and len(color) >= 3:
        return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
    return "#ffffff"

router = APIRouter()


class ScorePhantomRequest(BaseModel):
    role_id: str
    props: list  # List of {attributeName, attributeValue}
    cost: int  # Echo cost (1, 3, 4)


class ScoreCalcRequest(BaseModel):
    uid: str
    token: str
    char_id: str
    role_data: dict  # Full roleDetailData from API


class ScoreResponse(BaseModel):
    success: bool
    msg: str = ""
    data: Optional[dict] = None


@router.post("/echo", response_model=ScoreResponse)
async def score_echo(req: ScorePhantomRequest):
    """Score a single echo/phantom (generic algorithm)."""
    try:
        from core.calculate import calc_phantom_score
        # Build a minimal calc_temp using defaults
        # In the real flow, get_calc_map() computes this from character data
        calc_temp = {
            "name": "默认模板",
            "main_props": {"4": {}, "3": {}, "1": {}},
            "sub_props": {},
            "skill_weight": [0.25, 0.1, 0.3, 0.25, 0.05, 0.05],
            "total_grade": "s",
        }

        score, grade = calc_phantom_score(req.role_id, req.props, req.cost, calc_temp)

        return ScoreResponse(
            success=True,
            data={
                "score": round(score, 2),
                "grade": grade,
                "max_score": 50,
            },
        )
    except Exception as e:
        logger.exception(f"Echo scoring failed: {e}")
        return ScoreResponse(success=False, msg=str(e))


@router.post("/character", response_model=ScoreResponse)
async def score_character(req: ScoreCalcRequest):
    """Calculate character composite score using the full scoring engine."""
    try:
        from core.calc import WuWaCalc
        from core.calculate import get_calc_map, get_total_score_bg, calc_phantom_score, calc_phantom_entry, get_valid_color
        from core.map.damage.register import register_score

        # Ensure scoring modules are loaded
        register_score()

        from core.api.model.role import RoleDetailData
        role_detail = RoleDetailData.model_validate(req.role_data)

        calc = WuWaCalc(role_detail)

        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            calc.phantom_pre = calc.prepare_phantom()
            calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
            calc.calc_temp = get_calc_map(
                calc.phantom_card,
                role_detail.role.roleName,
                role_detail.role.roleId,
                "",
            )

            # Score each echo
            phantom_scores = []
            substat_scores = []
            total_phantom_score = 0
            attr_name = role_detail.role.attributeName or ""
            for phantom in role_detail.phantomData.equipPhantomList:
                if phantom and phantom.phantomProp:
                    props = phantom.get_props()
                    score, grade = calc_phantom_score(
                        role_detail.role.roleId,
                        props,
                        phantom.cost,
                        calc.calc_temp,
                    )
                    score = min(score, 50.0)
                    total_phantom_score += score
                    phantom_scores.append({
                        "phantom_id": phantom.phantomProp.phantomId,
                        "cost": phantom.cost,
                        "score": round(score, 2),
                        "grade": grade,
                    })
                    # Per-substat individual scores + colors from compiled .pyd
                    ph_sub_scores = []
                    for prop_idx, prop in enumerate(props):
                        prop_name = prop.attributeName if hasattr(prop, "attributeName") else ""
                        prop_val = prop.attributeValue if hasattr(prop, "attributeValue") else ""
                        if prop_idx > 1:
                            try:
                                _, final_score = calc_phantom_entry(
                                    prop_idx, prop, phantom.cost, calc.calc_temp, attr_name
                                )
                            except Exception:
                                final_score = 0
                            # Call the original .pyd for real name/num colors
                            try:
                                name_color, num_color = get_valid_color(prop_name, prop_val, calc.calc_temp)
                                name_color = _to_hex(name_color)
                                num_color = _to_hex(num_color)
                            except Exception as e:
                                logger.warning(f"[WuwaWeb] get_valid_color failed for {prop_name}={prop_val}: {e}")
                                name_color, num_color = "#ffffff", "#ffffff"
                        else:
                            final_score = 0
                            name_color, num_color = "#ffffff", "#ffffff"
                        ph_sub_scores.append({
                            "attr_name": prop_name,
                            "attr_value": prop_val,
                            "score": final_score,
                            "name_color": name_color,
                            "num_color": num_color,
                        })
                    substat_scores.append(ph_sub_scores)

            total_grade = get_total_score_bg(
                role_detail.role.roleName,
                total_phantom_score,
                calc.calc_temp,
            )

            # Extract weight maps for frontend color coding
            sub_weights = calc.calc_temp.get("sub_props", {}) if isinstance(calc.calc_temp, dict) else {}
            main_weights = calc.calc_temp.get("main_props", {}) if isinstance(calc.calc_temp, dict) else {}

            return ScoreResponse(
                success=True,
                data={
                    "total_score": round(total_phantom_score, 2),
                    "max_score": 250,
                    "grade": total_grade,
                    "phantoms": phantom_scores,
                    "sub_weights": sub_weights,
                    "main_weights": main_weights,
                    "substat_scores": substat_scores,
                },
            )
        else:
            return ScoreResponse(
                success=True,
                data={
                    "total_score": 0,
                    "max_score": 250,
                    "grade": "c",
                    "phantoms": [],
                    "sub_weights": {},
                    "main_weights": {},
                    "substat_scores": [],
                },
            )
    except Exception as e:
        logger.exception(f"Character scoring failed: {e}")
        return ScoreResponse(success=False, msg=str(e))


class BatchScoreRequest(BaseModel):
    uid: str
    token: str
    did: str = ""
    bat: str = ""
    char_ids: list[str]  # List of character IDs to score


@router.post("/batch", response_model=ScoreResponse)
async def score_batch(req: BatchScoreRequest):
    """Score all characters in one batch. Returns {charId: {total_score, grade}} — minimal, just for listing."""
    from core.api.model.role import RoleDetailData
    from core.waves_api_wrapper import call_role_detail
    from core.calculate import calc_phantom_score, get_calc_map, get_total_score_bg
    from core.calc import WuWaCalc
    from core.map.damage.register import register_score

    register_score()

    results = {}
    for char_id in req.char_ids:
        try:
            detail_resp = await call_role_detail(req.uid, req.token, char_id, req.did, req.bat)
            if not detail_resp.success or not detail_resp.data:
                results[char_id] = {"total_score": 0, "grade": "c"}
                continue

            role_detail = RoleDetailData.model_validate(detail_resp.data)
            if not role_detail.phantomData or not role_detail.phantomData.equipPhantomList:
                results[char_id] = {"total_score": 0, "grade": "c"}
                continue

            calc = WuWaCalc(role_detail)
            calc.phantom_pre = calc.prepare_phantom()
            calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
            calc.calc_temp = get_calc_map(calc.phantom_card, role_detail.role.roleName, role_detail.role.roleId, "")

            total = 0
            for ph in role_detail.phantomData.equipPhantomList:
                if ph and ph.phantomProp:
                    props = ph.get_props()
                    score, _ = calc_phantom_score(role_detail.role.roleId, props, ph.cost, calc.calc_temp)
                    total += min(score, 50.0)

            grade = get_total_score_bg(role_detail.role.roleName, total, calc.calc_temp)
            results[char_id] = {"total_score": round(total, 2), "grade": grade}
        except Exception as e:
            logger.error(f"Batch score failed for {char_id}: {e}")
            results[char_id] = {"total_score": 0, "grade": "c"}

    return ScoreResponse(success=True, data=results)
