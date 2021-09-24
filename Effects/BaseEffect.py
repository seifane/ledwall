from colorutils import Color


class BaseEffect:

    @staticmethod
    def get_name():
        return 'No name effect'

    def get_attributes(self):
        return []

    def get_attribute_value(self, attribute_name: str):
        return None

    def set_attribute_value(self, attribute_name: str, value: any):
        pass

    def stop(self):
        pass

    def draw(self, buffer: [[Color]]) -> [[Color]]:
        pass
