class ValidationService:

    MIN_WIDTH = 40
    MIN_HEIGHT = 15

    @classmethod
    def validate(
        cls,
        name,
        strokes
    ):

        if not name:

            return (
                False,
                "Employee name required."
            )

        if not strokes:

            return (
                False,
                "Signature required."
            )

        xs = []
        ys = []

        for stroke in strokes:

            for point in stroke:

                xs.append(point.x())
                ys.append(point.y())

        if not xs:

            return (
                False,
                "Invalid signature."
            )

        width = (
            max(xs)
            - min(xs)
        )

        height = (
            max(ys)
            - min(ys)
        )

        if (
            width < cls.MIN_WIDTH
            or
            height < cls.MIN_HEIGHT
        ):

            return (
                False,
                "Signature too small."
            )

        return (
            True,
            ""
        )