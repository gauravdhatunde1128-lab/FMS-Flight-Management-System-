import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

# -------------------------------
# MISSION & COST ENGINE
# -------------------------------
def run_mission_analysis(empty_m, pilot_pax, fuel_gal, cargo, pwr, alt, dist_nm, fuel_price):
    # Constants
    BSFC = 0.45  # lbs/hp-hr (typical for Lycoming engines)
    g, rho0 = 9.81, 1.225
    rho = rho0 * ((288.15 - 0.0065 * alt) / 288.15) ** 4.256
    
    # 1. Performance at Cruise (approx 75% power)
    cruise_pwr = pwr * 0.75
    fuel_flow_gph = (cruise_pwr * BSFC) / 6.0  # Gallons per hour
    
    # Estimate Cruise Speed (Simplified based on power/drag balance)
    # V_cruise ~ (Power / (0.5 * rho * S * CD0))^(1/3)
    v_cruise_mps = ( (cruise_pwr * 745.7 * 0.8) / (0.5 * rho * 16.2 * 0.032) )**(1/3)
    v_cruise_kts = v_cruise_mps * 1.94384
    
    # 2. Mission Calculations
    flight_time_hrs = dist_nm / v_cruise_kts
    total_fuel_burned = fuel_flow_gph * flight_time_hrs
    fuel_cost = total_fuel_burned * fuel_price
    
    # 3. Dynamic Weight & Balance (Start vs End of flight)
    fuel_mass_start = fuel_gal * 2.72
    fuel_mass_end = (fuel_gal - total_fuel_burned) * 2.72
    
    def get_cg(f_mass):
        moments = (empty_m * 1.02) + (pilot_pax * 0.94) + (f_mass * 1.22) + (cargo * 2.41)
        return moments / (empty_m + pilot_pax + f_mass + cargo)

    cg_start = get_cg(fuel_mass_start)
    cg_end = get_cg(fuel_mass_end)

    # -------------------------------
    # VISUALIZATION
    # -------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot 1: CG Migration (Industrial Standard for Flight Manuals)
    
    ax1.plot([0.89, 0.89, 1.19, 1.19, 0.89], [600, 1157, 1157, 600, 600], 'b-', label='Envelope')
    ax1.plot([cg_start, cg_end], [empty_m+pilot_pax+fuel_mass_start+cargo, empty_m+pilot_pax+fuel_mass_end+cargo], 'r-o', label='Fuel Burn Path')
    ax1.annotate('Takeoff', (cg_start, empty_m+pilot_pax+fuel_mass_start+cargo))
    ax1.annotate('Landing', (cg_end, empty_m+pilot_pax+fuel_mass_end+cargo))
    ax1.set_title("CG Migration During Mission"); ax1.legend(); ax1.grid(True)
    
    # Plot 2: Cost Breakdown
    ax2.pie([fuel_cost, 50, 100], labels=['Fuel Cost', 'Maintenance (Est)', 'Airport Fees'], autopct='%1.1f%%', colors=['gold', 'lightcoral', 'skyblue'])
    ax2.set_title(f"Trip Cost Analysis (Total: ${fuel_cost+150:.2f})")
    
    plt.tight_layout(); plt.show()
    
    print(f"--- MISSION SUMMARY ---")
    print(f"Est. Cruise Speed: {v_cruise_kts:.1f} knots")
    print(f"Flight Time: {flight_time_hrs:.2f} hours")
    print(f"Fuel Burned: {total_fuel_burned:.1f} Gallons")
    if total_fuel_burned > fuel_gal:
        print("❌ DANGER: INSUFFICIENT FUEL FOR THIS MISSION!")

# -------------------------------
# GUI
# -------------------------------
s = {'description_width': '140px'}
w_e = widgets.IntSlider(value=750, min=500, max=1000, description="Empty Mass (kg)", style=s)
w_p = widgets.IntSlider(value=170, min=0, max=400, description="Pilot/Pax (kg)", style=s)
w_f = widgets.IntSlider(value=40, min=10, max=53, description="Fuel Load (Gal)", style=s)
dist = widgets.IntSlider(value=200, min=50, max=500, description="Trip Dist (NM)", style=s)
f_price = widgets.FloatSlider(value=6.50, min=4.0, max=10.0, description="Fuel $/Gal", style=s)
alt = widgets.IntSlider(value=2500, min=0, max=4000, description="Cruise Alt (m)", style=s)
pwr = widgets.IntSlider(value=180, min=100, max=300, description="Engine HP", style=s)

ui = widgets.HBox([widgets.VBox([w_e, w_p, w_f]), widgets.VBox([dist, f_price]), widgets.VBox([alt, pwr])])
out = widgets.Output()

def update(change):
    with out:
        clear_output(wait=True)
        run_mission_analysis(w_e.value, w_p.value, w_f.value, 20, pwr.value, alt.value, dist.value, f_price.value)

for w in [w_e, w_p, w_f, dist, f_price, alt, pwr]: w.observe(update, 'value')
display(ui, out); update(None)

