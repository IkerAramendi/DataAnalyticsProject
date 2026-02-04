import calendar
import numpy as np
import pandas as pd

def generate_synthetic_data():
    datetime_index = pd.date_range(
        start="2025-01-01",
        end="2025-12-31 23:00",
        freq="h"
    )

    df = pd.DataFrame({"datetime": datetime_index})
    df["hour"] = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.month
    df["day"] = df["datetime"].dt.day
    df["dayofyear"] = df["datetime"].dt.dayofyear

    df["solar_irradiation"] = df.apply(
        lambda x: generate_solar_irradiation(x["hour"], x["month"], x["day"]), axis=1
    )

    df["ambient_temperature"] = df.apply(
        lambda x: generate_temperature(x["hour"], x["month"]), axis=1
    )

    system_capacity = 5
    constant = 0.0009

    df["solar_energy_generated"] = (
        df["solar_irradiation"] * system_capacity * constant
    )
    df["energy_consumption"] = df.apply(
        lambda x: generate_consumption(x["hour"], x["month"]), axis=1
    )
    
    df["net_energy"] = (
        df["solar_energy_generated"] - df["energy_consumption"]
    )  
    
    df.to_csv("synthetic_energy_bilbao_2025.csv", index=False)

    return df


 

def generate_solar_irradiation(hour, month, day):
    monthly_max_irradiation = {
        1: 481, 2: 553, 3: 725, 4: 902,
        5: 926, 6: 925, 7: 923, 8: 891,
        9: 782, 10: 622, 11: 495, 12: 382
    }
    sunrise = 7
    sunset = 20
    if hour < sunrise or hour > sunset:
        return 0

    #Porcentaje del mes pasado
    days_in_month = calendar.monthrange(2025, month)[1]
    progress = (day - 1) / days_in_month

    current_max = monthly_max_irradiation[month]

    if month == 12:
        next_month = 1
    else:
        next_month = month + 1

    next_max = monthly_max_irradiation[next_month]
    
    max_val = (1 - progress) * current_max + progress * next_max

    value = max_val * np.sin(np.pi * (hour - sunrise) / (sunset - sunrise))
    noise = np.random.normal(0, 40)
    return max(value + noise, 0)
    

def generate_temperature(hour, month):
    monthly_avg_temp = {
        1: 9, 2: 10, 3: 12, 4: 13,
        5: 16, 6: 19, 7: 21, 8: 21,
        9: 19, 10: 16, 11: 12, 12: 10
    }
    base = monthly_avg_temp[month]
    daily_variation = 3 * np.sin(np.pi * (hour - 6) / 24)
    noise = np.random.normal(0, 1.5)
    return base + daily_variation + noise

def generate_consumption(hour, month):
    base = 0.4
    if 7 <= hour <= 9:
        base += 0.3
    if 18 <= hour <= 22:
        base += 0.4
    if month in [6,7,8]:
        base += 0.1
    return max(base + np.random.normal(0, 0.1), 0.1)