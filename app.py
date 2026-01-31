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

        #Update with new data
        st.subheader("Update data")
        if st.button("Add new hourly record"):
            new_row = df.iloc[-1].copy()
            new_row["datetime"] += pd.Timedelta(hours=1)
            st.session_state.df = pd.concat(
                [df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("New data added")

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


   