REM This batch file creates a dist\functionplot directory
REM where it bundles everything this project needs.
REM PyInstaller is used for this purpose:
REM https://github.com/pyinstaller/pyinstaller

pyinstaller -w --noconfirm  ^
    --icon=desktop\functionplot.ico ^
    --noupx ^
    functionplot\functionplot.py

copy COPYING dist\functionplot\
copy AUTHORS dist\functionplot\
mkdir dist\functionplot\img
xcopy functionplot\img\* dist\functionplot\img\
copy functionplot\functionplot.glade dist\functionplot
mkdir dist\functionplot\share
xcopy "C:\Program Files\GTK2-Runtime\share\share" dist\functionplot\share\ /s
mkdir dist\functionplot\locale
xcopy mo\* dist\functionplot\locale\ /s
del dist\functionplot\tcl85.dll
del dist\functionplot\tk85.dll