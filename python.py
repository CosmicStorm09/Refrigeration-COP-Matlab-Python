import CoolProp.CoolProp as CP
import matplotlib.pyplot as plt
import numpy as np

def get_state_props(refrigerant, P, T):
    """
    Get enthalpy (J/kg) and entropy (J/kg-K) at given pressure (Pa) and temperature (K)
    """
    h = CP.PropsSI('H', 'P', P, 'T', T, refrigerant)
    s = CP.PropsSI('S', 'P', P, 'T', T, refrigerant)
    return h, s

def get_saturated_props(refrigerant, P):
    """
    Get saturated liquid and vapor enthalpy and entropy at given pressure (Pa)
    """
    hL = CP.PropsSI('H', 'P', P, 'Q', 0, refrigerant)
    hV = CP.PropsSI('H', 'P', P, 'Q', 1, refrigerant)
    sL = CP.PropsSI('S', 'P', P, 'Q', 0, refrigerant)
    sV = CP.PropsSI('S', 'P', P, 'Q', 1, refrigerant)
    T_sat = CP.PropsSI('T', 'P', P, 'Q', 0, refrigerant)
    return hL, hV, sL, sV, T_sat

def main():
    print("Simple Vapor Compression Refrigeration System COP Calculator")
    refrigerant = input("Enter refrigerant (e.g., R134a, R22, R410A): ").strip()
    
    # Input pressures in kPa and convert to Pa
    P_evap_kPa = float(input("Enter evaporator pressure (kPa): "))
    P_cond_kPa = float(input("Enter condenser pressure (kPa): "))
    P_evap = P_evap_kPa * 1000
    P_cond = P_cond_kPa * 1000
    
    # Input temperatures in Celsius and convert to Kelvin
    T_evap_in_C = float(input("Enter evaporator inlet temperature (°C): "))
    T_evap_out_C = float(input("Enter evaporator outlet temperature (°C): "))
    T_cond_in_C = float(input("Enter condenser inlet temperature (°C): "))
    T_cond_out_C = float(input("Enter condenser outlet temperature (°C): "))
    
    T_evap_in = T_evap_in_C + 273
    T_evap_out = T_evap_out_C + 273
    T_cond_in = T_cond_in_C + 273
    T_cond_out = T_cond_out_C + 273
    
    # State 1: Evaporator outlet (saturated vapor ideally)
    h1, s1 = get_state_props(refrigerant, P_evap, T_evap_out)
    
    # State 2: Compressor outlet (isentropic compression from state 1 to condenser pressure)
    s2s = s1
    # Find temperature at condenser pressure with entropy s2s (isentropic)
    T2s = CP.PropsSI('T', 'P', P_cond, 'S', s2s, refrigerant)
    h2s = CP.PropsSI('H', 'P', P_cond, 'S', s2s, refrigerant)
    
    # Assume isentropic efficiency of compressor (optional, here 100%)
    eta_comp = 1.0
    # Real enthalpy at compressor outlet
    h2 = (h2s - h1) / eta_comp + h1
    
    # State 3: Condenser outlet (saturated liquid ideally)
    h3, s3 = get_state_props(refrigerant, P_cond, T_cond_out)
    
    # State 4: Expansion valve outlet (isenthalpic expansion)
    h4 = h3
    # At evaporator pressure, find temperature and entropy at h4
    T4 = CP.PropsSI('T', 'P', P_evap, 'H', h4, refrigerant)
    s4 = CP.PropsSI('S', 'P', P_evap, 'H', h4, refrigerant)
    
    # Refrigeration effect (q_in) = h1 - h4
    q_in = h1 - h4
    
    # Work input (w_in) = h2 - h1
    w_in = h2 - h1
    
    # COP = refrigeration effect / work input
    COP = q_in / w_in
    
    print("\nResults:")
    print(f"State 1 (Evaporator outlet): h1 = {h1/1000:.2f} kJ/kg, T1 = {T_evap_out_C:.2f} °C")
    print(f"State 2 (Compressor outlet): h2 = {h2/1000:.2f} kJ/kg, T2 = {T2s - 273:.2f} °C (isentropic T2s)")
    print(f"State 3 (Condenser outlet): h3 = {h3/1000:.2f} kJ/kg, T3 = {T_cond_out_C:.2f} °C")
    print(f"State 4 (Expansion valve outlet): h4 = {h4/1000:.2f} kJ/kg, T4 = {T4 - 273:.2f} °C")
    print(f"Refrigeration effect (q_in): {q_in/1000:.2f} kJ/kg")
    print(f"Work input (w_in): {w_in/1000:.2f} kJ/kg")
    print(f"Coefficient of Performance (COP): {COP:.2f}")
    
    # Plot p-h diagram with cycle
    plot_ph_diagram(refrigerant, P_evap, P_cond, [h1, h2, h3, h4], [P_evap, P_cond, P_cond, P_evap])

def plot_ph_diagram(refrigerant, P_evap, P_cond, h_cycle, P_cycle):
    # Generate saturation curve data
    P_sat = np.logspace(np.log10(P_evap*0.8), np.log10(P_cond*1.2), 500)
    hL = []
    hV = []
    for P in P_sat:
        try:
            hL.append(CP.PropsSI('H', 'P', P, 'Q', 0, refrigerant)/1000)
            hV.append(CP.PropsSI('H', 'P', P, 'Q', 1, refrigerant)/1000)
        except:
            hL.append(np.nan)
            hV.append(np.nan)
    P_sat_kPa = P_sat / 1000
    
    plt.figure(figsize=(10,6))
    plt.plot(hL, P_sat_kPa, 'b-', label='Saturated Liquid')
    plt.plot(hV, P_sat_kPa, 'r-', label='Saturated Vapor')
    
    # Plot cycle points and lines
    h_cycle_kJ = np.array(h_cycle) / 1000
    P_cycle_kPa = np.array(P_cycle) / 1000
    
    # Close the cycle by adding first point at end
    h_cycle_kJ = np.append(h_cycle_kJ, h_cycle_kJ[0])
    P_cycle_kPa = np.append(P_cycle_kPa, P_cycle_kPa[0])
    
    plt.plot(h_cycle_kJ, P_cycle_kPa, 'ko-', label='Cycle')
    
    for i, (h, P) in enumerate(zip(h_cycle_kJ[:-1], P_cycle_kPa[:-1])):
        plt.text(h, P, f'{i+1}', fontsize=12, fontweight='bold')
    
    plt.xlabel('Enthalpy (kJ/kg)')
    plt.ylabel('Pressure (kPa)')
    plt.title(f'Pressure-Enthalpy (p-h) Diagram for {refrigerant}')
    plt.yscale('log')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.gca().invert_yaxis()  # Pressure decreases upward in refrigeration p-h diagrams
    plt.show()

if __name__ == "__main__":
    main()
