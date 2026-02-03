import streamlit as st
import pandas as pd
from generator import generate_synthetic_data

st.title("Synthetic Solar Energy Generator")

st.write("Generate synthetic rooftop solar data based on weather patterns")

tool = st.sidebar.selectbox(
    "Select tool",
    ["Synthetic Data Generator", "Analytics App"]
)

if tool == "Synthetic Data Generator":
        if st.button("Generate synthetic data"):
            df = generate_synthetic_data()
            st.success("Data generated!")
            st.dataframe(df.head(10000))
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="synthetic_energy.csv",
                mime="text/csv"
            )

if tool == "Analytics App":
    st.header("Energy Analytics App")

    #Upload CSV
    uploaded_file = st.file_uploader("Upload CSV")

    
    if uploaded_file:
        #Save state
        if "df" not in st.session_state:
            st.session_state.df = pd.read_csv(
                uploaded_file, parse_dates=["datetime"]
            )

        df = st.session_state.df

        st.subheader("Loaded data preview")
        st.dataframe(df.head(10000))

        st.subheader("Dataset summary")
        st.write("Rows:", len(df))
        st.write(
            "Date range:",
            df["datetime"].min(),
            "→",
            df["datetime"].max()
        )

        #Update with new data
        st.subheader("Update data")
        if st.button("Add new hourly record"):
            new_row = df.iloc[-1].copy()
            new_dt = new_row["datetime"] + pd.Timedelta(hours=1)
            new_row["datetime"] = new_dt

            new_row["hour"] = new_dt.hour
            new_row["month"] = new_dt.month
            new_row["dayofyear"] = new_dt.dayofyear
            new_row["date"] = new_dt.date()

            cols_to_nan = ["solar_irradiation", "ambient_temperature", "solar_energy_generated",
                           "energy_consumption", "net_energy"]
            new_row[cols_to_nan] = pd.NA

            st.session_state.df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            st.success("New hourly record added")
            df = st.session_state.df
   

   

        #Conflict handling
        duplicates = df.duplicated(subset="datetime").sum()
        st.write(f"Conflicting timestamps: {duplicates}")

        if duplicates > 0 and st.button("Remove duplicated timestamps"):
            st.session_state.df = df.drop_duplicates(
                subset="datetime", keep="first"
            )
            st.success("Conflicts resolved")

        df = st.session_state.df
        
        #Missing data handling
        st.subheader("Missing data handling (seasonality-aware)")

        numeric_cols = [
            "solar_irradiation",
            "ambient_temperature",
            "solar_energy_generated",
            "energy_consumption",
            "net_energy"
        ]

        df = st.session_state.df.copy()

        missing_rows = df[df[numeric_cols].isna().any(axis=1)]

        st.write("Rows with missing values:", len(missing_rows))

        if len(missing_rows) > 0 and st.button("Estimate missing values using historical patterns"):
            for idx in missing_rows.index:
                current_dt = df.loc[idx, "datetime"]

                # same hour one year ago
                past_year_dt = current_dt - pd.DateOffset(years=1)
                past_year_row = df[df["datetime"] == past_year_dt]
                
                # previous hour
                prev_row = df[df["datetime"] == (current_dt - pd.Timedelta(hours=1))]

                for col in numeric_cols:
                    
                    if col == "solar_irradiation" or col == "solar_energy_generated":
                        hour = current_dt.hour
                        if hour < 8 or hour > 20:
                            df.at[idx, col] = 0
                            continue  
                            
                    values = []

                    if not past_year_row.empty:
                        values.append(past_year_row.iloc[0][col])

                    if not prev_row.empty:
                        values.append(prev_row.iloc[0][col])

                    if values:
                        df.at[idx, col] = sum(values) / len(values)

            st.session_state.df = df
            st.success("Missing values estimated using seasonality-aware method")



        
        #Aggregations
        df["date"] = df["datetime"].dt.date
        daily = df.groupby("date").agg({
            "solar_energy_generated": "sum",
            "energy_consumption": "sum",
            "net_energy": "sum"
        }).reset_index()
        st.subheader("Daily aggregated data")
        st.dataframe(daily)


        #Visualizations
        st.subheader("Daily Energy Profiles")

        st.line_chart(
            daily.set_index("date")[
                ["solar_energy_generated", "energy_consumption"]
            ]
        )

        st.subheader("Daily Net Energy Balance")
        st.line_chart(daily.set_index("date")["net_energy"])


        #Interpolation / Prediction
        daily["solar_predicted"] = (
            daily["solar_energy_generated"]
            .rolling(window=2)
            .mean()
        )

        st.subheader("Solar Generation (with simple prediction)")
        st.line_chart(
            daily.set_index("date")[
                ["solar_energy_generated", "solar_predicted"]
            ]
        )

        #Save current state
        st.download_button(
            "Download current app state",
            st.session_state.df.to_csv(index=False),
            file_name="energy_app_state.csv",
            mime="text/csv"
        )


   