### **[Disclaimer]**:

I am not an experienced developer. I am a gamer and sometimes a livestreamer who imagined an overlay for my livestream that didn't seem to exist anywhere. I learned the basics of python specifically to make this application. I would like to apologise in advance if there are any conventions or norms that I have not followed when it comes to making open-source software. I am very open to constructive criticism and feedback.

Also please forgive me if this README is a bit verbose. Scurry is intended to be used by gamers and livestreamers--who may not be coders--so I want to be sure to cover all of the basics to the best of my ability.

## Preview:
![ScurryDemo1](https://github.com/user-attachments/assets/3d64b374-7730-438a-9faf-c2f448cda3c1)
# What is Scurry?

Scurry is a python-based overlay application designed for livestreamers. I was looking for an overlay for my stream that would display my mouse movements, similar to a conrtoller or keyboard overlay (such as Nohboard, Input-Overlay, or GamePadViewer). However, it seemed like the best any of the overlays could do was draw an arrow or vector to indicate movement--whereas I wanted to see a physical sprite moving around on my screen to illustrate my mouse movements. 

Some key features of Scurry:
- Easy to use: 
    - If you download the binary release, just extract the zip folder and drop it anywhere on your pc and it will run in 1 click.
    - If you have python installed, you can also run the app straight from the source code.


- Extremely Customizeable:
    - 38 configurable parameters that can be changed to best suit your needs. All organized in a central launcher with plenty of information available for help.
    - Save and load custom configurations (profiles) to quickly switch configs for all of your different use cases.
    - Support for custom sprites and animated sprite sheets.

![ScurryDemo2](https://github.com/user-attachments/assets/464c8f61-4073-4c24-ba59-c7533d6bdad7)
# Youtube Demo:
### ***[WORK IN PROGRESS]***

# Current Limitations:
### Windows Only:
- Due to my limitations as a brand-new developer, I'm only able to guarentee stability/functionality of this software on Windows. I tried to test it in an Ubuntu VM, but I ran into some problems caused by linux sandboxing, and I don't know enough about linux to solve them, or even if they are solveable.

### IF NOT RUNNING .exe VERSION:
- Requires Python 3.12.x:
  - I originally started building the app using python 3.12.6. However, when python 3.13.0 came out recently, I tested the app out with the new interpereter, and found that some libraries don't seem to be compatible. However, I found that the app is fully compatible with Python 3.12.7 (archived).
    
  - Python Dependencies (required libraries):
     - pynput (for handling mouse input data)
     - Pygame (for rendering the graphics)
     - PyQt6 (for constructing and running the GUI)

# Installation:

### Windows binary (.exe) version:
*Beginner friendly, but you will probably have to make an exception in Windows Defender or whatever AntiVirus software you use.*
1. Navigate to the [newest release](https://github.com/Contemplaytion/Scurry-Mouse-Visualizer/releases/tag/v1.0.0-beta) page, which can be found on the right hand side of the Scurry Mouse Visualizer repository homepage.
2. Download the first item: "Scurry_Mouse_Visualizer_(version)_Binary_Release.zip". The app is fully portable, so you can extract the contents of the zip folder anywhere you would like on your PC.
    >(2.5). Windows Defender and other AntiVirus softwares will most likely flag ScurryLauncher.exe as a virus. You may need to make an exception in your AnitVirus software to run Scurry
3. Run ScurryLauncher.exe
    
### Python version:
*More advanced, but files are smaller, will not be flagged by AntiVirus, and you can view and modify the source code.*
1. Install python 3.12.x if you do not already have it installed. You can find it in the releases section of [python's official website](https://www.python.org/downloads/release/python-3127/). As mentioned earlier, you may find compatibility issues with some dependencies if you use a python version other than 3.12.x
    - Be sure to check the checkbox that says "Add python.exe to PATH." When installing. This will tell your PC where your python interpereter is installed, and will allow your PC to call the python interpereter from the command prompt to run your scripts.

2. Install dependencies (3rd party libraries). When python is installed, it also installs a "package manager" called "pip". Pip is responsible for grabbing 3rd party python packages that aren't part of the python standard library from an official repository and adding them to your local machine. Assuming python.exe was added to the PATH in step 1, then we can access pip from the command prompt:
    1. open the command prompt or windows powershell
    2. Check to see if pip was installed correctly by entering the command below:
        
            pip --version
        You should receieve a version number and a filepath as the response. If you get "'pip' is not recognized as an internal or external command, operable program, or batch file" as the output, then re-run the installer from step 1, and be absolutely sure that the "Add python.exe to PATH" checkbox is checked.
    3. Install the 3 required packages with pip by entering the command below:

            pip install pynput pygame pyqt6
    
    4. If you receive no errors, you can close the command prompt.

3. Download the contents of "Scurry_Source_Code" from the main GitHub repository (technically, you don't need the contents of "Additional_Resources," to run Scurry, though). Extract them into any desired location on your PC. It is important that you keep them in their own folder, and that you don't move or delete anything that's already inside.

### How To run Scurry using Python: 
The main script responsible for running Scurry is "ScurryLauncher.py". You will need to use the python interpereter to run it. This can be done with the command prompt:
1. Navigate to the folder you created for Scurry.
2. Open the command prompt in that specific folder. There are 2 ways to do this:
    1. On the top left of the file explorer window, click the "File" button, and select "Open Windows Powershell" fromthe dropdown menu
    
    OR
    
    2. enter either "cmd" or "powershell" into the address bar at the top of your file explorer. 
        - You can edit the address by either single clicking the white space to the right of the text, or by right clicking it and selecting "edit address". replace the highlighted text with either "cmd" or "powershell" and press enter
3. You should see a terminal window open, and you should see the current folder filepath on the left before the ">" symbol. Likewise, if you enter "dir" into the terminal, you should see a list of the files and folders inside--and one of them should be "ScurryLauncher.py". Use python to run ScurryLauncher.py by entering the command below (case-sensitive):
    
            python ScurryLauncher.py

You will need to leave the terminal open while running Scurry. Closing the terminal will also close Scurry.

# How To Contribute:

I am still learning the basics of Git and GitHub so please bear with me. I will do my best to stay up to date with discussions and issues, and would be happy to receive constructive feedback you may have for me. 

If you would like to contribute directly (bug fixes, etc), please let me know before you start working just so I know to keep an eye out. Feel free to fork the repo into another branch and submit a pull request. 

Also, feel free to submit some custom sprites, animated or otherwise! Assuming they are licensed appropriately, I might be happy to bundle them into one of the releases.

------------------
### Thanks for checking out my repo! I hope you like Scurry!


        
