from src.components.data_reader import DataReader

if __name__ == "__main__":
    data_reader = DataReader()
    DATA_PATH = "data/raw/students_list.xlsx"
    try:
        cleaned_data = data_reader.initiate_data_reader(DATA_PATH)
        # Save to processed/ output here
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")