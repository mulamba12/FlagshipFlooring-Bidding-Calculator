import streamlit as st
import pandas as pd

# Default costs and constants
COSTS = {
    "sports_courts_base_cost_per_sqft": 3.03,
    "sports_courts_concrete_cost_per_sqft": 6.25,
    "light_cost_per_pair": 3000,
    "hoop_cost_each": 2300,
    "fence_cost_per_foot": 7,
    "epoxy_vapor_barrier_cost_per_gal": 86,
    "epoxy_vapor_barrier_coverage": 140,
    "flake_cost_per_box": 105,
    "flake_coverage": 350,
    "kinetic_85_ef_cost_per_10gal": 850,
    "kinetic_85_hs_cost_per_10gal": 1000,
    "kinetic_85_coverage": 120,
    "pigment_cost_per_gal": 38,
    "pigment_coverage": 140,
    "quartz_cost_per_bag": 24,
    "quartz_coverage": 80,
    "urethane_cement_cost_per_bag": 45,
    "urethane_cement_coverage": 100,
    "urethane_cement_standalone_cost_per_sqft": 6.0,
    "grinding_cost_per_machine": 1510,
    "grinding_coverage_per_machine": 7500,
    "cutting_agent_cost_per_5gal": 300,
    "cutting_agent_coverage": 500,
    "densifier_cost_per_5gal": 100,
    "densifier_coverage": 500,
    "guard_sealer_cost_per_gal": 600,
    "guard_sealer_coverage": 2500,
    "hourly_wage": 30,
    "mileage_rate": 0.68,
    "lodging_cost_per_day": 250,
    "workday_hours": 8,
    "lodging_distance_limit": 100,
}

def calculate_bid(job_type, square_footage, distance, profit_margin, num_workers, options=None):
    travel_cost = distance * COSTS["mileage_rate"] * 2
    lodging_cost = 0
    if distance > COSTS["lodging_distance_limit"]:
        lodging_days = (square_footage / (num_workers * COSTS["workday_hours"])) / 8
        lodging_cost = lodging_days * COSTS["lodging_cost_per_day"]

    material_cost = 0
    additional_costs = 0
    labor_hours = square_footage / 200  # Default productivity estimate
    additional_details = {}

    if job_type == "Sports Courts":
        material_cost = square_footage * COSTS["sports_courts_base_cost_per_sqft"]
        if options:
            if options.get("concrete"):
                additional_costs += square_footage * COSTS["sports_courts_concrete_cost_per_sqft"]
                additional_details["Concrete"] = additional_costs
            if options.get("lights"):
                additional_costs += options["num_courts"] * COSTS["light_cost_per_pair"]
                additional_details["Lights"] = additional_costs
            if options.get("hoops"):
                additional_costs += options["num_courts"] * COSTS["hoop_cost_each"]
                additional_details["Hoops"] = additional_costs
            if options.get("fence"):
                additional_costs += options["fence_length"] * COSTS["fence_cost_per_foot"]
                additional_details["Fence"] = additional_costs

    elif job_type == "Epoxy Flake":
        if options.get("over_quartz"):
            material_cost = (square_footage / COSTS["quartz_coverage"]) * COSTS["quartz_cost_per_bag"]
            labor_hours = square_footage / COSTS["quartz_coverage"]
        else:  # Over Flake
            if options.get("use_urethane_cement"):
                material_cost = (square_footage / COSTS["urethane_cement_coverage"]) * COSTS["urethane_cement_cost_per_bag"]
            else:
                material_cost = (square_footage / COSTS["epoxy_vapor_barrier_coverage"]) * COSTS["epoxy_vapor_barrier_cost_per_gal"]
            flake_cost = (square_footage / COSTS["flake_coverage"]) * COSTS["flake_cost_per_box"]
            material_cost += flake_cost
            if options.get("residential"):
                topcoat_cost = (square_footage / COSTS["kinetic_85_coverage"]) * COSTS["kinetic_85_ef_cost_per_10gal"]
            else:
                topcoat_cost = (square_footage / COSTS["kinetic_85_coverage"]) * COSTS["kinetic_85_hs_cost_per_10gal"]
            material_cost += topcoat_cost

    elif job_type == "Polished Concrete":
        grinding_cost = (square_footage / COSTS["grinding_coverage_per_machine"]) * COSTS["grinding_cost_per_machine"]
        cutting_agent_cost = (square_footage / COSTS["cutting_agent_coverage"]) * COSTS["cutting_agent_cost_per_5gal"]
        densifier_cost = (square_footage / COSTS["densifier_coverage"]) * COSTS["densifier_cost_per_5gal"]
        guard_cost = (square_footage / COSTS["guard_sealer_coverage"]) * COSTS["guard_sealer_cost_per_gal"]
        material_cost = grinding_cost + cutting_agent_cost + densifier_cost + guard_cost

    elif job_type == "Urethane Cement":
        material_cost = square_footage * COSTS["urethane_cement_standalone_cost_per_sqft"]
        labor_hours = labor_hours = square_footage / (num_workers * 25)

    labor_cost = labor_hours * COSTS["hourly_wage"]* num_workers
    total_cost = material_cost + labor_cost + additional_costs + travel_cost + lodging_cost
    profit = total_cost * (profit_margin / 100)
    bid_price = total_cost + profit

    return {
        "Material Cost": material_cost,
        "Labor Cost": labor_cost,
        "Additional Costs": additional_details,
        "Travel Cost": travel_cost,
        "Lodging Cost": lodging_cost,
        "Total Cost": total_cost,
        "Profit": profit,
        "Bid Price": bid_price,
    }

# Streamlit UI
st.title("Job Bidding Calculator")
st.sidebar.title("Adjust Costs")

# Sidebar: Adjust Costs
if st.sidebar.checkbox("Adjust Costs"):
    for key, value in COSTS.items():
        COSTS[key] = st.sidebar.number_input(f"{key.replace('_', ' ').title()}", value=value)

# Main Job Inputs
job_type = st.selectbox("Select Job Type", ["Sports Courts", "Epoxy Flake", "Polished Concrete", "Urethane Cement"])
square_footage = st.number_input("Square Footage", min_value=0.0)
distance = st.number_input("Distance from Lubbock (miles)", min_value=0.0)
profit_margin = st.number_input("Profit Margin (%)", min_value=0.0)
num_workers = st.number_input("Number of Workers", min_value=1)

options = {}
if job_type == "Sports Courts":
    options["concrete"] = st.checkbox("Include Concrete")
    options["lights"] = st.checkbox("Include Lights")
    options["hoops"] = st.checkbox("Include Hoops")
    options["fence"] = st.checkbox("Include Fence")
    options["fence_length"] = st.number_input("Fence Length (feet)", min_value=0.0)
    options["num_courts"] = st.number_input("Number of Courts", min_value=1)
elif job_type == "Epoxy Flake":
    options["over_quartz"] = st.checkbox("Over Quartz")
    if not options["over_quartz"]:
        options["use_urethane_cement"] = st.checkbox("Use Urethane Cement Instead of Vapor Barrier")
        options["residential"] = st.checkbox("Residential Application")

if st.button("Calculate Bid"):
    result = calculate_bid(job_type, square_footage, distance, profit_margin, num_workers, options)
    st.subheader("Job Pricing Summary")
    for key, value in result.items():
        st.write(f"{key}: {value}")
