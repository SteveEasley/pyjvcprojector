"""Command definitions."""

# pylint: disable=line-too-long

from .base import (
    Command,
    LaserPowerParameter,
    LightTimeParameter,
    MacAddressParameter,
    MapParameter,
    Model,
    ModelParameter,
    Spec,
    VersionParameter,
)

# SPECIFICATIONS:
# * Spec name is the year of the model release followed by an incremental sequence number.
# * Model name is really a model series/family since there is no way to know the exact model.
# * Model can be a list of models when they could go by different names (like in CS20191)
# * At runtime a projector model is matched to a spec in the order given below (e.g., B8A2, B8A1, B5A3, ...)
#   - First an exact match from top to bottom is done. If no match is found then:
#   - A partial match of the first 3 characters is done top to bottom. (e.g., B5A9 would match B5A3)
#   - If no match is found, the projector is considered to be in limp mode, with minimal command support.

SPECIFICATIONS: tuple[Spec, ...] = (
    CS20241 := Spec(
        "CS20241",
        B8A2 := Model("B8A2"),  # RS3200, NZ800, N988, V800R
        B8A1 := Model("B8A1"),  # RS4200, NZ900, N1188, V900R
    ),
    CS20242 := Spec(
        "CS20242",
        D8A2 := Model("D8A2"),  # NZ500, RS1200, N799, N788, N700, Z5
        D8A1 := Model("D8A1"),  # NZ700, RS2200, N899, N888, N800, Z7
    ),
    CS20221 := Spec(
        "CS20221",
        B5A3 := Model("B5A3"),  # RS2100, NZ7, N88, V70R
        B5A2 := Model("B5A2"),  # RS3100, NZ8, N98, V80R
        B5A1 := Model("B5A1"),  # RS4100, NZ9, N11, V90R
        B5B1 := Model("B5B1"),  # RS1100, NP5, N78, V50
    ),
    CS20191 := Spec(
        "CS20191",
        B2A3 := Model("B2A3", "A2B3"),  # RS1000, NX5, N5, N6, V5
        B2A2 := Model("B2A2", "A2B2"),  # RS2000, NX7, N7, N8, V7
        B2A1 := Model("B2A1", "A2B1"),  # RS3000, NX9, NX11, V9R
    ),
    CS20172 := Spec(
        "CS20172",
        A0A0 := Model("A0A0"),  # Z1, RS4500
    ),
    CS20171 := Spec(
        "CS20171",
        XHR1 := Model("XHR1"),  # X570R, RS420
        XHR3 := Model("XHR3"),  # X770R, X970, X970R, RS520, RS620
    ),
    CS20161 := Spec(
        "CS20161",
        XHP1 := Model("XHP1"),  # X550R, X5000, XC5890R, RS400
        XHP2 := Model("XHP2"),  # XC6890, XC6890R
        XHP3 := Model("XHP3"),  # X750R, X7000, XC7890R, RS500, X950R, X9000, RS600, PX1
    ),
    CS20141 := Spec(
        "CS20141",
        XHK1 := Model("XHK1"),  # X500R, XC5880R, RS49
        XHK2 := Model("XHK2"),  # RS4910
        XHK3 := Model("XHK3"),  # X700R, X7880R, XC7880R, RS57, X900R, RS67, RS6710
    ),
    CS20131 := Spec(
        "CS20131",
        XHG1 := Model("XHG1"),  # X35, XC3800, RS46, RS4810
        XHH1 := Model("XHH1"),  # X55R, XC5800R, RS48
        XHH4 := Model("XHH4"),  # X75R, XC7800R, RS56, X95R, XC9800R, RS66
    ),
    CS20121 := Spec(
        "CS20121",
        XHE := Model("XHE"),  # X30, XC388, RS45, RS4800
        XHF := Model("XHF"),  # X70R, XC788R, RS55, X90R, XC988R, RS65
    ),
)


class ModelName(Command):
    """Model command."""

    code = "MD"
    reference = True
    operation = False
    limp_mode = True
    parameter = ModelParameter()


class MacAddress(Command):
    """Mac Address command."""

    code = "LSMA"
    reference = True
    operation = False
    limp_mode = True
    parameter = MacAddressParameter()


class Version(Command):
    """Software Version command."""

    code = "IFSV"
    reference = True
    operation = False
    limp_mode = True
    parameter = VersionParameter()


class Power(Command):
    """Power command."""

    code = "PW"
    reference = True
    operation = True
    limp_mode = True

    OFF = "off"
    ON = "on"
    STANDBY = "standby"
    COOLING = "cooling"
    WARMING = "warming"
    ERROR = "error"

    parameter = MapParameter(
        size=1,
        read={
            "0": STANDBY,
            "1": ON,
            "2": COOLING,
            "3": WARMING,
            "4": ERROR,
        },
        write={
            "0": OFF,
            "1": ON,
        },
    )


class Input(Command):
    """Input command."""

    code = "IP"
    reference = True
    operation = True
    operation_timeout = 10.0
    limp_mode = True

    HDMI1 = "hdmi1"
    HDMI2 = "hdmi2"
    COMP = "comp"
    PC = "pc"

    parameter = MapParameter(
        size=1,
        readwrite={
            "6": HDMI1,
            "7": HDMI2,
        },
    )


class Signal(Command):
    """Signal command."""

    code = "SC"
    reference = True
    operation = False
    limp_mode = True

    NONE = "none"
    SIGNAL = "signal"

    parameter = MapParameter(
        size=1,
        read={
            "0": NONE,
            "1": SIGNAL,
        },
    )


class Remote(Command):
    """Remote command."""

    code = "RC"
    reference = False
    operation = True
    limp_mode = True

    OK = "ok"
    MENU = "menu"
    BACK = "back"
    HIDE = "hide"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    INFO = "info"
    INPUT = "input"
    HDMI1 = "hdmi1"
    HDMI2 = "hdmi2"
    SETTING_MEMORY = "setting-memory"
    LENS_CONTROL = "lens-control"
    PICTURE_MODE = "picture-mode"
    COLOR_PROFILE = "color-profile"
    GAMMA_SETTINGS = "gamma-settings"
    CMD = "cmd"
    MPC = "mpc"
    ADVANCED_MENU = "advanced-menu"
    MODE_1 = "mode-1"
    MODE_2 = "mode-2"
    MODE_3 = "mode-3"
    MODE_4 = "mode-4"
    MODE_5 = "mode-5"
    MODE_6 = "mode-6"
    MODE_7 = "mode-7"
    MODE_8 = "mode-8"
    MODE_9 = "mode-9"
    MODE_10 = "mode-10"
    LENS_APERTURE = "lens-aperture"
    PICTURE_ADJUST = "picture-adjust"
    ANAMORPHIC = "anamorphic"
    GAMMA = "gamma"
    COLOR_TEMP = "color-temp"
    V3D_FORMAT = "3d-format"
    NATURAL = "natural"
    CINEMA = "cinema"

    parameter = MapParameter(
        size=4,
        write={
            "732F": OK,
            "732E": MENU,
            "7303": BACK,
            "731D": HIDE,
            "7301": UP,
            "7302": DOWN,
            "7336": LEFT,
            "7334": RIGHT,
            "7374": INFO,
            "7308": INPUT,
            "7370": HDMI1,
            "7371": HDMI2,
            "73D4": SETTING_MEMORY,
            "7330": LENS_CONTROL,
            "73F4": PICTURE_MODE,
            "7388": COLOR_PROFILE,
            "73F5": GAMMA_SETTINGS,
            "738A": CMD,
            "73F0": MPC,
            "7373": ADVANCED_MENU,
            "73D8": MODE_1,
            "73D9": MODE_2,
            "73DA": MODE_3,
            "73E5": MODE_4,
            "73E6": MODE_5,
            "73E7": MODE_6,
            "73E8": MODE_7,
            "73E9": MODE_8,
            "73EA": MODE_9,
            "73EB": MODE_10,
            "7320": LENS_APERTURE,
            "7372": PICTURE_ADJUST,
            "73C5": ANAMORPHIC,
            "7375": GAMMA,
            "7376": COLOR_TEMP,
            "73D6": V3D_FORMAT,
            "736A": NATURAL,
            "7368": CINEMA,
        },
    )


class PictureMode(Command):
    """Picture Mode command."""

    code = "PMPM"
    reference = True
    operation = True

    ANIMATION = "animation"
    CINEMA = "cinema"
    FILM = "film"
    FILMMAKER_MODE = "filmmaker-mode"
    FRAME_ADAPT_HDR = "frame-adapt-hdr"
    FRAME_ADAPT_HDR2 = "frame-adapt-hdr2"
    FRAME_ADAPT_HDR3 = "frame-adapt-hdr3"
    HDR = "hdr"
    HDR1 = "hdr1"
    HDR2 = "hdr2"
    HDR10 = "hdr10"
    HDR10_LL = "hdr10-ll"
    HDR10_PLUS = "hdr10+"
    HLG = "hlg"
    HLG_LL = "hlg-ll"
    ISF_DAY = "isf-day"
    ISF_NIGHT = "isf-night"
    NATURAL = "natural"
    NATURAL_LL = "natural-ll"
    PANA_PQ = "pana-pq"
    PHOTO = "photo"
    RESERVED = "reserved"
    SDR_1 = "sdr-1"
    SDR_2 = "sdr-2"
    STAGE = "stage"
    THX = "thx"
    THX_BRIGHT = "thx-bright"
    THX_DARK = "thx-dark"
    USER_1 = "user-1"
    USER_2 = "user-2"
    USER_3 = "user-3"
    USER_4 = "user-4"
    USER_5 = "user-5"
    USER_6 = "user-6"
    VIVID = "vivid"
    THREE_D = "3d"
    R4K = "4k"

    parameter = {
        CS20241: MapParameter(
            size=2,
            readwrite={
                "00": FILM,
                "01": CINEMA,
                "03": NATURAL,
                "04": HDR10,
                "0B": FRAME_ADAPT_HDR,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
                "11": USER_6,
                "14": HLG,
                "15": HDR10_PLUS,
                "17": FILMMAKER_MODE,
                "18": FRAME_ADAPT_HDR2,
                "19": FRAME_ADAPT_HDR3,
                "1B": VIVID,
                "1C": NATURAL_LL,
                "1D": HDR10_LL,
                "1E": HLG_LL,
            },
        ),
        CS20242: MapParameter(
            size=2,
            readwrite={
                "01": CINEMA,
                "03": NATURAL,
                "0B": FRAME_ADAPT_HDR,
                "0C": SDR_1,
                "0D": SDR_2,
                "0E": HDR1,
                "0F": HDR2,
                "14": HLG,
                "15": HDR10_PLUS,
                "17": FILMMAKER_MODE,
                "18": FRAME_ADAPT_HDR2,
                "1B": VIVID,
            },
        ),
        CS20221: MapParameter(
            size=2,
            readwrite={
                "00": (FILM, B5A1, B5A2),
                "01": CINEMA,
                "03": NATURAL,
                "04": HDR10,
                "0B": FRAME_ADAPT_HDR,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
                "11": USER_6,
                "14": HLG,
                "15": HDR10_PLUS,
                "16": PANA_PQ,
                "17": FILMMAKER_MODE,
                "18": FRAME_ADAPT_HDR2,
                "19": FRAME_ADAPT_HDR3,
            },
        ),
        CS20191: MapParameter(
            size=2,
            readwrite={
                "00": (FILM, B2A1, B2A2),
                "01": CINEMA,
                "03": NATURAL,
                "04": HDR10,
                "06": (THX, B2A1),
                "0B": FRAME_ADAPT_HDR,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
                "11": USER_6,
                "14": HLG,
                "16": PANA_PQ,
            },
        ),
        CS20172: MapParameter(
            size=2,
            readwrite={
                "00": FILM,
                "01": CINEMA,
                "03": NATURAL,
                "04": HDR,
                "06": THX,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
                "11": USER_6,
            },
        ),
        CS20171: MapParameter(
            size=2,
            readwrite={
                "00": (FILM, XHR3),
                "01": CINEMA,
                "02": ANIMATION,
                "03": NATURAL,
                "04": HDR,
                "06": (THX, XHR3),
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
            },
        ),
        CS20161: MapParameter(
            size=2,
            readwrite={
                "00": (FILM, XHP3),
                "01": CINEMA,
                "02": ANIMATION,
                "03": NATURAL,
                "06": (THX, XHP3),
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
                "11": USER_6,
            },
        ),
        CS20141: MapParameter(
            size=2,
            read={
                "00": (FILM, XHK3),
                "01": CINEMA,
                "02": ANIMATION,
                "03": NATURAL,
                "04": STAGE,
                "06": (THX, XHK3),
                "0B": R4K,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "12": (PHOTO, XHK3),
            },
            write={
                "00": (FILM, XHK3),
                "01": CINEMA,
                "02": ANIMATION,
                "03": NATURAL,
                "04": STAGE,
                "06": (THX, XHK3),
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "12": (PHOTO, XHK3),
            },
        ),
        CS20131: MapParameter(
            size=2,
            readwrite={
                "00": FILM,
                "01": CINEMA,
                "02": ANIMATION,
                "03": NATURAL,
                "04": STAGE,
                "05": RESERVED,
                "06": THX,
                "07": (ISF_DAY, XHH4),
                "08": (ISF_NIGHT, XHH4),
                "09": (THX_BRIGHT, XHH4),
                "0A": (THX_DARK, XHH4),
                "0B": THREE_D,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
            },
        ),
        CS20121: MapParameter(
            size=2,
            readwrite={
                "00": FILM,
                "01": CINEMA,
                "02": ANIMATION,
                "03": NATURAL,
                "04": STAGE,
                "05": RESERVED,
                "06": THX,
                "07": (ISF_DAY, XHF),
                "08": (ISF_NIGHT, XHF),
                "09": (THX_BRIGHT, XHF),
                "0A": (THX_DARK, XHF),
                "0B": THREE_D,
                "0C": USER_1,
                "0D": USER_2,
                "0E": USER_3,
                "0F": USER_4,
                "10": USER_5,
            },
        ),
    }


class IntelligentLensAperture(Command):
    """Intelligent Lens Aperture command."""

    code = "PMDI"
    reference = True
    operation = True

    OFF = "off"
    AUTO_1 = "auto-1"
    AUTO_2 = "auto-2"

    parameter = {
        CS20221: MapParameter(
            size=1,
            readwrite={
                "0": (OFF, B5B1),
                "1": (AUTO_1, B5B1),
                "2": (AUTO_2, B5B1),
            },
        ),
        (CS20191, CS20171, CS20161, CS20141): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": AUTO_1,
                "2": AUTO_2,
            },
        ),
    }


class ColorProfile(Command):
    """Color Profile command."""

    code = "PMPR"
    reference = True
    operation = True

    ADOBE = "adobe"
    ANIME = "anime"
    ANIME_1 = "anime-1"
    ANIME_2 = "anime-2"
    AUTO = "auto"
    BT_2020 = "bt-2020"
    BT_2020_NORMAL = "bt-2020-normal"
    BT_2020_WIDE = "bt-2020-wide"
    BT_709 = "bt-709"
    CINEMA = "cinema"
    CINEMA_1 = "cinema-1"
    CINEMA_2 = "cinema-2"
    CUSTOM_1 = "custom-1"
    CUSTOM_2 = "custom-2"
    CUSTOM_3 = "custom-3"
    CUSTOM_4 = "custom-4"
    CUSTOM_5 = "custom-5"
    CUSTOM_6 = "custom-6"
    DCI = "dci"
    FILM = "film"
    FILM_1 = "film-1"
    FILM_2 = "film-2"
    FILM_3 = "film-3"
    HDR = "hdr"
    NATURAL = "natural"
    OFF = "off"
    OFF_WIDE = "off-wide"
    PANA_PQ_BL = "pana-pq-bl"
    PANA_PQ_HL = "pana-pq-hl"
    REFERENCE = "reference"
    STAGE = "stage"
    STANDARD = "standard"
    THX = "thx"
    VIDEO = "video"
    VIVID = "vivid"
    THREE_D = "3d"
    THREE_D_ANIMATION = "3d-animation"
    THREE_D_ANIME = "3d-anime"
    THREE_D_CINEMA = "3d-cinema"
    THREE_D_FILM = "3d-film"
    THREE_D_PHOTO = "3d-photo"
    THREE_D_STAGE = "3d-stage"
    THREE_D_THX = "3d-thx"
    THREE_D_VIDEO = "3d-video"
    XV_COLOR = "xv-color"

    parameter = {
        CS20241: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": FILM_1,
                "02": FILM_2,
                "03": BT_709,
                "04": CINEMA,
                "06": ANIME,
                "08": VIDEO,
                "0B": BT_2020_WIDE,
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "21": DCI,
                "23": VIVID,
                "24": BT_2020_NORMAL,
                "25": OFF_WIDE,
                "26": AUTO,
            },
        ),
        CS20242: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "03": BT_709,
                "04": CINEMA,
                "06": (ANIME, D8A1),
                "08": VIDEO,
                "0B": (BT_2020_WIDE, D8A1),
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "21": DCI,
                "23": VIVID,
                "24": BT_2020_NORMAL,
                "25": (OFF_WIDE, D8A1),
                "26": AUTO,
            },
        ),
        CS20221: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": (FILM_1, B5A1, B5A2),
                "02": (FILM_2, B5A1, B5A2),
                "03": BT_709,
                "04": CINEMA,
                "06": (ANIME, B5A1, B5A2),
                "08": VIDEO,
                "0B": (BT_2020_WIDE, B5A1, B5A2),
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "12": CUSTOM_5,
                "21": DCI,
                "22": CUSTOM_6,
                "24": BT_2020_NORMAL,
                "25": (OFF_WIDE, B5A1, B5A2),
                "26": AUTO,
            },
        ),
        CS20191: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": (FILM_1, B2A1, B2A2),
                "02": (FILM_2, B2A1, B2A2),
                "03": BT_709,
                "04": CINEMA,
                "06": (ANIME, B2A1, B2A2),
                "08": VIDEO,
                "0A": HDR,
                "0B": (BT_2020_WIDE, B2A1, B2A2),
                "0D": (THX, B2A1),
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "12": PANA_PQ_HL,
                "21": DCI,
                "22": PANA_PQ_BL,
                "24": BT_2020_NORMAL,
                "25": (OFF_WIDE, B2A1, B2A2),
                "26": AUTO,
            },
        ),
        CS20172: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": FILM_1,
                "02": FILM_2,
                "03": BT_709,
                "04": CINEMA,
                "06": ANIME,
                "0A": HDR,
                "0B": BT_2020,
                "0D": THX,
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "12": CUSTOM_5,
                "21": DCI,
                "22": CUSTOM_6,
            },
        ),
        CS20171: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": (FILM_1, XHR3),
                "02": (FILM_2, XHR3),
                "03": STANDARD,
                "04": CINEMA_1,
                "05": (CINEMA_2, XHR3),
                "06": ANIME_1,
                "07": (ANIME_2, XHR3),
                "08": VIDEO,
                "09": XV_COLOR,
                "0B": BT_2020,
                "0C": THREE_D_CINEMA,
                "0D": (THX, XHR3),
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "12": CUSTOM_5,
                "13": (FILM_3, XHR3),
                "14": THREE_D_VIDEO,
                "15": THREE_D_ANIMATION,
                "1E": (THREE_D_FILM, XHR3),
                "20": (THREE_D_THX, XHR3),
                "21": (REFERENCE, XHR3),
            },
        ),
        CS20161: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": (FILM_1, XHP3),
                "02": (FILM_2, XHP3),
                "03": STANDARD,
                "04": CINEMA_1,
                "05": (CINEMA_2, XHP3),
                "06": ANIME_1,
                "07": (ANIME_2, XHP3),
                "08": VIDEO,
                "09": (XV_COLOR, XHP3),
                "0C": THREE_D_CINEMA,
                "0D": (THX, XHP3),
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "12": CUSTOM_5,
                "13": (FILM_3, XHP3),
                "14": THREE_D_VIDEO,
                "15": THREE_D_ANIMATION,
                "1E": (THREE_D_FILM, XHP3),
                "20": (THREE_D_THX, XHP3),
                "21": (REFERENCE, XHP3),
                "22": CUSTOM_6,
            },
        ),
        CS20141: MapParameter(
            size=2,
            readwrite={
                "00": OFF,
                "01": (FILM_1, XHK3),
                "02": (FILM_2, XHK3),
                "03": STANDARD,
                "04": CINEMA_1,
                "05": (CINEMA_2, XHK3),
                "06": ANIME_1,
                "07": (ANIME_2, XHK3),
                "08": VIDEO,
                "09": (XV_COLOR, XHK3),
                "0A": (ADOBE, XHK3),
                "0B": STAGE,
                "0C": THREE_D_CINEMA,
                "0D": (THX, XHK3),
                "0E": CUSTOM_1,
                "0F": CUSTOM_2,
                "10": CUSTOM_3,
                "11": CUSTOM_4,
                "12": CUSTOM_5,
                "13": (FILM_3, XHK3),
                "14": THREE_D_VIDEO,
                "15": THREE_D_ANIME,
                "16": (THREE_D_PHOTO, XHK3),
                "1E": (THREE_D_FILM, XHK3),
                "1F": (THREE_D_STAGE, XHK3),
                "20": (THREE_D_THX, XHK3),
            },
        ),
        CS20131: MapParameter(
            size=2,
            readwrite={
                "00": (OFF, XHH4),
                "01": (FILM_1, XHH4),
                "02": (FILM_2, XHH4),
                "03": (STANDARD, XHH4),
                "04": (CINEMA_1, XHH4),
                "05": (CINEMA_2, XHH4),
                "06": (ANIME_1, XHH4),
                "07": (ANIME_2, XHH4),
                "08": (VIDEO, XHH4),
                "09": (VIVID, XHH4),
                "0A": (ADOBE, XHH4),
                "0B": (STAGE, XHH4),
                "0C": (THREE_D_CINEMA, XHH4),
                "0D": (THX, XHH4),
                "0E": (CUSTOM_1, XHH4),
                "0F": (CUSTOM_2, XHH4),
                "10": (CUSTOM_3, XHH4),
                "11": (CUSTOM_4, XHH4),
                "12": (CUSTOM_5, XHH4),
                "13": (FILM_3, XHH4),
                "14": (THREE_D_VIDEO, XHH4),
                "15": (THREE_D_ANIME, XHH4),
                "16": (STANDARD, XHH1),
                "17": (FILM, XHH1),
                "18": (CINEMA, XHH1),
                "19": (ANIME, XHH1),
                "1A": (NATURAL, XHH1),
                "1B": (STAGE, XHH1),
                "1C": (THREE_D, XHH1),
                "1D": (OFF, XHH1),
            },
        ),
        CS20121: MapParameter(
            size=2,
            readwrite={
                "00": (OFF, XHF),
                "01": (FILM_1, XHF),
                "02": (FILM_2, XHF),
                "03": (STANDARD, XHF),
                "04": (CINEMA_1, XHF),
                "05": (CINEMA_2, XHF),
                "06": (ANIME_1, XHF),
                "07": (ANIME_2, XHF),
                "08": (VIDEO, XHF),
                "09": (VIVID, XHF),
                "0A": (ADOBE, XHF),
                "0B": (STAGE, XHF),
                "0C": (THREE_D, XHF),
                "0D": (THX, XHF),
                "0E": (CUSTOM_1, XHF),
                "0F": (CUSTOM_2, XHF),
                "10": (CUSTOM_3, XHF),
                "11": (CUSTOM_4, XHF),
                "12": (CUSTOM_5, XHF),
            },
        ),
    }


class ColorManagement(Command):
    """Color Management command."""

    code = "PMCB"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"
    CUSTOM_1 = "custom-1"
    CUSTOM_2 = "custom-2"
    CUSTOM_3 = "custom-3"

    parameter = {
        (CS20241, CS20242, CS20221, CS20191, CS20172, CS20171, CS20161): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
        CS20141: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": CUSTOM_1,
                "2": CUSTOM_2,
                "3": CUSTOM_3,
            },
        ),
        CS20131: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": (CUSTOM_1, XHH4),
                "2": (CUSTOM_2, XHH4),
                "3": (CUSTOM_3, XHH4),
            },
        ),
        CS20121: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": (CUSTOM_1, XHF),
                "2": (CUSTOM_2, XHF),
                "3": (CUSTOM_3, XHF),
            },
        ),
    }


class ColorTemperature(Command):
    """Color Temperature command."""

    code = "PMCL"
    reference = True
    operation = True

    CUSTOM_1 = "custom-1"
    CUSTOM_2 = "custom-2"
    CUSTOM_3 = "custom-3"
    HDR = "hdr"
    HDR10 = "hdr10"
    HDR10_PLUS = "hdr10+"
    HIGH_BRIGHT = "high-bright"
    HLG = "hlg"
    VIVID = "vivid"
    T5500K = "5500k"
    T6000K = "6000k"
    T6500K = "6500k"
    T7000K = "7000k"
    T7500K = "7500k"
    T8000K = "8000k"
    T8500K = "8500k"
    T9000K = "9000k"
    T9300K = "9300k"
    T9500K = "9500k"
    XENON_1 = "xenon-1"
    XENON_2 = "xenon-2"
    XENON_3 = "xenon-3"

    parameter = {
        CS20241: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0A": CUSTOM_1,
                "0B": CUSTOM_2,
                "0C": HDR10,
                "0D": XENON_1,
                "0E": XENON_2,
                "14": HLG,
                "15": HDR10_PLUS,
            },
        ),
        CS20242: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0A": CUSTOM_1,
                "0B": CUSTOM_2,
                "0C": HDR10,
                "0D": (XENON_1, D8A1),
                "0E": (XENON_2, D8A1),
                "14": HLG,
                "15": HDR10_PLUS,
            },
        ),
        CS20221: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0A": (CUSTOM_1, B5A1, B5A2, B5B1),
                "0B": CUSTOM_2,
                "0C": HDR10,
                "0D": (XENON_1, B5A1, B5A2),
                "0E": (XENON_2, B5A1, B5A2),
                "14": HLG,
                "15": HDR10_PLUS,
            },
        ),
        CS20191: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0A": (CUSTOM_1, B2A1, B2A2),
                "0B": CUSTOM_2,
                "0C": HDR10,
                "0D": (XENON_1, B2A1, B2A2),
                "0E": (XENON_2, B2A1, B2A2),
                "14": HLG,
            },
        ),
        CS20172: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0A": CUSTOM_1,
                "0B": CUSTOM_2,
                "0C": HDR,
                "0D": XENON_1,
                "0E": XENON_2,
            },
        ),
        CS20171: MapParameter(
            size=1,
            readwrite={
                "0": T5500K,
                "2": T6500K,
                "4": T7500K,
                "8": T9300K,
                "9": HIGH_BRIGHT,
                "A": CUSTOM_1,
                "B": CUSTOM_2,
                "C": HDR,
                "D": XENON_1,
                "E": XENON_2,
                "F": XENON_3,
            },
        ),
        CS20161: MapParameter(
            size=1,
            readwrite={
                "0": T5500K,
                "2": T6500K,
                "4": T7500K,
                "8": T9300K,
                "9": HIGH_BRIGHT,
                "A": CUSTOM_1,
                "B": CUSTOM_2,
                "C": CUSTOM_3,
                "D": XENON_1,
                "E": XENON_2,
                "F": XENON_3,
            },
        ),
        (CS20141, CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": T5500K,
                "1": T6000K,
                "2": T6500K,
                "3": T7000K,
                "4": T7500K,
                "5": T8000K,
                "6": T8500K,
                "7": T9000K,
                "8": T9500K,
                "9": HIGH_BRIGHT,
                "A": CUSTOM_1,
                "B": CUSTOM_2,
                "C": CUSTOM_3,
                "D": XENON_1,
                "E": XENON_2,
                "F": XENON_3,
            },
        ),
    }


class ColorTemperatureCorrection(Command):
    """Color Temperature Correction command."""

    code = "PMCC"
    reference = True
    operation = True

    HIGH_BRIGHT = "high-bright"
    T5500K = "5500k"
    T6000K = "6000k"
    T6500K = "6500k"
    T7000K = "7000k"
    T7500K = "7500k"
    T8000K = "8000k"
    T8500K = "8500k"
    T9000K = "9000k"
    T9300K = "9300k"
    T9500K = "9500k"
    XENON_1 = "xenon-1"
    XENON_2 = "xenon-2"
    XENON_3 = "xenon-3"

    parameter = {
        CS20241: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0D": XENON_1,
                "0E": XENON_2,
            },
        ),
        CS20242: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0D": (XENON_1, D8A1),
                "0E": (XENON_2, D8A1),
            },
        ),
        CS20221: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0D": (XENON_1, B5A1, B5A2),
                "0E": (XENON_2, B5A1, B5A2),
            },
        ),
        CS20191: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0D": (XENON_1, B2A1, B2A2),
                "0E": (XENON_2, B2A1, B2A2),
            },
        ),
        CS20172: MapParameter(
            size=2,
            readwrite={
                "00": T5500K,
                "02": T6500K,
                "04": T7500K,
                "08": T9300K,
                "09": HIGH_BRIGHT,
                "0D": XENON_1,
                "0E": XENON_2,
            },
        ),
        (CS20171, CS20161): MapParameter(
            size=1,
            readwrite={
                "0": T5500K,
                "2": T6500K,
                "4": T7500K,
                "8": T9300K,
                "9": HIGH_BRIGHT,
                "D": XENON_1,
                "E": XENON_2,
                "F": XENON_3,
            },
        ),
        CS20141: MapParameter(
            size=1,
            readwrite={
                "0": T5500K,
                "1": T6000K,
                "2": T6500K,
                "3": T7000K,
                "4": T7500K,
                "5": T8000K,
                "6": T8500K,
                "7": T9000K,
                "8": T9500K,
                "9": HIGH_BRIGHT,
                "D": XENON_1,
                "E": XENON_2,
                "F": XENON_3,
            },
        ),
        (CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": T5500K,
                "1": T6000K,
                "2": T6500K,
                "3": T7000K,
                "4": T7500K,
                "5": T8000K,
                "6": T8500K,
                "7": T9000K,
                "8": T9500K,
                "9": HIGH_BRIGHT,
                "A": XENON_1,
                "B": XENON_2,
                "C": XENON_3,
            },
        ),
    }


class MotionEnhance(Command):
    """Motion Enhance command."""

    code = "PMME"
    reference = True
    operation = True

    OFF = "off"
    LOW = "low"
    HIGH = "high"

    parameter = {
        (CS20241, CS20221, CS20191, CS20172, CS20171, CS20161): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": LOW,
                "2": HIGH,
            },
        ),
    }


class LightPower(Command):
    """Light Power (Lamp/Laser) command."""

    code = "PMLP"
    reference = True
    operation = True

    LOW = "low"
    MID = "mid"
    HIGH = "high"
    NORMAL = "normal"

    parameter = {
        (CS20241, CS20242): MapParameter(
            size=1,
            readwrite={
                "0": LOW,
                "1": HIGH,
                "2": MID,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={"0": LOW, "1": HIGH, "2": (MID, B5A3, B5A2, B5A1)},
        ),
        CS20172: MapParameter(
            size=1,
            readwrite={
                "0": NORMAL,
                "1": HIGH,
                "2": MID,
            },
        ),
        (CS20191, CS20171, CS20161, CS20141, CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": NORMAL,
                "1": HIGH,
            },
        ),
    }


class LaserPower(Command):
    """Laser Power (LD Current) command."""

    code = "PMCV"
    reference = True
    operation = True

    parameter = {
        (CS20241, CS20242): LaserPowerParameter(),
    }


class EShift(Command):
    """EShift command."""

    code = "PMUS"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "0": (OFF, B5A1, B5A2, B5A3),
                "1": (ON, B5A1, B5A2, B5A3),
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "0": (OFF, B2A1),
                "1": (ON, B2A1),
            },
        ),
        (CS20172, CS20171, CS20161, CS20141): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
    }


class GraphicMode(Command):
    """Graphic Mode command."""

    code = "PMGM"
    reference = True
    operation = True

    HIGH_RES = "high-res"
    HIGH_RES_2 = "high-res-2"
    OFF = "off"
    STANDARD = "standard"
    R2K = "2k"
    R4K = "4k"
    LOW = "low"
    HIGH = "high"

    parameter = {
        (CS20241, CS20221): MapParameter(
            size=1,
            read={
                "0": STANDARD,
                "1": HIGH_RES,
                "2": HIGH_RES_2,
                "F": OFF,
            },
            write={
                "0": STANDARD,
                "1": HIGH_RES,
                "2": HIGH_RES_2,
            },
        ),
        CS20242: MapParameter(
            size=1,
            readwrite={
                "0": HIGH,
                "1": LOW,
                "2": OFF,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "0": STANDARD,
                "1": HIGH_RES,
            },
        ),
        (CS20172, CS20171): MapParameter(
            size=1,
            readwrite={
                "0": R2K,
                "1": R4K,
            },
        ),
    }


class Smoother(Command):
    """Smoother command."""

    code = "PMST"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        CS20241: MapParameter(
            size=4,
            readwrite={
                "0000": ON,
                "0001": OFF,
            },
        )
    }


class Hdr(Command):
    """HDR command."""

    code = "IFHR"
    reference = True
    operation = False

    SDR = "sdr"
    HDR = "hdr"
    SMPTE_ST_2084 = "smpte-st-2084"
    HYBRID_LOG = "hybrid-log"
    HDR10_PLUS = "hdr10+"
    NONE = "none"

    parameter = {
        (CS20241, CS20242): MapParameter(
            size=1,
            read={
                "0": SDR,
                "1": HDR,
                "2": SMPTE_ST_2084,
                "3": HYBRID_LOG,
                "4": HDR10_PLUS,
                "F": NONE,
            },
        ),
        CS20221: MapParameter(
            size=1,
            read={
                "0": SDR,
                "1": HDR,
                "2": SMPTE_ST_2084,
                "3": HYBRID_LOG,
                "4": HDR10_PLUS,
            },
        ),
        CS20191: MapParameter(
            size=1,
            read={
                "0": SDR,
                "1": HDR,
                "2": SMPTE_ST_2084,
                "3": HYBRID_LOG,
                "F": NONE,
            },
        ),
        CS20172: MapParameter(
            size=1,
            read={
                "0": SDR,
                "1": HDR,
                "2": SMPTE_ST_2084,
                "F": NONE,
            },
        ),
    }


class HdrLevel(Command):
    """HDR Level  (HDR Quantizer) adjustment command."""

    code = "PMHL"
    reference = True
    operation = True

    AUTO = "auto"
    AUTO_WIDE = "auto-wide"
    V_M2 = "-2"
    V_M1 = "-1"
    V_0 = "0"
    V_1 = "1"
    V_2 = "2"

    parameter = {
        (CS20241, CS20242, CS20221): MapParameter(
            size=1,
            readwrite={
                "0": AUTO,
                "1": V_M2,
                "2": V_M1,
                "3": V_0,
                "4": V_1,
                "5": V_2,
                "6": AUTO_WIDE,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "0": AUTO,
                "1": V_M2,
                "2": V_M1,
                "3": V_0,
                "4": V_1,
                "5": V_2,
            },
        ),
    }


class HdrProcessing(Command):
    """HDR Processing command."""

    code = "PMHP"
    reference = True
    operation = True
    depends = {Hdr: (Hdr.HDR, Hdr.HDR10_PLUS, Hdr.HYBRID_LOG, Hdr.SMPTE_ST_2084)}

    HDR10_PLUS = "hdr10+"
    STATIC = "static"
    FRAME_BY_FRAME = "frame-by-frame"
    SCENE_BY_SCENE = "scene-by-scene"

    parameter = {
        (CS20241, CS20242): MapParameter(
            size=1,
            read={
                "0": HDR10_PLUS,
                "1": STATIC,
                "2": FRAME_BY_FRAME,
                "3": SCENE_BY_SCENE,
            },
            write={
                "1": STATIC,
                "2": FRAME_BY_FRAME,
                "3": SCENE_BY_SCENE,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "0": HDR10_PLUS,
                "1": STATIC,
                "2": FRAME_BY_FRAME,
                "3": SCENE_BY_SCENE,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "1": STATIC,
                "2": FRAME_BY_FRAME,
                "3": SCENE_BY_SCENE,
            },
        ),
    }


class ContentType(Command):
    """Content Type command."""

    code = "PMCT"
    reference = True
    operation = True

    AUTO = "auto"
    SDR = "sdr"
    HDR10_PLUS = "hdr10+"
    HDR10 = "hdr10"
    HLG = "hlg"

    parameter = {
        (CS20241, CS20242, CS20221): MapParameter(
            size=1,
            readwrite={
                "0": AUTO,
                "1": SDR,
                "2": HDR10_PLUS,
                "3": HDR10,
                "4": HLG,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "0": AUTO,
                "1": SDR,
                "3": HDR10,
                "4": HLG,
            },
        ),
    }


class TheaterOptimizer(Command):
    """Theater Optimizer command."""

    code = "PMNM"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        (CS20241, CS20221, CS20191): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
    }


class TheaterOptimizerLevel(Command):
    """Theater Optimizer Level command."""

    code = "PMNL"
    reference = True
    operation = True

    AUTO = "auto"
    AUTO_WIDE = "auto-wide"
    HIGH = "high"
    LOW = "low"
    MID = "mid"
    RESERVED = "reserved"
    V_M2 = "-2"
    V_M1 = "-1"
    V_0 = "0"
    V_1 = "1"
    V_2 = "2"

    parameter = {
        (CS20241, CS20221): MapParameter(
            size=1,
            readwrite={
                "0": AUTO,
                "1": V_M2,
                "2": V_M1,
                "3": V_0,
                "4": V_1,
                "5": V_2,
                "6": AUTO_WIDE,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "0": RESERVED,
                "1": LOW,
                "2": MID,
                "3": HIGH,
            },
        ),
    }


class TheaterOptimizerProcessing(Command):
    """Theater Optimizer Processing command."""

    code = "PMNP"
    reference = True
    operation = True

    OFF = "off"
    START = "start"

    parameter = {
        (CS20241, CS20221, CS20191): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": START,
            },
        ),
    }


class DeepBlack(Command):
    """Deep Black command."""

    code = "PMBK"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
    }


class HighlightColor(Command):
    """Highlight Color command."""

    code = "PMBE"
    reference = True
    operation = True

    LOW = "low"
    MID = "mid"
    HIGH = "high"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "0": LOW,
                "1": MID,
                "2": HIGH,
            },
        ),
    }


class HdmiInputLevel(Command):
    """HDMI Input Level command."""

    code = "ISIL"
    reference = True
    operation = True

    STANDARD = "standard"
    ENHANCED = "enhanced"
    SUPER_WHITE = "super-white"
    AUTO = "auto"

    parameter = MapParameter(
        size=1,
        readwrite={
            "0": STANDARD,
            "1": ENHANCED,
            "2": SUPER_WHITE,
            "3": AUTO,
        },
    )


class HdmiColorSpace(Command):
    """HDMI Color Space switch command."""

    code = "ISHS"
    reference = True
    operation = True

    AUTO = "auto"
    YCBCR_444 = "ycbcr-444"
    YCBCR_422 = "ycbcr-422"
    RGB = "rgb"

    parameter = MapParameter(
        size=1,
        readwrite={
            "0": AUTO,
            "1": YCBCR_444,
            "2": YCBCR_422,
            "3": RGB,
        },
    )


class Aspect(Command):
    """Aspect command."""

    code = "ISAS"
    reference = True
    operation = True

    A43 = "4:3"
    A169 = "16:9"
    ZOOM = "zoom"
    AUTO = "auto"
    JUST = "just"
    FULL = "full"
    NATIVE = "native"

    parameter = {
        (CS20241, CS20242, CS20221, CS20191): MapParameter(
            size=1,
            readwrite={
                "2": ZOOM,
                "3": AUTO,
                "4": NATIVE,
            },
        ),
        CS20172: MapParameter(
            size=1,
            readwrite={
                "2": ZOOM,
                "3": AUTO,
                "4": JUST,
            },
        ),
        CS20171: MapParameter(
            size=1,
            readwrite={
                "0": A43,
                "1": A169,
                "2": ZOOM,
            },
        ),
        (CS20161, CS20141, CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": A43,
                "1": A169,
                "2": ZOOM,
                "3": AUTO,
                "4": JUST,
                "5": FULL,
            },
        ),
    }


class Hdmi2D3D(Command):
    """HDMI 2D/3D switch command."""

    code = "IS3D"
    reference = True
    operation = True

    TWO_D = "2d"
    AUTO = "auto"
    SIDE_BY_SIDE = "side-by-side"
    TOP_AND_BOTTOM = "top-and-bottom"

    parameter = MapParameter(
        size=1,
        readwrite={
            "0": TWO_D,
            "1": AUTO,
            "3": SIDE_BY_SIDE,
            "4": TOP_AND_BOTTOM,
        },
    )


class Mask(Command):
    """Mask command. TODO: Add numeric top, bottom, left, right values"""

    code = "ISMA"
    reference = True
    operation = True

    CUSTOM = "custom"
    CUSTOM_1 = "custom-1"
    CUSTOM_2 = "custom-2"
    CUSTOM_3 = "custom-3"
    OFF = "off"
    ON = "on"
    P2_5 = "2.5%"
    P5 = "5%"

    parameter = {
        (CS20241, CS20242, CS20221, CS20191, CS20172): MapParameter(
            size=1,
            readwrite={
                "1": ON,
                "2": OFF,
            },
        ),
        (CS20171, CS20161): MapParameter(
            size=1,
            readwrite={
                "0": CUSTOM_1,
                "1": CUSTOM_2,
                "2": OFF,
                "3": CUSTOM_3,
            },
        ),
        (CS20141, CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": P2_5,
                "1": P5,
                "2": OFF,
                "3": CUSTOM,
            },
        ),
    }


class PictureModeHdr10(Command):
    """HDR10 Picture Mode command."""

    code = "ISHD"
    reference = True
    operation = True

    HDR10 = "hdr10"
    USER_4 = "user-4"
    USER_5 = "user-5"
    USER_6 = "user-6"
    FRAME_ADAPT_HDR = "frame-adapt-hdr"
    FRAME_ADAPT_HDR2 = "frame-adapt-hdr2"
    FRAME_ADAPT_HDR3 = "frame-adapt-hdr3"
    HDR10_LL = "hdr10-ll"
    PANA_PQ = "pana-pq"
    LAST_SETTING = "last-setting"
    HDR1 = "hdr1"
    HDR2 = "hdr2"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "1": HDR10,
                "5": USER_4,
                "6": USER_5,
                "7": USER_6,
                "8": FRAME_ADAPT_HDR,
                "C": FRAME_ADAPT_HDR2,
                "D": FRAME_ADAPT_HDR3,
                "E": HDR10_LL,
                "F": LAST_SETTING,
            },
        ),
        CS20242: MapParameter(
            size=1,
            readwrite={
                "4": HDR1,
                "5": HDR2,
                "8": FRAME_ADAPT_HDR,
                "C": FRAME_ADAPT_HDR2,
                "F": LAST_SETTING,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "1": HDR10,
                "5": USER_4,
                "6": USER_5,
                "7": USER_6,
                "8": FRAME_ADAPT_HDR,
                "9": PANA_PQ,
                "C": FRAME_ADAPT_HDR2,
                "D": FRAME_ADAPT_HDR3,
                "F": LAST_SETTING,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "1": HDR10,
                "5": USER_4,
                "6": USER_5,
                "7": USER_6,
                "8": FRAME_ADAPT_HDR,
                "9": PANA_PQ,
                "F": LAST_SETTING,
            },
        ),
    }


class PictureModeHlg(Command):
    """HLG Picture Mode command."""

    code = "ISHL"
    reference = True
    operation = True

    HLG = "hlg"
    HLG_LL = "hlg-ll"
    LAST_SETTING = "last-setting"
    USER_4 = "user-4"
    USER_5 = "user-5"
    USER_6 = "user-6"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "1": HLG,
                "5": USER_4,
                "6": USER_5,
                "7": USER_6,
                "9": HLG_LL,
                "F": LAST_SETTING,
            },
        ),
        (CS20221, CS20191): MapParameter(
            size=1,
            readwrite={
                "1": HLG,
                "5": USER_4,
                "6": USER_5,
                "7": USER_6,
                "F": LAST_SETTING,
            },
        ),
    }


class PictureModeSdr(Command):
    """SDR Picture Mode command."""

    code = "ISS2"
    reference = True
    operation = True

    NATURAL = "natural"
    USER_1 = "user-1"
    USER_2 = "user-2"
    USER_3 = "user-3"
    CINEMA = "cinema"
    FILM = "film"
    NATURAL_LL = "natural-ll"
    VIVID = "vivid"
    THX = "thx"
    LAST_SETTING = "last-setting"
    SDR_1 = "sdr-1"
    SDR_2 = "sdr-2"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": USER_1,
                "3": USER_2,
                "4": USER_3,
                "8": CINEMA,
                "9": FILM,
                "D": NATURAL_LL,
                "E": VIVID,
                "F": LAST_SETTING,
            },
        ),
        CS20242: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": SDR_1,
                "3": SDR_2,
                "8": CINEMA,
                "E": VIVID,
                "F": LAST_SETTING,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": USER_1,
                "3": USER_2,
                "4": USER_3,
                "8": CINEMA,
                "9": (FILM, B5A1, B5A2),
                "F": LAST_SETTING,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": USER_1,
                "3": USER_2,
                "4": USER_3,
                "8": CINEMA,
                "9": FILM,
                "E": THX,
                "F": LAST_SETTING,
            },
        ),
    }


class PictureModeSdr3d(Command):
    """SDR(3D) Picture Mode command."""

    code = "ISS3"
    reference = True
    operation = True

    NATURAL = "natural"
    USER_1 = "user-1"
    USER_2 = "user-2"
    USER_3 = "user-3"
    CINEMA = "cinema"
    FILM = "film"
    NATURAL_LL = "natural-ll"
    VIVID = "vivid"
    THX = "thx"
    LAST_SETTING = "last-setting"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": USER_1,
                "3": USER_2,
                "4": USER_3,
                "8": CINEMA,
                "9": FILM,
                "D": NATURAL_LL,
                "E": VIVID,
                "F": LAST_SETTING,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": USER_1,
                "3": USER_2,
                "4": USER_3,
                "8": CINEMA,
                "9": (FILM, B5A1, B5A2),
                "F": LAST_SETTING,
            },
        ),
        CS20191: MapParameter(
            size=1,
            readwrite={
                "1": NATURAL,
                "2": USER_1,
                "3": USER_2,
                "4": USER_3,
                "8": CINEMA,
                "9": FILM,
                "E": THX,
                "F": LAST_SETTING,
            },
        ),
    }


class FilmmakerMode(Command):
    """Filmmaker Mode command."""

    code = "ISFS"
    reference = True
    operation = True

    AUTO = "auto"
    MANUAL = "manual"

    parameter = {
        (CS20241, CS20242, CS20221): MapParameter(
            size=1,
            readwrite={
                "0": MANUAL,
                "1": AUTO,
            },
        ),
    }


class LowLatencyMode(Command):
    """Low Latency Mode command."""

    code = "PMLL"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        (CS20241, CS20221, CS20191, CS20172, CS20171): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
    }


class LowLatencyAutoMode(Command):
    """ALLM (Auto Low Latency Mode) command."""

    code = "ISAL"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        CS20241: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
    }


class DynamicControl(Command):
    """Dynamic Control command (Dynamic CTRL / CMS Display Color)."""

    code = "PMDC"
    reference = True
    operation = True
    depends = {LowLatencyMode: LowLatencyMode.OFF}

    BALANCED = "balanced"
    HIGH = "high"
    LOW = "low"
    MODE_1 = "mode-1"
    MODE_2 = "mode-2"
    MODE_3 = "mode-3"
    OFF = "off"

    parameter = {
        (CS20241, CS20242): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": LOW,
                "2": HIGH,
                "3": BALANCED,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "0": (OFF, B5A1, B5A2, B5A3),
                "1": (MODE_1, B5A1, B5A2, B5A3),
                "2": (MODE_2, B5A1, B5A2, B5A3),
                "3": (MODE_3, B5A1, B5A2, B5A3),
            },
        ),
        CS20172: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": MODE_1,
                "2": MODE_2,
            },
        ),
    }


class ClearMotionDrive(Command):
    """Clear Motion Drive command."""

    code = "PMCM"
    reference = True
    operation = True
    depends = {LowLatencyMode: LowLatencyMode.OFF}

    OFF = "off"
    LOW = "low"
    HIGH = "high"
    INVERSE_TELECINE = "inverse-telecine"

    parameter = {
        (
            CS20241,
            CS20221,
            CS20191,
            CS20172,
            CS20171,
            CS20161,
            CS20141,
            CS20131,
            CS20121,
        ): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "3": LOW,
                "4": HIGH,
                "5": INVERSE_TELECINE,
            },
        ),
        CS20242: MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "6": HIGH,
                "7": LOW,
            },
        ),
    }


class InstallationMode(Command):
    """Installation Mode command."""

    code = "INML"
    reference = True
    operation = True
    operation_timeout = 30

    MEMORY_1 = "memory-1"
    MEMORY_2 = "memory-2"
    MEMORY_3 = "memory-3"
    MEMORY_4 = "memory-4"
    MEMORY_5 = "memory-5"
    MEMORY_6 = "memory-6"
    MEMORY_7 = "memory-7"
    MEMORY_8 = "memory-8"
    MEMORY_9 = "memory-9"
    MEMORY_10 = "memory-10"

    parameter = {
        (CS20241, CS20221, CS20191, CS20172): MapParameter(
            size=1,
            readwrite={
                "0": MEMORY_1,
                "1": MEMORY_2,
                "2": MEMORY_3,
                "3": MEMORY_4,
                "4": MEMORY_5,
                "5": MEMORY_6,
                "6": MEMORY_7,
                "7": MEMORY_8,
                "8": MEMORY_9,
                "9": MEMORY_10,
            },
        ),
        CS20242: MapParameter(
            size=1,
            readwrite={
                "0": MEMORY_1,
                "1": MEMORY_2,
                "2": MEMORY_3,
                "3": MEMORY_4,
                "4": MEMORY_5,
            },
        ),
        CS20171: MapParameter(
            size=1,
            readwrite={
                "0": MEMORY_1,
                "1": MEMORY_2,
                "2": MEMORY_3,
                "3": MEMORY_4,
                "4": MEMORY_5,
                "5": (MEMORY_6, XHR3),
                "6": (MEMORY_7, XHR3),
                "7": (MEMORY_8, XHR3),
                "8": (MEMORY_9, XHR3),
                "9": (MEMORY_10, XHR3),
            },
        ),
        CS20161: MapParameter(
            size=1,
            readwrite={
                "0": MEMORY_1,
                "1": MEMORY_2,
                "2": MEMORY_3,
                "3": MEMORY_4,
                "4": MEMORY_5,
                "5": (MEMORY_6, XHP3),
                "6": (MEMORY_7, XHP3),
                "7": (MEMORY_8, XHP3),
                "8": (MEMORY_9, XHP3),
                "9": (MEMORY_10, XHP3),
            },
        ),
        CS20141: MapParameter(
            size=1,
            readwrite={
                "0": MEMORY_1,
                "1": MEMORY_2,
                "2": MEMORY_3,
                "3": MEMORY_4,
                "4": MEMORY_5,
                "5": (MEMORY_6, XHK3),
                "6": (MEMORY_7, XHK3),
                "7": (MEMORY_8, XHK3),
                "8": (MEMORY_9, XHK3),
                "9": (MEMORY_10, XHK3),
            },
        ),
        (CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": MEMORY_1,
                "1": MEMORY_2,
                "2": MEMORY_3,
            },
        ),
    }


class Trigger(Command):
    """Trigger command."""

    code = "FUTR"
    reference = True
    operation = True

    OFF = "off"
    POWER = "power"
    ANAMORPHIC = "anamorphic"
    INSTALLATION_1 = "installation-1"
    INSTALLATION_2 = "installation-2"
    INSTALLATION_3 = "installation-3"
    INSTALLATION_4 = "installation-4"
    INSTALLATION_5 = "installation-5"
    INSTALLATION_6 = "installation-6"
    INSTALLATION_7 = "installation-7"
    INSTALLATION_8 = "installation-8"
    INSTALLATION_9 = "installation-9"
    INSTALLATION_10 = "installation-10"

    parameter = {
        (CS20241, CS20221, CS20191, CS20172): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": POWER,
                "2": ANAMORPHIC,
                "3": INSTALLATION_1,
                "4": INSTALLATION_2,
                "5": INSTALLATION_3,
                "6": INSTALLATION_4,
                "7": INSTALLATION_5,
                "8": INSTALLATION_6,
                "9": INSTALLATION_7,
                "A": INSTALLATION_8,
                "B": INSTALLATION_9,
                "C": INSTALLATION_10,
            },
        ),
        (CS20171, CS20161, CS20141, CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": POWER,
                "2": ANAMORPHIC,
            },
        ),
    }


class OffTimer(Command):
    """Off Timer switch command."""

    code = "FUOT"
    reference = True
    operation = True

    OFF = "off"
    HOUR_1 = "1-hour"
    HOUR_2 = "2-hours"
    HOUR_3 = "3-hours"
    HOUR_4 = "4-hours"

    parameter = MapParameter(
        size=1,
        readwrite={
            "0": OFF,
            "1": HOUR_1,
            "2": HOUR_2,
            "3": HOUR_3,
            "4": HOUR_4,
        },
    )


class EcoMode(Command):
    """Eco Mode command."""

    code = "FUEM"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = MapParameter(
        size=1,
        readwrite={
            "0": OFF,
            "1": ON,
        },
    )


class HideEco(Command):
    """Hide Eco command."""

    code = "FUHE"
    reference = True
    operation = True

    OFF = "off"
    ON = "on"

    parameter = {
        (CS20241, CS20242, CS20172): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": ON,
            },
        ),
        CS20221: MapParameter(
            size=1,
            readwrite={
                "0": (OFF, B5A1, B5A2, B5A3),
                "1": (ON, B5A1, B5A2, B5A3),
            },
        ),
    }


class Source(Command):
    """Signal (Source) command."""

    code = "IFIS"
    reference = True
    operation = False

    FWXGA_1366X768 = "fwxga-1366x768"
    NO_SIGNAL = "no-signal"
    OUT_OF_RANGE = "out-of-range"
    QXGA = "qxga"
    SVGA_800X600 = "svga-800x600"
    SXGA_1280X1024 = "sxga-1280x1024"
    UXGA_1600X1200 = "uxga-1600x1200"
    VGA_640X480 = "vga-640x480"
    R1080I_3D = "1080i-3d"
    R1080I_50 = "1080i-50"
    R1080I_60 = "1080i-60"
    R1080P_100 = "1080p-100"
    R1080P_120 = "1080p-120"
    R1080P_24 = "1080p-24"
    R1080P_25 = "1080p-25"
    R1080P_30 = "1080p-30"
    R1080P_3D = "1080p-3d"
    R1080P_50 = "1080p-50"
    R1080P_60 = "1080p-60"
    R2048X1080_P24 = "2048x1080-p24"
    R2048X1080_P25 = "2048x1080-p25"
    R2048X1080_P30 = "2048x1080-p30"
    R2048X1080_P50 = "2048x1080-p50"
    R2048X1080_P60 = "2048x1080-p60"
    R3840X1080_P50 = "3840x1080-p50"
    R3840X1080_P60 = "3840x1080-p60"
    R3840X2160_100HZ = "3840x2160-100hz"
    R3840X2160_P120 = "3840x2160-p120"
    R4096X2160_100HZ = "4096x2160-100hz"
    R4096X2160_P120 = "4096x2160-p120"
    R480I = "480i"
    R480P = "480p"
    R4K = "4k"
    R4K_3840_24 = "4k-3840-24"
    R4K_3840_25 = "4k-3840-25"
    R4K_3840_30 = "4k-3840-30"
    R4K_3840_50 = "4k-3840-50"
    R4K_3840_60 = "4k-3840-60"
    R4K_4096_24 = "4k-4096-24"
    R4K_4096_25 = "4k-4096-25"
    R4K_4096_30 = "4k-4096-30"
    R4K_4096_50 = "4k-4096-50"
    R4K_4096_60 = "4k-4096-60"
    R576I = "576i"
    R576P = "576p"
    R720P_3D = "720p-3d"
    R720P_50 = "720p-50"
    R720P_60 = "720p-60"
    R8K_7680X4320_24 = "8k-7680x4320-24"
    R8K_7680X4320_25 = "8k-7680x4320-25"
    R8K_7680X4320_30 = "8k-7680x4320-30"
    R8K_7680X4320_48 = "8k-7680x4320-48"
    R8K_7680X4320_50 = "8k-7680x4320-50"
    R8K_7680X4320_60 = "8k-7680x4320-60"
    WQHD_120 = "wqhd-120"
    WQHD_60 = "wqhd-60"
    WQXGA = "wqxga"
    WSXGA_PLUS_1680X1050 = "wsxga+1680x1050"
    WUXGA_1920X1200 = "wuxga-1920x1200"
    WXGA_1280X768 = "wxga-1280x768"
    WXGA_1280X800 = "wxga-1280x800"
    WXGA_PLUS_1440X900 = "wxga+1440x900"
    WXGA_PLUS_PLUS_1600X900 = "wxga++1600x900"
    XGA_1024X768 = "xga-1024x768"

    parameter = {
        (CS20241, CS20221): MapParameter(
            size=2,
            read={
                "02": R480P,
                "03": R576P,
                "04": R720P_50,
                "05": R720P_60,
                "06": R1080I_50,
                "07": R1080I_60,
                "08": R1080P_24,
                "09": R1080P_50,
                "0A": R1080P_60,
                "0B": NO_SIGNAL,
                "0C": R720P_3D,
                "0D": R1080I_3D,
                "0E": R1080P_3D,
                "0F": OUT_OF_RANGE,
                "10": R4K_4096_60,
                "11": R4K_4096_50,
                "12": R4K_4096_30,
                "13": R4K_4096_25,
                "14": R4K_4096_24,
                "15": R4K_3840_60,
                "16": R4K_3840_50,
                "17": R4K_3840_30,
                "18": R4K_3840_25,
                "19": R4K_3840_24,
                "1C": R1080P_25,
                "1D": R1080P_30,
                "1E": R2048X1080_P24,
                "1F": R2048X1080_P25,
                "20": R2048X1080_P30,
                "21": R2048X1080_P50,
                "22": R2048X1080_P60,
                "23": R3840X2160_P120,
                "24": R4096X2160_P120,
                "25": VGA_640X480,
                "26": SVGA_800X600,
                "27": XGA_1024X768,
                "28": SXGA_1280X1024,
                "29": WXGA_1280X768,
                "2A": WXGA_PLUS_1440X900,
                "2B": WSXGA_PLUS_1680X1050,
                "2C": WUXGA_1920X1200,
                "2D": WXGA_1280X800,
                "2E": FWXGA_1366X768,
                "2F": WXGA_PLUS_PLUS_1600X900,
                "30": UXGA_1600X1200,
                "31": QXGA,
                "32": WQXGA,
                "34": R4096X2160_100HZ,
                "35": R3840X2160_100HZ,
                "36": R1080P_100,
                "37": R1080P_120,
                "38": R8K_7680X4320_60,
                "39": R8K_7680X4320_50,
                "3A": R8K_7680X4320_30,
                "3B": R8K_7680X4320_25,
                "3C": R8K_7680X4320_24,
                "3D": WQHD_60,
                "3E": WQHD_120,
                "3F": R8K_7680X4320_48,
            },
        ),
        CS20242: MapParameter(
            size=2,
            read={
                "02": R480P,
                "03": R576P,
                "04": R720P_50,
                "05": R720P_60,
                "08": R1080P_24,
                "09": R1080P_50,
                "0A": R1080P_60,
                "0B": NO_SIGNAL,
                "0F": OUT_OF_RANGE,
                "10": R4K_4096_60,
                "11": R4K_4096_50,
                "12": R4K_4096_30,
                "13": R4K_4096_25,
                "14": R4K_4096_24,
                "15": R4K_3840_60,
                "16": R4K_3840_50,
                "17": R4K_3840_30,
                "18": R4K_3840_25,
                "19": R4K_3840_24,
                "1C": R1080P_25,
                "1D": R1080P_30,
                "1E": R2048X1080_P24,
                "1F": R2048X1080_P25,
                "20": R2048X1080_P30,
                "21": R2048X1080_P50,
                "22": R2048X1080_P60,
                "25": VGA_640X480,
                "26": SVGA_800X600,
                "2C": WUXGA_1920X1200,
                "30": UXGA_1600X1200,
                "31": QXGA,
                "3D": WQHD_60,
            },
        ),
        CS20191: MapParameter(
            size=2,
            read={
                "02": R480P,
                "03": R576P,
                "04": R720P_50,
                "05": R720P_60,
                "06": R1080I_50,
                "07": R1080I_60,
                "08": R1080P_24,
                "09": R1080P_50,
                "0A": R1080P_60,
                "0B": NO_SIGNAL,
                "0C": R720P_3D,
                "0D": R1080I_3D,
                "0E": R1080P_3D,
                "0F": OUT_OF_RANGE,
                "10": R4K_4096_60,
                "11": R4K_4096_50,
                "12": R4K_4096_30,
                "13": R4K_4096_25,
                "14": R4K_4096_24,
                "15": R4K_3840_60,
                "16": R4K_3840_50,
                "17": R4K_3840_30,
                "18": R4K_3840_25,
                "19": R4K_3840_24,
                "1C": R1080P_25,
                "1D": R1080P_30,
                "1E": R2048X1080_P24,
                "1F": R2048X1080_P25,
                "20": R2048X1080_P30,
                "21": R2048X1080_P50,
                "22": R2048X1080_P60,
                "23": R3840X2160_P120,
                "24": R4096X2160_P120,
                "25": VGA_640X480,
                "26": SVGA_800X600,
                "27": XGA_1024X768,
                "28": SXGA_1280X1024,
                "29": WXGA_1280X768,
                "2A": WXGA_PLUS_1440X900,
                "2B": WSXGA_PLUS_1680X1050,
                "2C": WUXGA_1920X1200,
                "2D": WXGA_1280X800,
                "2E": FWXGA_1366X768,
                "2F": WXGA_PLUS_PLUS_1600X900,
                "30": UXGA_1600X1200,
                "31": QXGA,
                "32": WQXGA,
            },
        ),
        CS20172: MapParameter(
            size=2,
            read={
                "02": R480P,
                "03": R576P,
                "04": R720P_50,
                "05": R720P_60,
                "06": R1080I_50,
                "07": R1080I_60,
                "08": R1080P_24,
                "09": R1080P_50,
                "0A": R1080P_60,
                "0B": NO_SIGNAL,
                "0C": R720P_3D,
                "0D": R1080I_3D,
                "0E": R1080P_3D,
                "0F": OUT_OF_RANGE,
                "10": R4K_4096_60,
                "11": R4K_4096_50,
                "12": R4K_4096_30,
                "13": R4K_4096_25,
                "14": R4K_4096_24,
                "15": R4K_3840_60,
                "16": R4K_3840_50,
                "17": R4K_3840_30,
                "18": R4K_3840_25,
                "19": R4K_3840_24,
                "1C": R1080P_25,
                "1D": R1080P_30,
                "1E": R2048X1080_P24,
                "1F": R2048X1080_P25,
                "20": R2048X1080_P30,
                "21": R2048X1080_P50,
                "22": R2048X1080_P60,
                "23": R3840X2160_P120,
                "24": R4096X2160_P120,
            },
        ),
        CS20171: MapParameter(
            size=2,
            read={
                "02": R480P,
                "03": R576P,
                "04": R720P_50,
                "05": R720P_60,
                "06": R1080I_50,
                "07": R1080I_60,
                "08": R1080P_24,
                "09": R1080P_50,
                "0A": R1080P_60,
                "0B": NO_SIGNAL,
                "0C": R720P_3D,
                "0D": R1080I_3D,
                "0E": R1080P_3D,
                "10": R4K_4096_60,
                "11": R4K_4096_50,
                "12": R4K_4096_30,
                "13": R4K_4096_25,
                "14": R4K_4096_24,
                "15": R4K_3840_60,
                "16": R4K_3840_50,
                "17": R4K_3840_30,
                "18": R4K_3840_25,
                "19": R4K_3840_24,
                "1A": R3840X1080_P50,
                "1B": R3840X1080_P60,
                "1C": R1080P_25,
                "1D": R1080P_30,
            },
        ),
        CS20161: MapParameter(
            size=2,
            read={
                "02": R480P,
                "03": R576P,
                "04": R720P_50,
                "05": R720P_60,
                "06": R1080I_50,
                "07": R1080I_60,
                "08": R1080P_24,
                "09": R1080P_50,
                "0A": R1080P_60,
                "0B": NO_SIGNAL,
                "0C": R720P_3D,
                "0D": R1080I_3D,
                "0E": R1080P_3D,
                "10": R4K_4096_60,
                "11": R4K_4096_50,
                "12": R4K_4096_30,
                "13": R4K_4096_25,
                "14": R4K_4096_24,
                "15": R4K_3840_60,
                "16": R4K_3840_50,
                "17": R4K_3840_30,
                "18": R4K_3840_25,
                "19": R4K_3840_24,
            },
        ),
        CS20141: MapParameter(
            size=1,
            read={
                "0": R480I,
                "1": R576I,
                "2": R480P,
                "3": R576P,
                "4": R720P_50,
                "5": R720P_60,
                "6": R1080I_50,
                "7": R1080I_60,
                "8": R1080P_24,
                "9": R1080P_50,
                "A": R1080P_60,
                "B": NO_SIGNAL,
                "C": R720P_3D,
                "D": R1080I_3D,
                "E": R1080P_3D,
                "F": R4K,
            },
        ),
        (CS20131, CS20121): MapParameter(
            size=1,
            read={
                "0": R480I,
                "1": R576I,
                "2": R480P,
                "3": R576P,
                "4": R720P_50,
                "5": R720P_60,
                "6": R1080I_50,
                "7": R1080I_60,
                "8": R1080P_24,
                "9": R1080P_50,
                "A": R1080P_60,
                "B": NO_SIGNAL,
                "C": R720P_3D,
                "D": R1080I_3D,
                "E": R1080P_3D,
            },
        ),
    }


class ColorDepth(Command):
    """Color Depth (Deep Color) command."""

    code = "IFDC"
    reference = True
    operation = False

    BIT_8 = "8-bit"
    BIT_10 = "10-bit"
    BIT_12 = "12-bit"

    parameter = MapParameter(
        size=1,
        read={
            "0": BIT_8,
            "1": BIT_10,
            "2": BIT_12,
        },
    )


class ColorSpace(Command):
    """Color Space Display command."""

    code = "IFXV"
    reference = True
    operation = False

    RGB = "rgb"
    YCBCR_422 = "ycbcr-422"
    YCBCR_444 = "ycbcr-444"
    YCBCR_420 = "ycbcr-420"
    YUV = "yuv"
    XV_COLOR = "xv-color"

    parameter = {
        (CS20241, CS20242, CS20221): MapParameter(
            size=1,
            read={
                "0": RGB,
                "1": YCBCR_422,
                "2": YCBCR_444,
                "3": YCBCR_420,
            },
        ),
        (CS20191, CS20172): MapParameter(
            size=1,
            read={
                "0": RGB,
                "1": YUV,
            },
        ),
        (CS20171, CS20161, CS20141): MapParameter(
            size=1,
            read={
                "0": RGB,
                "1": YUV,
                "2": XV_COLOR,
            },
        ),
    }


class LightTime(Command):
    """Light Time (Lamp/Laser) command."""

    code = "IFLT"
    reference = True
    operation = False
    parameter = LightTimeParameter()


class Colorimetry(Command):
    """Colorimetry command."""

    code = "IFCM"
    reference = True
    operation = False

    NO_DATA = "no-data"
    BT_601 = "bt-601"
    BT_709 = "bt-709"
    XV_YCC_601 = "xvycc-601"
    XV_YCC_709 = "xvycc-709"
    S_YCC_601 = "sycc-601"
    ADOBE_YCC_601 = "adobe-ycc-601"
    ADOBE_RGB = "adobe-rgb"
    BT_2020_CONSTANT_LUMINANCE = "bt-2020-constant-luminance"
    BT_2020_NON_CONSTANT_LUMINANCE = "bt-2020-non-constant-luminance"
    S_RGB = "srgb"
    OTHER = "other"
    DCI_P3_D65 = "dci-p3-d65"
    DCI_P3_THEATER = "dci-p3-theater"

    parameter = {
        (CS20241, CS20242, CS20221): MapParameter(
            size=1,
            read={
                "0": NO_DATA,
                "1": BT_601,
                "2": BT_709,
                "3": XV_YCC_601,
                "4": XV_YCC_709,
                "5": S_YCC_601,
                "6": ADOBE_YCC_601,
                "7": ADOBE_RGB,
                "8": BT_2020_CONSTANT_LUMINANCE,
                "9": BT_2020_NON_CONSTANT_LUMINANCE,
                "A": S_RGB,
                "B": DCI_P3_D65,
                "C": DCI_P3_THEATER,
            },
        ),
        CS20191: MapParameter(
            size=1,
            read={
                "0": NO_DATA,
                "1": BT_601,
                "2": BT_709,
                "3": XV_YCC_601,
                "4": XV_YCC_709,
                "5": S_YCC_601,
                "6": ADOBE_YCC_601,
                "7": ADOBE_RGB,
                "8": BT_2020_CONSTANT_LUMINANCE,
                "9": BT_2020_NON_CONSTANT_LUMINANCE,
                "A": S_RGB,
            },
        ),
        CS20172: MapParameter(
            size=1,
            read={
                "0": NO_DATA,
                "1": BT_601,
                "2": BT_709,
                "3": XV_YCC_601,
                "4": XV_YCC_709,
                "5": S_YCC_601,
                "6": ADOBE_YCC_601,
                "7": ADOBE_RGB,
                "8": BT_2020_CONSTANT_LUMINANCE,
                "9": BT_2020_NON_CONSTANT_LUMINANCE,
                "A": OTHER,
            },
        ),
    }


class DscMode(Command):
    """Dsc Mode command."""

    code = "IFDS"
    reference = True
    operation = False

    OFF = "off"
    ON = "on"

    parameter = {
        (CS20241, CS20221): MapParameter(
            size=1,
            read={
                "0": OFF,
                "1": ON,
            },
        )
    }


class LinkRate(Command):
    """Link Rate command."""

    code = "IFLR"
    reference = True
    operation = False

    DISABLE = "disable"
    R_3_GBPS_3_LANES = "3-gbps-3-lanes"
    R_6_GBPS_3_LANES = "6-gbps-3-lanes"
    R_6_GBPS_4_LANES = "6-gbps-4-lanes"
    R_8_GBPS_4_LANES = "8-gbps-4-lanes"
    R_10_GBPS_4_LANES = "10-gbps-4-lanes"

    parameter = {
        (CS20241, CS20242, CS20221): MapParameter(
            size=1,
            read={
                "0": DISABLE,
                "1": R_3_GBPS_3_LANES,
                "3": R_6_GBPS_3_LANES,
                "4": R_6_GBPS_4_LANES,
                "5": R_8_GBPS_4_LANES,
                "6": R_10_GBPS_4_LANES,
            },
        ),
    }


class Anamorphic(Command):
    """Anamorphic command."""

    code = "INVS"
    reference = True
    operation = True

    OFF = "off"
    A = "a"
    B = "b"
    C = "c"
    D = "d"

    parameter = {
        (CS20241, CS20242, CS20221, CS20191): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": A,
                "2": B,
                "3": C,
                "4": D,
            },
        ),
        (CS20172, CS20171, CS20161, CS20141, CS20131, CS20121): MapParameter(
            size=1,
            readwrite={
                "0": OFF,
                "1": A,
                "2": B,
            },
        ),
    }
