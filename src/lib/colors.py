class CFColors:

    @staticmethod
    def get_rating_color(rating):
        if type(rating) == str: return "grey"
        if rating < 1200: return "grey"
        if rating < 1400: return "green"
        if rating < 1600: return "cyan"
        if rating < 1900: return "blue"
        if rating < 2100: return "magenta"
        if rating < 2300: return "yellow"
        if rating < 2400: return "yellow"
        if rating < 2600: return "red"
        if rating < 3000: return "red"
        return "red"

    @staticmethod
    def get_participation_type_color(type):
        return "green" if type == "contestant" else ("yellow" if type == "virtual" else "cyan")

    @staticmethod
    def get_delta_color(delta):
        return "white" if type(delta) == str else ("red" if delta < 0 else ("green" if delta > 0 else "white"))
