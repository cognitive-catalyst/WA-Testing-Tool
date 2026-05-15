
def move_col_to_front(df, first_col):
    if df.size == 0:
        return df
    new_col_order = [first_col] + [col for col in df.columns if col != first_col]
    return df[new_col_order]