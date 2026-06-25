# class TrailingSL:

#     @staticmethod
#     def update_sl(
#         current_sl,
#         previous_candle_low
#     ):

#         return max(
#             current_sl,
#             previous_candle_low
#         )

class TrailingSL:


    @staticmethod
    def update_sl(
        current_sl,
        previous_candle_low
    ):

        return max(
            current_sl,
            previous_candle_low
        )

