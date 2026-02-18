from src.components.data_reader import DataReader

def initiate_data_reader_pipeline(data_path:str):
    data_reader = DataReader()
    try:
        cleaned_data_artifact = data_reader.initiate_data_reader(data_path)
        return cleaned_data_artifact
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")