import os
from PyQt5.QtGui import QFontDatabase, QFont

class FontManager:
    _fonts_loaded = False
    PoppinsRegular = None
    PoppinsMedium = None
    PoppinsSemiBold = None

    @staticmethod
    def load_fonts():
        if FontManager._fonts_loaded:
            return

        base_dir = os.path.dirname(os.path.dirname(__file__))
        fonts_dir = os.path.join(base_dir, "global_assets", "fonts")

        
        regular_id = QFontDatabase.addApplicationFont(os.path.join(fonts_dir, "Poppins-Regular.ttf"))
        medium_id = QFontDatabase.addApplicationFont(os.path.join(fonts_dir, "Poppins-Medium.ttf"))
        semibold_id = QFontDatabase.addApplicationFont(os.path.join(fonts_dir, "Poppins-SemiBold.ttf"))

        regular_family = QFontDatabase.applicationFontFamilies(regular_id)[0]
        medium_family = QFontDatabase.applicationFontFamilies(medium_id)[0]
        semibold_family = QFontDatabase.applicationFontFamilies(semibold_id)[0]

        FontManager.PoppinsRegular = QFont(regular_family, 12)
        FontManager.PoppinsMedium = QFont(medium_family, 12)
        FontManager.PoppinsSemiBold = QFont(semibold_family, 14)

        FontManager._fonts_loaded = True
