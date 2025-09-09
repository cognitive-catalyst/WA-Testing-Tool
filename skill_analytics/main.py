import json
from src.assistant_static_analyzer import AssistantStaticAnalyzer

def main(analyzer):
    variable_id = "<variable used in your assistant>"            # <-- TODO: Add your variable name here
    df = analyzer.search_for_variables(variable_id, return_as="csv")
    df.to_csv(f"{variable_id} usage.csv")                        # <-- OPTIONAL: Update the save path here
    print(df)

if __name__ == "__main__":
    path_to_assistant_json = "./jsons/<filename>.json"            # <-- TODO: Add your path here
    assistant_obj = json.load(open(path_to_assistant_json, 'r'))
    analyzer = AssistantStaticAnalyzer(assistant_obj)
    main(analyzer)
