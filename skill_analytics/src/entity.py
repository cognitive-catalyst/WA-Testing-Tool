
class Entity:

    def __init__(self, entity_obj):
        self.raw_obj = entity_obj

        self.ID = entity_obj.get("entity")
        self.is_fuzzy_match = entity_obj.get("fuzzy_match", False)
        self.values = entity_obj.get("values")