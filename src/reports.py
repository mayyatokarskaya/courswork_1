import pandas as pd

def save_excel_report(data: pd.DataFrame, file_path: str):
    """Сохранение отчета в Excel."""
    data.to_excel(file_path, index=False)


