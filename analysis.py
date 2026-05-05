def calculate_metrics(df):
    total_call = df["Call OI"].sum()
    total_put = df["Put OI"].sum()

    pcr = total_put / total_call if total_call != 0 else 0

    support = df.loc[df["Put OI"].idxmax(), "Strike"]
    resistance = df.loc[df["Call OI"].idxmax(), "Strike"]

    return pcr, support, resistance