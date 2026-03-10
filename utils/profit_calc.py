"""
Profit calculation engine for crop recommendations.
"""


def calculate_profit(crops, price_data, acres=1):
    """
    Calculate revenue, cost, and profit for a list of recommended crops.
    
    Args:
        crops: list of crop dicts from prediction.recommend_crops()
        price_data: dict mapping crop name to price per kg
        acres: land area in acres (default 1)
    
    Returns:
        list of dicts with profit analysis for each crop
    """
    results = []
    for crop in crops:
        crop_name = crop["crop"]
        yield_per_acre = crop.get("yield_per_acre", 0)
        cost_per_acre = crop.get("cost_per_acre", 0)
        price_per_kg = price_data.get(crop_name, 0)

        total_yield = yield_per_acre * acres
        revenue = total_yield * price_per_kg
        total_cost = cost_per_acre * acres
        profit = revenue - total_cost
        roi_percent = round((profit / total_cost * 100), 1) if total_cost > 0 else 0

        results.append({
            "crop": crop_name,
            "yield_kg": total_yield,
            "price_per_kg": price_per_kg,
            "revenue": revenue,
            "cost": total_cost,
            "profit": profit,
            "roi_percent": roi_percent,
            "season": crop.get("season", "N/A"),
            "suitability_score": crop.get("suitability_score", 0)
        })

    # Sort by profit descending
    results.sort(key=lambda x: x["profit"], reverse=True)
    return results


def format_currency(amount):
    """Format number as Indian currency string."""
    if amount >= 100000:
        return f"₹{amount/100000:.2f} L"
    elif amount >= 1000:
        return f"₹{amount/1000:.1f}K"
    else:
        return f"₹{amount:.0f}"


def get_best_crop(profit_data):
    """Return the most profitable crop from profit analysis."""
    if not profit_data:
        return None
    return max(profit_data, key=lambda x: x["profit"])
