@echo off
setlocal enabledelayedexpansion

:: Get current directory name (e.g. SmallRain_fore)
for %%A in ("%cd%") do set "folder_name=%%~nxA"
set "output_dir=!folder_name!pre"

echo Output folder: !output_dir!

:: Create target folder if it doesn't exist
if not exist "!output_dir!" (
    mkdir "!output_dir!"
    echo Folder created: !output_dir!
)  

for %%f in (*.png) do (
    set "filename=%%~nf"
    echo Processing: %%f
   ffmpeg -i "%%f" -vf "premultiply=inplace=1" "!output_dir!\!filename!.png"
)

echo Conversion complete! All files saved to [!output_dir!] folder.
pause