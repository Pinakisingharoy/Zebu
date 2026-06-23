class TrailingSL:

    @staticmethod
    def update_sl(
        current_sl,
        previous_low
    ):

        if previous_low > current_sl:
            return previous_low

        return current_sl