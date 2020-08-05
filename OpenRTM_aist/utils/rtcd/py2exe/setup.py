from distutils.core import setup
import py2exe

option = {
    "compressed": 1,
    "optimize": 2,
}

setup(
    options={"py2exe"	: option
             },
    console=[
        {"script"	: "rtcd_python.py"}
    ],
    zipfile="rtcd-lib/rtcd.zip"
)
