import pandas as pd

def load_data():
    google = pd.read_csv("data/google_ads.csv")
    facebook = pd.read_csv("data/facebook_ads.csv")
    instagram = pd.read_csv("data/instagram_ads.csv")

    google["Platform"] = "Google"
    facebook["Platform"] = "Facebook"
    instagram["Platform"] = "Instagram"

    return pd.concat([google, facebook, instagram])

def calculate_metrics(df):

    df["CTR"] = (df["Clicks"] / df["Impressions"]) * 100

    df["Conversion_Rate"] = (
        df["Conversions"] / df["Clicks"]
    ) * 100

    df["ROI"] = (
        (df["Revenue"] - df["Cost"])
        / df["Cost"]
    ) * 100

    return df