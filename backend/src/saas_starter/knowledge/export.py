import json

class KnowledgeExporter:
    def export_dataset(self, dataset_data: dict) -> str:
        return json.dumps(dataset_data, indent=2)
