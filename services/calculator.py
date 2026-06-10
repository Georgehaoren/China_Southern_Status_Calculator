from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from .rules import load_rules, tier_label, partner_label, get_partner_status, is_current_accrual_partner


def ceil_non_negative(value: float) -> int:
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    return max(0, math.ceil(value))


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_cabin(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()[:1]


def normalize_carrier(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()



def service_class_label(value: Any) -> str:
    """Return a bilingual, user-facing service class label.

    Internal rule files keep a stable English enum so CSV/JSON remain easy to
    maintain. UI/export surfaces this bilingual label for clarity.
    """
    key = str(value or "").strip().lower()
    labels = {
        "first": "头等舱 / First Class",
        "business": "公务舱 / Business Class",
        "premium_economy": "超级经济舱 / Premium Economy",
        "economy": "经济舱 / Economy Class",
        "unknown": "未列明 / Not Listed",
    }
    if not key:
        return ""
    return labels.get(key, str(value))


def normalize_airport(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()[:3]


def normalize_mileage_source(value: Any) -> str:
    allowed = {
        "manual_official_tool",
        "manual_actual_posting",
        "cz_skypearl_calculator",
        "airline_own_calculator",
        "airport_distance_estimate",
        "unknown",
    }
    source = str(value or "").strip().lower()
    return source if source in allowed else "unknown"



def normalize_cost_input_mode(value: Any) -> str:
    allowed = {
        "per_unit",
        "row_total",
        "order_total_even",
        "order_total_by_standard_miles",
    }
    mode = str(value or "per_unit").strip().lower()
    return mode if mode in allowed else "per_unit"


def cost_input_mode_label(value: Any) -> str:
    labels = {
        "per_unit": "每段/每次成本",
        "row_total": "本行总成本",
        "order_total_even": "整单总价：按段数均分",
        "order_total_by_standard_miles": "整单总价：按标准里程分摊",
    }
    mode = normalize_cost_input_mode(value)
    return labels.get(mode, mode)

def lookup_mileage_tool(rules: Dict[str, Any], *carrier_candidates: str) -> Dict[str, Any]:
    tools = rules.get("mileage_tools", {}).get("tools", [])
    by_code = {str(t.get("code", "")).upper(): t for t in tools}
    for code in carrier_candidates:
        code = normalize_carrier(code)
        if code in by_code:
            return by_code[code]
    return by_code.get("CZ", tools[0] if tools else {})


def normalize_retention_year(value: Any) -> str:
    """Normalize assessment scenario / consecutive retention year.

    Returns:
    - "" for not selected
    - "upgrade" for upgrade / new qualification, with no retention discount
    - "1", "2", "3" for first / second / third-or-more consecutive retention year
    """
    if value is None:
        return ""
    text = str(value).strip().lower()
    if text in {"", "none", "null"}:
        return ""
    if text in {"upgrade", "new", "standard", "no_discount"}:
        return "upgrade"
    try:
        year = int(float(text))
    except Exception:
        return ""
    if year <= 1:
        return "1"
    if year == 2:
        return "2"
    return "3"


def has_positive_number(value: Any) -> bool:
    """Return True only when the user supplied a positive numeric value.

    This intentionally treats blank / 0 / invalid values as missing. It prevents
    auto mode from falling back to mileage-based calculations before the required
    cash amount or standard mileage has been entered.
    """
    return to_float(value, 0.0) > 0


def target_thresholds(rules: Dict[str, Any], current_tier: str, target_tier: str, retention_year: Any) -> Dict[str, Any]:
    tiers = rules["tiers"]
    current_tier = str(current_tier or "").upper()
    target_tier = str(target_tier or "").upper()
    scenario = normalize_retention_year(retention_year)

    if not target_tier or target_tier not in tiers:
        return {
            "target_tier": target_tier,
            "target_name": "请选择目标级别",
            "base_required_miles": 0,
            "base_required_segments": 0,
            "discount": 1.0,
            "required_miles": 0,
            "required_segments": 0,
            "mode": "target_not_selected",
            "assessment_scenario": scenario,
            "note": "未选择目标级别，暂不判断升级或保级缺口。",
        }

    current = tiers.get(current_tier, tiers["BASE"])
    target = tiers[target_tier]
    base_miles = target["qualifying_miles"]
    base_segments = target["qualifying_segments"]
    discount = 1.0
    mode = "upgrade"
    note = "升级 / 新定级或非折扣场景按原始标准测算，不使用保级折扣。"

    if scenario in {"1", "2", "3"}:
        if current["rank"] >= 1 and target["rank"] >= 1 and target["rank"] <= current["rank"]:
            discount = float(rules["retention_discounts"].get(current_tier, {}).get(scenario, 1.0))
            mode = "retention_discount"
            note = "保级折扣仅用于保至当前或以下精英级别；冲更高级别按原始标准。"
        else:
            mode = "retention_selected_but_not_applicable"
            note = "已选择保级年限，但目标级别高于当前级别或当前级别不是精英会员；因此按升级 / 原始标准测算。"
    elif scenario == "upgrade":
        mode = "upgrade"
    else:
        mode = "scenario_not_selected"
        note = "未选择评定场景；暂按原始标准测算，不使用保级折扣。"

    return {
        "target_tier": target_tier,
        "target_name": target.get("name_cn", target_tier),
        "base_required_miles": base_miles,
        "base_required_segments": base_segments,
        "discount": discount,
        "required_miles": ceil_non_negative(base_miles * discount),
        "required_segments": round(base_segments * discount, 2),
        "mode": mode,
        "assessment_scenario": scenario,
        "note": note,
    }


def partner_codes(rules: Dict[str, Any]) -> set[str]:
    codes = set(rules.get("partner_accrual", {}).get("partners", {}).keys())
    for code, partner in rules.get("partner_accrual", {}).get("partners", {}).items():
        for alias in partner.get("also_codes", []):
            codes.add(str(alias).upper())
    return codes


def resolve_partner_code(rules: Dict[str, Any], carrier: str) -> Optional[str]:
    carrier = normalize_carrier(carrier)
    partners = rules.get("partner_accrual", {}).get("partners", {})
    if carrier in partners:
        return carrier
    for code, partner in partners.items():
        if carrier in {str(alias).upper() for alias in partner.get("also_codes", [])}:
            return code
    return None


def lookup_partner_rule(rules: Dict[str, Any], carrier: str, cabin: str) -> Optional[Dict[str, Any]]:
    code = resolve_partner_code(rules, carrier)
    if not code:
        return None
    partner = rules.get("partner_accrual", {}).get("partners", {}).get(code, {})
    for rule in partner.get("rules", []):
        if cabin in [str(c).upper() for c in rule.get("cabins", [])]:
            return {**rule, "partner_code": code, "partner": partner}
    return {"partner_code": code, "partner": partner, "mileage_rate": 0.0, "segment_credit": 0.0, "service_class": "unknown", "cabins": []}




def resolve_codeshare_784_code(rules: Dict[str, Any], carrier: str) -> Optional[str]:
    carrier = normalize_carrier(carrier)
    carriers = rules.get("codeshare_784_accrual", {}).get("carriers", {})
    if carrier in carriers:
        return carrier
    return None


def lookup_codeshare_784_rule(rules: Dict[str, Any], carrier: str, cabin: str) -> Optional[Dict[str, Any]]:
    code = resolve_codeshare_784_code(rules, carrier)
    if not code:
        return None
    carrier_info = rules.get("codeshare_784_accrual", {}).get("carriers", {}).get(code, {})
    for rule in carrier_info.get("rules", []):
        if cabin in [str(c).upper() for c in rule.get("cabins", [])]:
            return {**rule, "carrier_code": code, "carrier": carrier_info, "rule_source": rule.get("rule_source", "codeshare_784_json")}
    return {"carrier_code": code, "carrier": carrier_info, "mileage_rate": 0.0, "service_class": "unknown", "cabins": [], "rule_source": "not_listed"}

def determine_earning_mode(row: Dict[str, Any], rules: Dict[str, Any]) -> str:
    selected = str(row.get("earning_mode", "auto")).strip().lower()
    if selected == "":
        return "none"
    if selected in {"cash", "standard", "partner", "codeshare_784", "manual", "none", "ancillary"}:
        return selected

    product_type = str(row.get("product_type", "ticket")).lower()
    if product_type in {"upgrade", "ancillary"}:
        return "ancillary"
    if product_type == "manual":
        return "manual"

    marketing = normalize_carrier(row.get("marketing_carrier"))
    operating = normalize_carrier(row.get("operating_carrier"))
    ticket_prefix = str(row.get("ticket_prefix", "")).strip()

    # 784-ticket CZ/OQ flights are amount-based only when the operating carrier is CZ/OQ
    # or still blank. If CZ/OQ-marketed 784 ticket is operated by a non-CZ/OQ carrier,
    # use the dedicated code-share mode: miles follow non-CZ operating-carrier rules,
    # while qualifying segments follow the CZ-ticketed booking class.
    if marketing in rules["eligible_marketing_carriers"] and ticket_prefix.startswith(rules["cash_ticket_prefix"]):
        if operating and operating not in rules["eligible_operating_carriers"]:
            return "codeshare_784"
        return "cash"
    if resolve_partner_code(rules, marketing) or resolve_partner_code(rules, operating):
        return "partner"
    return "standard"



def prepare_cost_allocation(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize cash/cost inputs before row-level mileage calculation.

    Existing versions treated cash_amount as a per-segment/per-product amount.
    v22 adds cost_input_mode:
    - per_unit: cash_amount is already per segment/product.
    - row_total: cash_amount is total for this row; divide by count.
    - order_total_even: rows with the same cost_group share one order total evenly by count.
    - order_total_by_standard_miles: rows with the same cost_group share one order total by standard_miles * count.

    For grouped order modes, the order total is the maximum positive cash_amount entered
    within the group. This lets the user paste the same full order price on several rows
    without multiplying the total by the number of rows.
    """
    prepared: List[Dict[str, Any]] = []
    groups: Dict[str, List[int]] = {}

    for idx, row in enumerate(rows):
        item = dict(row)
        mode = normalize_cost_input_mode(item.get("cost_input_mode"))
        item["cost_input_mode"] = mode
        item["cost_group"] = str(item.get("cost_group", "") or "").strip()
        item["_entered_cash_amount"] = to_float(item.get("cash_amount"), 0)
        count = max(0, to_int(item.get("count"), 0))
        item["_count_for_cost"] = count
        item["_cost_allocation_note"] = ""

        if mode == "per_unit":
            item["_effective_cash_amount_per_unit"] = item["_entered_cash_amount"]
            item["_allocated_total_cost"] = item["_entered_cash_amount"] * count
            item["_cost_allocation_note"] = "按每段/每次金额计算。"
        elif mode == "row_total":
            per_unit = item["_entered_cash_amount"] / count if count else 0
            item["_effective_cash_amount_per_unit"] = per_unit
            item["_allocated_total_cost"] = item["_entered_cash_amount"] if count else 0
            item["_cost_allocation_note"] = "本行现金金额按本行总成本处理，并除以次数/段数。"
        else:
            group = item["cost_group"] or f"__row_{idx}"
            item["_cost_group_key"] = group
            groups.setdefault(group, []).append(idx)
            item["_effective_cash_amount_per_unit"] = 0
            item["_allocated_total_cost"] = 0
        prepared.append(item)

    for group, indexes in groups.items():
        group_rows = [prepared[i] for i in indexes]
        totals = [r["_entered_cash_amount"] for r in group_rows if r["_entered_cash_amount"] > 0]
        order_total = max(totals) if totals else 0
        inconsistent = len({round(v, 2) for v in totals}) > 1
        mode = group_rows[0].get("cost_input_mode", "order_total_even")

        if mode == "order_total_by_standard_miles":
            weights = []
            for r in group_rows:
                count = r.get("_count_for_cost", 0)
                miles = max(0.0, to_float(r.get("standard_miles"), 0))
                weights.append(miles * count)
            if sum(weights) <= 0:
                weights = [r.get("_count_for_cost", 0) for r in group_rows]
                basis_note = "未填写可用于分摊的标准里程，已回退按段数均分。"
            else:
                basis_note = "按标准里程×次数/段数分摊整单总价。"
        else:
            weights = [r.get("_count_for_cost", 0) for r in group_rows]
            basis_note = "按次数/段数均分整单总价。"

        total_weight = sum(weights)
        for r, weight in zip(group_rows, weights):
            count = r.get("_count_for_cost", 0)
            allocated_total = order_total * (weight / total_weight) if total_weight > 0 else 0
            per_unit = allocated_total / count if count else 0
            r["_effective_cash_amount_per_unit"] = per_unit
            r["_allocated_total_cost"] = allocated_total
            notes = [basis_note]
            if not r.get("cost_group"):
                notes.append("未填写成本分摊组，已仅按本行处理。")
            if inconsistent:
                notes.append("同一成本分摊组内填写了多个不同总价；本工具使用最大值作为整单总价，请核对。")
            r["_cost_allocation_note"] = " ".join(notes)

    return prepared

def calculate_row(row: Dict[str, Any], rules: Dict[str, Any], member_tier: str) -> Dict[str, Any]:
    count = max(0, to_int(row.get("count"), 0))
    cabin = normalize_cabin(row.get("booking_class"))
    marketing = normalize_carrier(row.get("marketing_carrier", ""))
    operating = normalize_carrier(row.get("operating_carrier", ""))
    origin_airport = normalize_airport(row.get("origin_airport", ""))
    destination_airport = normalize_airport(row.get("destination_airport", ""))
    flight_number = str(row.get("flight_number", "") or "").strip().upper()
    standard_miles_source = normalize_mileage_source(row.get("standard_miles_source", "unknown"))
    standard_miles_note = str(row.get("standard_miles_note", "") or "").strip()
    mileage_tool_code = normalize_carrier(row.get("mileage_tool_code", ""))
    product_type = str(row.get("product_type", "ticket")).lower()
    mode = determine_earning_mode(row, rules)
    minimum_miles = rules.get("minimum_standard_miles", 500)
    partner_min = rules.get("partner_accrual", {}).get("minimum_standard_miles", minimum_miles)
    raw_standard_miles = to_float(row.get("standard_miles"), 0)
    standard_miles = max(minimum_miles, raw_standard_miles) if raw_standard_miles > 0 else 0
    partner_standard_miles = max(partner_min, raw_standard_miles) if raw_standard_miles > 0 else 0
    entered_cash_amount = to_float(row.get("_entered_cash_amount", row.get("cash_amount")), 0)
    cash_amount = to_float(row.get("_effective_cash_amount_per_unit", row.get("cash_amount")), 0)
    allocated_total_cost = to_float(row.get("_allocated_total_cost"), cash_amount * count)
    cost_input_mode = normalize_cost_input_mode(row.get("cost_input_mode"))
    cost_group = str(row.get("cost_group", "") or "").strip()
    cost_allocation_note = str(row.get("_cost_allocation_note", "") or "").strip()
    manual_qm = to_float(row.get("manual_qualifying_miles"), 0)
    manual_qs = to_float(row.get("manual_qualifying_segments"), 0)
    manual_award = to_float(row.get("manual_award_miles"), 0)
    notes: List[str] = []
    if cost_allocation_note:
        notes.append(f"成本口径：{cost_input_mode_label(cost_input_mode)}。{cost_allocation_note}")

    member_coef = float(rules["tiers"].get(member_tier, rules["tiers"]["BASE"])["reward_coefficient"])
    ticket_coef = float(row.get("category_coefficient") or rules["category_coefficients"].get("ticket", 0.8))
    ancillary_coef = float(row.get("category_coefficient") or rules["category_coefficients"].get("ancillary", 0.5))
    cabin_rate = float(rules["cz_cabin_mileage_accrual"].get(cabin, 0.0))
    segment_credit = float(rules["cz_cabin_segment_credit"].get(cabin, 0.0))
    service_class = ""
    partner_code = ""
    carrier_label = ""
    mileage_tool = lookup_mileage_tool(rules, mileage_tool_code, operating, marketing, "CZ")
    official_tool_url = mileage_tool.get("tool_url", "")
    official_tool_name = mileage_tool.get("name_cn", mileage_tool.get("program", ""))

    if cabin == "R" and mode == "cash":
        notes.append("R舱/产品舱在手册中特别提示不参与现金消费金额累积；如为特殊产品请以实际产品规则为准。")

    q_miles_per = 0
    award_miles_per = 0
    q_segments_per = 0.0
    cost_per = cash_amount
    ineligible = False
    incomplete = False

    if mode == "cash" and cash_amount <= 0:
        incomplete = True
        notes.append("784票号现金消费金额模式需要填写现金消费额/成本；未填写前不计算定级里程或定级航段。")
    elif mode in {"standard", "partner", "codeshare_784"} and raw_standard_miles <= 0:
        incomplete = True
        notes.append("标准里程/合作伙伴/784代码共享模式需要填写标准里程；未填写前不计算定级里程或定级航段。")
    elif mode in {"standard", "partner", "codeshare_784"} and not cabin:
        incomplete = True
        notes.append("标准里程/合作伙伴/784代码共享模式需要填写舱位；未填写前不计算定级里程或定级航段。")
    elif mode == "codeshare_784" and not operating:
        incomplete = True
        notes.append("784代码共享/非南航承运模式需要填写实际承运方。")
    elif mode == "ancillary" and cash_amount <= 0:
        incomplete = True
        notes.append("辅助产品模式需要填写现金消费额/成本；未填写前不计算里程。")

    if raw_standard_miles <= 0 and (origin_airport or destination_airport) and mode in {"standard", "partner", "codeshare_784"}:
        notes.append("已填写始发/到达机场但未填写标准里程；建议先使用官方里程查询工具查到标准里程后手动填入。")
    if raw_standard_miles > 0 and standard_miles_source == "unknown":
        notes.append("已填写标准里程，但未标注来源；建议选择“航空公司工具/实际入账/机场距离估算”等来源，便于后续数据分析。")
    if standard_miles_source == "airport_distance_estimate":
        notes.append("标准里程来源为机场距离估算，可能不同于南航/IATA/航司实际入账口径。")

    if incomplete:
        ineligible = True
        notes.append("该行信息尚未完整，已暂不纳入汇总。")
    elif mode == "none":
        ineligible = True
        notes.append("已手动标记为不累积。")
    elif mode == "manual":
        q_miles_per = ceil_non_negative(manual_qm)
        award_miles_per = ceil_non_negative(manual_award)
        q_segments_per = manual_qs
        notes.append("使用手动累积值，适合合作伙伴、活动或特殊票价。")
    elif mode == "ancillary":
        q_miles_per = ceil_non_negative(cash_amount * ancillary_coef)
        award_miles_per = ceil_non_negative(cash_amount * ancillary_coef * member_coef)
        q_segments_per = 0.0
        notes.append("升舱/国际付费选座/行李等辅助产品只计定级里程和奖励里程，不计定级航段。")
    elif mode == "cash":
        if marketing not in rules["eligible_marketing_carriers"]:
            notes.append("现金消费金额模式通常要求市场方为 CZ/OQ，请核对票面与实际入账。")
        q_miles_per = ceil_non_negative(cash_amount * ticket_coef)
        award_miles_per = ceil_non_negative(cash_amount * ticket_coef * member_coef)
        q_segments_per = segment_credit
    elif mode == "codeshare_784":
        if marketing not in rules["eligible_marketing_carriers"] or not str(row.get("ticket_prefix", "")).strip().startswith(rules["cash_ticket_prefix"]):
            notes.append("784代码共享模式通常用于 CZ/OQ 市场方且票号前缀为 784 的非南航实际承运航班。")
        if operating in rules["eligible_operating_carriers"]:
            notes.append("实际承运方为 CZ/OQ 时通常应使用 784现金消费模式；请核对是否选错模式。")

        codeshare_rule = lookup_codeshare_784_rule(rules, operating, cabin)
        rule_source = "codeshare_784"
        if not codeshare_rule:
            partner_rule = lookup_partner_rule(rules, operating, cabin)
            if partner_rule:
                codeshare_rule = {
                    "carrier_code": partner_rule.get("partner_code", operating),
                    "carrier": partner_rule.get("partner", {}),
                    "mileage_rate": partner_rule.get("mileage_rate", 0.0),
                    "service_class": partner_rule.get("service_class", ""),
                    "rule_source": "fallback_partner_accrual_table",
                }
                rule_source = "fallback_partner_accrual_table"

        q_segments_per = segment_credit
        if not codeshare_rule:
            ineligible = True
            notes.append("未在 784代码共享规则库或合作伙伴规则库中找到该实际承运方/舱位；请补充 JSON/CSV 或改用手动模式。")
        else:
            partner_code = codeshare_rule.get("carrier_code", operating)
            carrier_info = codeshare_rule.get("carrier", {})
            carrier_label = f"{carrier_info.get('name_cn', partner_code)} / {carrier_info.get('name_en', partner_code)}"
            cabin_rate = float(codeshare_rule.get("mileage_rate", 0.0))
            service_class = str(codeshare_rule.get("service_class", ""))
            q_miles_per = ceil_non_negative(partner_standard_miles * cabin_rate)
            award_miles_per = ceil_non_negative(q_miles_per * member_coef)
            if cabin_rate <= 0:
                ineligible = True
                notes.append("该舱位在 784代码共享/非南航承运规则库中未列明或不累积。")
            notes.append(f"784代码共享/非南航承运：定级里程按 {carrier_label} {round(cabin_rate*100, 2)}% 估算；定级航段按南航票面 {cabin} 舱计算为 {q_segments_per} 段。")
            if rule_source == "fallback_partner_accrual_table":
                notes.append("本行未命中专用 784代码共享库，已回退使用合作伙伴累积表的里程比例；定级航段仍按南航票面舱位。")
    elif mode == "partner":
        chosen_carrier = operating or marketing
        partner_rule = lookup_partner_rule(rules, chosen_carrier, cabin)
        if not partner_rule and marketing and marketing != chosen_carrier:
            partner_rule = lookup_partner_rule(rules, marketing, cabin)
            chosen_carrier = marketing
        if not partner_rule:
            ineligible = True
            notes.append("未在合作伙伴规则库中找到该航司；请手动录入或更新 JSON/CSV。")
        else:
            partner_code = partner_rule.get("partner_code", "")
            carrier_label = partner_label(rules, partner_code)
            status_info = get_partner_status(rules, partner_code)
            status_note = status_info.get("status_note_cn", "")
            current_eligible = bool(status_info.get("current_accrual_eligible"))
            cabin_rate = float(partner_rule.get("mileage_rate", 0.0))
            q_segments_per = float(partner_rule.get("segment_credit", 0.0))
            service_class = str(partner_rule.get("service_class", ""))
            q_miles_per = ceil_non_negative(partner_standard_miles * cabin_rate)
            # Screenshot note: reward miles and qualifying miles are treated the same for partner table.
            award_miles_per = q_miles_per
            if not current_eligible:
                ineligible = True
                q_miles_per = 0
                award_miles_per = 0
                q_segments_per = 0.0
                notes.append(f"合作状态风险：{partner_code} 当前未标记为可自动累积南航明珠。{status_note} 已暂不纳入汇总；如有最新公告或实际入账，请改用手动模式或更新 JSON/CSV。")
            if cabin_rate <= 0:
                ineligible = True
                notes.append("该舱位在合作伙伴规则库中未列明或不累积。")
            if marketing and operating and marketing != operating:
                notes.append("合作伙伴累积通常要求市场方和实际承运人为同一家合作伙伴；代码共享需逐票核对。")
            notes.append(f"合作伙伴规则：{carrier_label}，{service_class_label(service_class) or '未列明 / Not Listed'}，累积率 {round(cabin_rate*100, 2)}%，计入定级航段 {q_segments_per}。")
            if status_info.get("ffp_status"):
                notes.append(f"当前合作状态：{status_info.get('ffp_status')}；风险等级：{status_info.get('risk_level', 'medium')}。")
    else:  # standard CZ/OQ non-784 or mileage-based
        if marketing not in rules["eligible_marketing_carriers"] and product_type == "ticket":
            notes.append("市场方不是 CZ/OQ；如为合作伙伴，请改用“合作伙伴标准里程”或自动模式。")
        q_miles_per = ceil_non_negative(standard_miles * cabin_rate)
        award_miles_per = ceil_non_negative(standard_miles * cabin_rate * member_coef)
        q_segments_per = segment_credit

    total_q_miles = q_miles_per * count
    total_award = award_miles_per * count
    total_segments = q_segments_per * count
    total_cost = allocated_total_cost
    cost_per_qmile = round(total_cost / total_q_miles, 4) if total_q_miles else None
    cost_per_qseg = round(total_cost / total_segments, 2) if total_segments else None

    return {
        "id": row.get("id", ""),
        "name": row.get("name", ""),
        "count": count,
        "product_type": product_type,
        "earning_mode": mode,
        "marketing_carrier": marketing,
        "operating_carrier": operating,
        "origin_airport": origin_airport,
        "destination_airport": destination_airport,
        "flight_number": flight_number,
        "standard_miles_source": standard_miles_source,
        "standard_miles_note": standard_miles_note,
        "cost_group": cost_group,
        "cost_input_mode": cost_input_mode,
        "cost_input_mode_label": cost_input_mode_label(cost_input_mode),
        "entered_cash_amount": round(entered_cash_amount, 2),
        "allocated_total_cost": round(allocated_total_cost, 2),
        "cost_allocation_note": cost_allocation_note,
        "mileage_tool_code": mileage_tool.get("code", mileage_tool_code),
        "official_tool_name": official_tool_name,
        "official_tool_url": official_tool_url,
        "ticket_prefix": str(row.get("ticket_prefix", "")),
        "booking_class": cabin,
        "partner_code": partner_code,
        "partner_label": carrier_label,
        "service_class": service_class,
        "service_class_display": service_class_label(service_class),
        "cash_amount_per_unit": cash_amount,
        "standard_miles_per_segment": partner_standard_miles if mode == "partner" else standard_miles,
        "category_coefficient": ancillary_coef if mode == "ancillary" else ticket_coef,
        "cabin_accrual_rate": cabin_rate,
        "segment_credit_per_segment": q_segments_per,
        "member_reward_coefficient": member_coef,
        "qualifying_miles_per_unit": q_miles_per,
        "qualifying_segments_per_unit": q_segments_per,
        "award_miles_per_unit": award_miles_per,
        "total_cost": round(total_cost, 2),
        "total_qualifying_miles": total_q_miles,
        "total_qualifying_segments": round(total_segments, 2),
        "total_award_miles": total_award,
        "cost_per_qualifying_mile": cost_per_qmile,
        "cost_per_qualifying_segment": cost_per_qseg,
        "ineligible": ineligible,
        "incomplete": incomplete,
        "notes": notes,
    }


def best_tier_by_progress(rules: Dict[str, Any], q_miles: float, q_segments: float) -> Dict[str, Any]:
    best_code = "BASE"
    for code, info in rules["tiers"].items():
        if code == "BASE":
            continue
        if q_miles >= info["qualifying_miles"] or q_segments >= info["qualifying_segments"]:
            if info["rank"] > rules["tiers"][best_code]["rank"]:
                best_code = code
    return {"tier": best_code, "name": rules["tiers"][best_code]["name_cn"]}


def calculate_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    rules = load_rules()
    raw_current_tier = str(payload.get("current_tier", "") or "").upper()
    raw_member_tier = str(payload.get("member_tier", "") or "").upper()
    raw_target_tier = str(payload.get("target_tier", "") or "").upper()
    current_tier = raw_current_tier if raw_current_tier in rules["tiers"] else "BASE"
    member_tier = raw_member_tier if raw_member_tier in rules["tiers"] else current_tier
    target_tier = raw_target_tier if raw_target_tier in rules["tiers"] else ""
    retention_year = payload.get("retention_year", "")
    current_q_miles = to_float(payload.get("current_qualifying_miles"), 0)
    current_q_segments = to_float(payload.get("current_qualifying_segments"), 0)
    carryover_miles = to_float(payload.get("carryover_miles"), 0)
    carryover_segments = to_float(payload.get("carryover_segments"), 0)

    rows = payload.get("items") or []
    prepared_rows = prepare_cost_allocation(rows)
    calculated_rows = [calculate_row(row, rules, member_tier) for row in prepared_rows]

    planned_cost = sum(row["total_cost"] for row in calculated_rows)
    planned_q_miles = sum(row["total_qualifying_miles"] for row in calculated_rows)
    planned_q_segments = sum(row["total_qualifying_segments"] for row in calculated_rows)
    planned_award = sum(row["total_award_miles"] for row in calculated_rows)

    total_q_miles = current_q_miles + carryover_miles + planned_q_miles
    total_q_segments = current_q_segments + carryover_segments + planned_q_segments

    threshold = target_thresholds(rules, current_tier, target_tier, retention_year)
    target_selected = threshold.get("mode") != "target_not_selected"
    miles_gap = max(0, threshold["required_miles"] - total_q_miles) if target_selected else 0
    seg_gap = max(0, threshold["required_segments"] - total_q_segments) if target_selected else 0
    target_met_by_miles = target_selected and total_q_miles >= threshold["required_miles"]
    target_met_by_segments = target_selected and total_q_segments >= threshold["required_segments"]

    standard_best = best_tier_by_progress(rules, total_q_miles, total_q_segments)

    return {
        "settings": {
            "current_tier": current_tier,
            "current_tier_name": tier_label(rules, current_tier),
            "member_tier": member_tier,
            "member_tier_name": tier_label(rules, member_tier),
            "target_tier": target_tier,
            "target_tier_name": tier_label(rules, target_tier) if target_tier else "请选择目标级别",
            "retention_year": normalize_retention_year(retention_year),
        },
        "target": threshold,
        "summary": {
            "current_qualifying_miles": ceil_non_negative(current_q_miles),
            "current_qualifying_segments": round(current_q_segments, 2),
            "carryover_miles": ceil_non_negative(carryover_miles),
            "carryover_segments": round(carryover_segments, 2),
            "planned_cost": round(planned_cost, 2),
            "planned_qualifying_miles": ceil_non_negative(planned_q_miles),
            "planned_qualifying_segments": round(planned_q_segments, 2),
            "planned_award_miles": ceil_non_negative(planned_award),
            "total_qualifying_miles": ceil_non_negative(total_q_miles),
            "total_qualifying_segments": round(total_q_segments, 2),
            "miles_gap_to_target": ceil_non_negative(miles_gap),
            "segments_gap_to_target": round(seg_gap, 2),
            "target_met_by_miles": target_met_by_miles,
            "target_met_by_segments": target_met_by_segments,
            "target_met": target_met_by_miles or target_met_by_segments,
            "best_standard_tier_without_retention_discount": standard_best,
            "cost_per_qualifying_mile": round(planned_cost / planned_q_miles, 4) if planned_q_miles else None,
            "cost_per_qualifying_segment": round(planned_cost / planned_q_segments, 2) if planned_q_segments else None,
        },
        "items": calculated_rows,
        "partner_library": {
            "version": rules.get("partner_accrual", {}).get("version"),
            "partners": sorted(list(rules.get("partner_accrual", {}).get("partners", {}).keys())),
        },
        "partner_status_library": {
            "version": rules.get("partner_status", {}).get("version"),
            "carrier_count": len(rules.get("partner_status", {}).get("carriers", {})),
        },
        "mileage_tools_library": {
            "version": rules.get("mileage_tools", {}).get("version"),
            "default_tool_code": rules.get("mileage_tools", {}).get("default_tool_code", "CZ"),
            "tool_count": len(rules.get("mileage_tools", {}).get("tools", [])),
        },
        "rules_version": {
            "program": rules["program"],
            "valid_from": rules["valid_from"],
            "valid_to": rules["valid_to"],
        },
        "warnings": [
            "本工具为规划测算。特殊运价、打包产品、促销产品、合作伙伴航班、R舱/产品舱及实际入账以航空公司官方规则、客票规则和账户实际入账为准。",
            "合作伙伴规则库为维护者维护的本地参考数据，已同时保存为 JSON/CSV，日后可直接替换。",
            "v11加入合作状态库：历史天合合作伙伴默认不再视为当前可累积，需以南航最新公告/页面/实际入账为准。",
            "保级折扣为2025-01-01至2027-12-31试运行口径；2028年后如政策变化需更新规则 JSON。"
        ],
    }
