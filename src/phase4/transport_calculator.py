"""
src/phase4/transport_calculator.py

Transport Freight & Net Profit Engine for Krishi Market Advisor.
Calculates distance between Karnataka farmer location and APMC mandis,
estimates freight transport costs, and computes net extra profit.
"""

from typing import Dict, Any, Optional

# Representative road distance matrix between key Karnataka districts and major APMCs (in KM)
DISTANCES_KM: Dict[str, Dict[str, float]] = {
    "Shivamogga (Shimoga)": {
        "APMC THIRTHAHALLI": 60,
        "Shikaripura APMC": 55,
        "Sagara APMC": 72,
        "Hosanagara APMC": 65,
        "Shimoga APMC": 10,
        "Sirsi APMC": 135,
        "Channagiri APMC": 45,
    },
    "Chikmagalur (Chikkamagaluru)": {
        "APMC THIRTHAHALLI": 95,
        "Tarikere APMC": 40,
        "Koppa APMC": 75,
        "Kadur APMC": 40,
        "Shimoga APMC": 95,
        "Sagara APMC": 140,
    },
    "Uttara Kannada (Sirsi / Karwar)": {
        "Sirsi APMC": 15,
        "Siddapur APMC": 35,
        "Yellapur APMC": 50,
        "Sagara APMC": 75,
        "APMC THIRTHAHALLI": 145,
        "Shikaripura APMC": 120,
    },
    "Hassan": {
        "Arsikere APMC": 45,
        "Hassan APMC": 10,
        "Channarayapatna APMC": 38,
        "APMC THIRTHAHALLI": 180,
        "Shimoga APMC": 150,
    },
    "Dakshina Kannada (Mangaluru / Bantwal)": {
        "Bantwala APMC": 25,
        "Puttur APMC": 50,
        "Belthangady APMC": 60,
        "APMC THIRTHAHALLI": 165,
        "Sagara APMC": 210,
    },
    "Chitradurga": {
        "Hiriyur APMC": 40,
        "Chitradurga APMC": 15,
        "Channagiri APMC": 65,
        "Shimoga APMC": 100,
        "Shikaripura APMC": 130,
    },
    "Davanagere": {
        "Davanagere APMC": 15,
        "Harihar APMC": 20,
        "Channagiri APMC": 50,
        "Shikaripura APMC": 75,
        "Shimoga APMC": 90,
    },
    "Tumakuru (Tumkur)": {
        "Tumkur APMC": 15,
        "Tiptur APMC": 75,
        "Gubbi APMC": 25,
        "Hiriyur APMC": 95,
        "Ramanagara APMC": 110,
    },
    "Ramanagara / Bengaluru Rural": {
        "Ramanagara APMC": 20,
        "Yeshwanthpur APMC": 45,
        "Channapatna APMC": 35,
        "Kolar APMC": 110,
    }
}

# Freight rate estimates per kilometer based on vehicle capacity
VEHICLE_TYPES: Dict[str, Dict[str, Any]] = {
    "Small Pickup (e.g. Bolero / Ace - Up to 1.5 Tonnes / 15 Quintals)": {
        "capacity_quintals": 15,
        "rate_per_km": 25.0,  # ₹25 per km (round trip)
    },
    "Medium Truck (Up to 5 Tonnes / 50 Quintals)": {
        "capacity_quintals": 50,
        "rate_per_km": 40.0,  # ₹40 per km (round trip)
    },
    "Heavy Commercial Truck (10+ Tonnes / 100+ Quintals)": {
        "capacity_quintals": 100,
        "rate_per_km": 60.0,  # ₹60 per km (round trip)
    }
}


def get_estimated_distance(farmer_district: str, target_mandi: str) -> float:
    """Returns road distance in KM between district and mandi (or default estimate)."""
    district_map = DISTANCES_KM.get(farmer_district, {})
    if target_mandi in district_map:
        return district_map[target_mandi]
    # Default fallback distance estimate
    return 75.0


def calculate_net_transport_profit(
    farmer_district: str,
    target_mandi: str,
    lowest_mandi: str,
    price_diff_per_quintal: float,
    quantity_quintals: float,
    vehicle_type: str = "Small Pickup (e.g. Bolero / Ace - Up to 1.5 Tonnes / 15 Quintals)",
    custom_distance_km: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes gross extra revenue, estimated transport freight cost, and net extra profit.
    """
    distance_km = custom_distance_km if custom_distance_km is not None else get_estimated_distance(farmer_district, target_mandi)
    
    vehicle_info = VEHICLE_TYPES.get(vehicle_type, VEHICLE_TYPES["Small Pickup (e.g. Bolero / Ace - Up to 1.5 Tonnes / 15 Quintals)"])
    rate_per_km = vehicle_info["rate_per_km"]

    # Round trip transport distance
    round_trip_km = distance_km * 2
    estimated_freight_cost = round_trip_km * rate_per_km

    # Gross extra earnings selling at recommended vs lowest market
    gross_extra_revenue = price_diff_per_quintal * quantity_quintals

    # Net profit after deducting transport freight
    net_extra_profit = gross_extra_revenue - estimated_freight_cost
    net_profit_per_quintal = net_extra_profit / quantity_quintals if quantity_quintals else 0

    is_profitable = net_extra_profit > 0

    if is_profitable:
        recommendation_advice = (
            f"✅ **Profitable Choice**: Transporting {quantity_quintals:.0f} quintals to **{target_mandi}** "
            f"yields a gross extra revenue of ₹{gross_extra_revenue:,.0f}. "
            f"After deducting estimated transport costs of ₹{estimated_freight_cost:,.0f} ({distance_km:.0f} km), "
            f"you make a **PURE EXTRA NET PROFIT of ₹{net_extra_profit:,.0f}** (+₹{net_profit_per_quintal:,.0f}/quintal)."
        )
    else:
        recommendation_advice = (
            f"⚠️ **Caution - Transport Cost Exceeds Price Gain**: Transporting {quantity_quintals:.0f} quintals to {target_mandi} "
            f"costs approx ₹{estimated_freight_cost:,.0f} in freight, which outweighs your price gain of ₹{gross_extra_revenue:,.0f}. "
            f"Selling at a closer market like **{lowest_mandi}** is more profitable."
        )

    return {
        "farmer_district": farmer_district,
        "target_mandi": target_mandi,
        "lowest_mandi": lowest_mandi,
        "distance_km": distance_km,
        "round_trip_km": round_trip_km,
        "quantity_quintals": quantity_quintals,
        "vehicle_type": vehicle_type,
        "estimated_freight_cost": estimated_freight_cost,
        "gross_extra_revenue": gross_extra_revenue,
        "net_extra_profit": net_extra_profit,
        "net_profit_per_quintal": net_profit_per_quintal,
        "is_profitable": is_profitable,
        "advice": recommendation_advice
    }
