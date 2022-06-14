class CFColors:

    @staticmethod
    def get_rating_color(rating):
        if type(rating) == str: return "grey"
        if rating < 1200: return "#a6a6a6"
        if rating < 1400: return "#69f562"
        if rating < 1600: return "#1cccd9"
        if rating < 1900: return "#0d7eff"
        if rating < 2100: return "#cc5ccc"
        if rating < 2300: return "#ffbb45"
        if rating < 2400: return "#e08e00"
        if rating < 2600: return "#ff1935"
        if rating < 3000: return "#ff1200"
        return "#8c0011"

    @staticmethod
    def get_participation_type_color(type):
        return "#11ff00" if type == "contestant" else ("#e5ff00" if type == "virtual" else "#9dff00")

    @staticmethod
    def get_delta_color(delta):
        return "white" if type(delta) == str else ("#ff0008" if delta < 0 else ("#15ff00" if delta > 0 else "white"))
