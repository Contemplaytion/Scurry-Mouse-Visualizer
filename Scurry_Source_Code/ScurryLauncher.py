# PLEASE DON'T JUDGE ME--I am not a developer--this is my first app--and I did my best T_T.
# Also I KNOW that python isn't the best language for this project. I explored the possibility of using C++ but I couldn't even figure out how to get
# C++ to compile. Trying to learn C++ proved way too advanced for a noob like me. :(

#NOTE:  It seems the pynput module is not compatible with python 3.13.0. As such, I can only claim this app to work with python 3.12.x

#NOTE:  For now, I need to limit this app to WINDOWS ONLY. While I tried to design this app in a cross-plaform conscious way, 
#       I tried to run this script on an ubuntu vm and ran into problems with sandboxing, and I'm too much of a linux noob to
#       find a solution. Essentially. pynput would only track the mouse while the cursor was over the app itself, which basically breaks the whole app.

#KNOWN ISSUES: QLineEdit objects have really frustrating cursor movement mechanics. Because they call functions every time the text changes, the cursor will automatically move to the right end of the text field.

import sys
import os
import platform
import datetime
import math

import configparser
import traceback

from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

import CursorBoundaryTool
import ScurryMouseVisualizer_app as ScurryMouseVisualizer

from ConfigurationUI import Ui_formConfig

class mainUI(Ui_formConfig):
    
    def __init__(self, GUI_instance): #...really...really...long...
        #Set up GUI designed from QT Designer and compiled with pyuic6
        self.setupUi(GUI_instance)

        #define additional custom GUI properties 
        self.window_icon_filepath = "./Assets/Icon.png"
        self.icon = QIcon()
        self.icon.addPixmap(QPixmap(self.window_icon_filepath), QIcon.Mode.Normal, QIcon.State.Off)
        GUI_instance.setWindowIcon(self.icon)

        # The following are what I call object prefixes. I used them as a naming convention for GUI objects, such that it is easy to see what type of object it is from the object name alone.
        # I define these as attributes here to add them to the tab complete list and reduce the probability of a typo or bug.
        self.FORM = "form"
        self.TABWIDGET = "tabwidget"
        self.TAB = "tab"
        self.FRAME = "frame"
        self.BTN = "btn"
        self.LBL = "lbl"
        self.TXT = "txt"
        self.SPIN = "spin"
        self.DBLSPIN = "dblspin"
        self.HSLIDER = "hslider"
        self.COMBO = "combo"
        self.RADIO = "radio"
        self.CB = "cb"

        #create sets as a reference list of related objects that can be iterated over.
        self.PREFIXES = {self.FORM, self.TABWIDGET, self.TAB, self.BTN, self.LBL, self.TXT, self.SPIN, self.DBLSPIN, self.HSLIDER, self.COMBO, self.RADIO, self.CB} #for determining a significant GUI element object type given it's object name. see self.get_object_type()
        self.HEX_CHARS = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"} #for determining valid hex strings. see self.valid_hex_color()
        
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Define hard-coded default configuration. This will serve as a comprehensive list of all configuration parameters that is also frequently used as a reference.
        self.DEFAULT_CONFIG = {
            'profile_filepath' : 'ScurryConfig.ini',

            'app_window_width': 800, 
            'app_window_height' : 600, 
            'background_color' : (0, 0, 100), 
            'fps' : 60, 

            'lower_x_boundary' : 0, 
            'upper_x_boundary' : 1920, 
            'lower_y_boundary' : 0, 
            'upper_y_boundary' : 1080, 

            'centered_cursor_mode' : 1, 

            'sensitivity' : 0.15,
            'trail_lifetime' : 0.5, 
            'enable_cursor_idle_reset' : True, 
            'cursor_idle_reset' : 0.5, 
            'wrapping_mode' : False, 

            'trail_thickness' : 8, 
            'trail_sample_rate' : 250,
            'velocity_smoothing' : 3, 

            'circle_sprite_size' : 16, 
            'circle_sprite_color' : (255, 255, 255), 
            'circle_outline_size' : 2, 
            'circle_outline_color' : (0, 0, 0), 

            'use_custom_sprite' : False, 
            'custom_sprite_size' : 64, 
            'prefer_relative_filepath' : False,
            'custom_sprite_filepath' : './Assets/Default_Mouse_Sprite_Sheet.png',

            'rotate_sprite' : True,
            'animate_sprite' : True, 
            'animation_speed' : 0.4,

            'draw_mouse_sprite' : True, 
            'draw_trail_dots' : False, 
            'draw_trail_lines' : True, 

            'slow_trail_color' : (255, 0, 0), 
            'medium_fast_trail_color' : (255, 255, 0), 
            'very_fast_trail_color' : (0, 200, 0), 

            'slow_color_upper_boundary' : 30, 
            'medium_fast_color_lower_boundary' : 40, 
            'medium_fast_color_upper_boundary' : 60, 
            'very_fast_color_lower_boundary' : 80 
        }

        self.current_config = self.DEFAULT_CONFIG.copy() #self.current_config will store the currently loaded/applied configuration, and will be sent to the scurry app at launch.

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Create an attribute for each individual config parameter. Therefore each parameter is stored twice by scurry. 

            # Attribute versions of parameters will serve as a real-time modifiable version of a parameter, subject to validity checks.
            # However, the actual configuration will be stored in the self.current_config dictionary.
            # Calling self.apply() will set all values of self.current_config equal to the corresponding attribute version of the parameter.
            # Calling self.apply(reversed=True) will serve as a revert function, wherein the values of all attribute versions of parameters 
            # will be reset to the values stored in self.current_config 

            #while it is tempting to use a loop to create all of these attributes, i.e.: 
                                                                         
                #for key in self.DEFAULT_CONFIG.keys(): 
                    #setattr(self, key, self.DEFAULT_CONFIG[key]))}
            
                #...I will type them all out verbosely because:
                    #1) they will become available in the tab-complete list
                    #2) they can be used as a quick and easy reference to see the corresponding GUI elements corrrespond to which parameter

        #IMPORTANT!!! - if you plan on changing the value of a parameter and its gui corresponding gui element. change the GUI element value FIRST.
            # that way, all of the logic performed by the various callback functions associated with changing values will be executed BEFORE setting the value of a parameter.
        
        self.profile_name = "DEFAULT" #NOT IN CONFIG SETTINGS. Will be used to update the text of self.lblCurrentProfile to inform the user which profile is active. see self.config_changed()
        
        self.profile_filepath = self.DEFAULT_CONFIG['profile_filepath']
        
        self.app_window_width = self.spinW.value()
        self.app_window_height = self.spinH.value()
        self.background_color = (self.spinBackgroundR.value(),self.spinBackgroundB.value(),self.spinBackgroundG.value())
        self.fps = self.spinCustomFPS.value()

        self.lower_x_boundary = self.spinLowerX.value()
        self.upper_x_boundary = self.spinUpperX.value()
        self.lower_y_boundary = self.spinLowerY.value()
        self.upper_y_boundary = self.spinUpperY.value()

        self.centered_cursor_mode = self.comboCenteredCursorMode.currentIndex()

        self.sensitivity = self.dblspinSensitivity.value()
        self.trail_lifetime = self.dblspinTrailLifetime.value()
        self.enable_cursor_idle_reset = self.cbCursorIdleReset.isChecked()
        self.cursor_idle_reset = self.dblspinCursorIdleReset.value()
        self.wrapping_mode = bool(self.comboWrapStyle.currentIndex()) #0 = "Spawn Center" = False, and 1 = "Wrap Across" = True

        self.trail_thickness = self.spinTrailThickness.value()
        self.trail_sample_rate = self.spinTrailSampleRate.value()
        self.velocity_smoothing = self.comboVelocitySmoothing.currentIndex()

        self.circle_sprite_size = self.spinCircleSpriteSize.value()
        self.circle_sprite_color = (self.spinCircleSpriteColorR.value(), self.spinCircleSpriteColorG.value(), self.spinCircleSpriteColorB.value())
        self.circle_outline_size = self.spinCircleOutlineSize.value()
        self.circle_outline_color = (self.spinCircleOutlineColorR.value(), self.spinCircleOutlineColorG.value(), self.spinCircleOutlineColorB.value())

        self.use_custom_sprite = self.radioCustomSprite.isChecked()
        self.custom_sprite_size = self.spinCustomSpriteSize.value()
        self.prefer_relative_filepath = self.cbPreferRelativeFilepath.isChecked()        
        self.custom_sprite_filepath = self.txtCustomSpriteFilepath.text()

        self.rotate_sprite = self.cbRotateSprite.isChecked()
        self.animate_sprite = self.cbAnimateSprite.isChecked()
        self.animation_speed = self.dblspinAnimationSpeed.value()
        
        #NOT IN CONFIG PARAMETERS. See used to power custom sprite preview objects. see self.update_preview()
        self.custom_sprite_frames = [] 
        self.custom_sprite_current_frame = 0 

        self.draw_mouse_sprite = not self.radioNoSprite.isChecked()
        self.draw_trail_dots = self.radioColoredDots.isChecked()
        self.draw_trail_lines = self.radioColoredLineSegments.isChecked()

        self.slow_trail_color = (self.spinSlowR.value(), self.spinSlowG.value(), self.spinSlowB.value())
        self.medium_fast_trail_color = (self.spinMedR.value(), self.spinMedG.value(), self.spinMedB.value())
        self.very_fast_trail_color = (self.spinFastR.value(), self.spinFastG.value(), self.spinFastB.value())

        self.slow_color_upper_boundary = self.spinSlowUpper.value()
        self.medium_fast_color_lower_boundary = self.spinMedLower.value()
        self.medium_fast_color_upper_boundary = self.spinMedUpper.value()
        self.very_fast_color_lower_boundary = self.spinFastLower.value()

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Define groups of related objects:
            # ...I am very sorry for how clunky and obfuscated this part of the code has become. I started building it this way to try to make my code more efficient, 
            # but as the program became more complex it became more difficult to conceptualize--but I got myself in too deep with the idea so had to see it through.

            # I have used a naming convention when naming relavent UI elements in Qt Designer. Relevant objects have names of the format {object-prefix}{group-name}{discriminator}
            # For example, txtBackgroundHex is a textbox (line edit) object that belongs to the "Background" Group that stores the "R" value. 
            # All of the elements in the "Background" group are part of the RGB color picker for the BACKGROUND_COLOR parameter.

            # I will use these groups below to help functions implicitly decide which objects to act upon by solely looking at their object names, as opposed to
            # having to redundantly type out which objects must be acted upon. 
                
        #Create groups related to color pickers
        self.background_color_group = "Background"
        self.circle_sprite_color_group = "CircleSpriteColor"
        self.circle_outline_color_group = "CircleOutlineColor"
        self.slow_color_group = "Slow"
        self.medium_fast_color_group = "Med"
        self.very_fast_color_group = "Fast"

        #Create groups that correspond with individual preview widgets
        self.background_preview_group = "Background"
        self.custom_sprite_preview_group = "CustomSprite"
        self.circle_sprite_preview_group = "CircleSprite"
        self.trail_gradient_preview_group = "Gradient"

        # Because many of the groups have similar functions, I will organize groups together into what I will call "meta-groups," whose purpose is to store a list of related groups, 
        # Each meta group will be a dictionary, whose keys will be related group names, and values will be the configuration parameter (attribute) accociated with each group name.
        # Creating meta-groups like this gives me a way to easily parse and iterate over related groups.
       
        #Stores all groups related to color pickers as well as the attribute name of the config parameter they affect.
        self.color_groups = { 
            #format: {Group : Corresponding Config Parameter (attribute)}
            self.background_color_group : "background_color",
            self.circle_sprite_color_group : "circle_sprite_color",
            self.circle_outline_color_group : "circle_outline_color",
            self.slow_color_group : "slow_trail_color",
            self.medium_fast_color_group : "medium_fast_trail_color",
            self.very_fast_color_group : "very_fast_trail_color"
            } 
        
        #Stores all groups related to preview widgets
        self.preview_groups = { 
            #format: {Group : (self, relavant_group_1, relavant_group_2, etc)}
            self.background_preview_group : (self.background_preview_group, self.background_color_group),
            self.circle_sprite_preview_group : (self.circle_sprite_preview_group, self.circle_sprite_color_group, self.circle_outline_color_group),
            self.custom_sprite_preview_group : (self.custom_sprite_preview_group),
            self.trail_gradient_preview_group : (self.trail_gradient_preview_group, self.slow_color_group, self.medium_fast_color_group, self.very_fast_color_group)
        }

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Define event handlers:

        #Main UI buttons
        self.btnSaveProfile.clicked.connect(self.profile_save)
        self.btnApply.clicked.connect(self.config_apply)
        self.btnLoadProfile.clicked.connect(self.profile_load)
        self.btnLaunch.clicked.connect(self.launch_scurry)
        self.btnRevert.clicked.connect(self.config_revert)
        self.btnRestoreDefaults.clicked.connect(self.config_restore_defaults)

        #App Dimensions
        self.spinW.valueChanged.connect(self.update_app_dimensions)
        self.spinH.valueChanged.connect(self.update_app_dimensions)

        #set up event handler for all color pickers:
            #Background Color
            #Circle Sprite Color
            #Circle Outline Color
            #Slow Trail Color
            #Medium-Fast Trail Color
            #Very Fast Trail Color
        for group in self.color_groups.keys():
            getattr(self, self.SPIN + group + "R").valueChanged.connect(self.update_color_picker)
            getattr(self, self.SPIN + group + "G").valueChanged.connect(self.update_color_picker)
            getattr(self, self.SPIN + group + "B").valueChanged.connect(self.update_color_picker)
            getattr(self, self.TXT + group + "Hex").textChanged.connect(self.update_color_picker)

        #FPS
        self.comboFPS.currentIndexChanged.connect(self.update_fps)
        self.spinCustomFPS.valueChanged.connect(self.update_fps)

        #Cursor Boundaries
        self.comboCursorBoundaries.currentIndexChanged.connect(self.update_cursor_boundaries)
        self.spinLowerX.valueChanged.connect(self.update_cursor_boundaries)
        self.spinUpperX.valueChanged.connect(self.update_cursor_boundaries)
        self.spinLowerY.valueChanged.connect(self.update_cursor_boundaries)
        self.spinUpperY.valueChanged.connect(self.update_cursor_boundaries)

        #Centered Cursor Mode
        self.comboCenteredCursorMode.currentIndexChanged.connect(self.update_centered_cursor_mode)

        #Mouse Sensitivity
        self.dblspinSensitivity.valueChanged.connect(self.update_sens)
        self.hsliderSensitivity.valueChanged.connect(self.update_sens)

        #Trail Lifetime
        self.dblspinTrailLifetime.valueChanged.connect(self.update_trail_lifetime)

        #Cursor Idle Reset
        self.cbCursorIdleReset.checkStateChanged.connect(self.toggle_cursor_idle_reset)
        self.dblspinCursorIdleReset.valueChanged.connect(self.update_cursor_idle_reset)

        #Wrapping mode
        self.comboWrapStyle.currentIndexChanged.connect(self.update_wrapping_mode)

        #Trail Thickness
        self.spinTrailThickness.valueChanged.connect(self.update_trail_thickness)

        #Trail Sample rate
        self.comboTrailSampleRate.currentIndexChanged.connect(self.update_trail_sample_rate)
        self.spinTrailSampleRate.valueChanged.connect(self.update_trail_sample_rate)

        #Velocity Smoothing
        self.comboVelocitySmoothing.currentIndexChanged.connect(self.update_velocity_smoothing)

        #sprite tab radio buttons
        self.radioDefaultColoredCircle.toggled.connect(self.select_sprite_type)
        self.radioCustomSprite.toggled.connect(self.select_sprite_type)
        self.radioNoSprite.toggled.connect(self.select_sprite_type)

        #Circle Sprite Size
        self.spinCircleSpriteSize.valueChanged.connect(self.update_circle_sprite_properties)

        #Circle Outline Size
        self.spinCircleOutlineSize.valueChanged.connect(self.update_circle_sprite_properties)

        #Custom Mouse Sprite Requirements scrollArea
        self.vscrollRequirements.valueChanged.connect(self.scroll_label)

        #Custom Sprite Size
        self.spinCustomSpriteSize.valueChanged.connect(self.update_custom_sprite_size)
        
        #Custom Sprite Filepath
        self.txtCustomSpriteFilepath.textChanged.connect(self.update_custom_sprite_filepath)
        self.btnBrowse.clicked.connect(self.update_custom_sprite_filepath)
        self.cbPreferRelativeFilepath.checkStateChanged.connect(self.toggle_prefer_relative_filepath)

        #Animate Sprite:
        self.cbAnimateSprite.checkStateChanged.connect(self.toggle_animate_sprite)
        
        #Cycle Animated Sprite Frames:
        self.btnCycleFrames.clicked.connect(self.cycle_custom_sprite_frames)

        #Animation Speed
        self.dblspinAnimationSpeed.valueChanged.connect(self.update_animation_speed)

        #Rotate Sprite:
        self.cbRotateSprite.checkStateChanged.connect(self.toggle_rotate_sprite)

        #Draw Trail Dots
        #Draw Trail Lines
        self.radioColoredDots.toggled.connect(self.set_trail_style)
        self.radioColoredLineSegments.toggled.connect(self.set_trail_style)
        self.radioBoth.toggled.connect(self.set_trail_style)
        self.radioNoTrailEffect.toggled.connect(self.set_trail_style)   

        #Slow Color Upper Boundary
        #Medium-Fast Color Lower Boundary
        #Medium-Fast Color Upper Boundary
        #Very Fast Color Lower Boundary
        self.spinSlowUpper.valueChanged.connect(self.update_trail_gradient_boundaries)
        self.spinMedLower.valueChanged.connect(self.update_trail_gradient_boundaries)
        self.spinMedUpper.valueChanged.connect(self.update_trail_gradient_boundaries)
        self.spinFastLower.valueChanged.connect(self.update_trail_gradient_boundaries)

        # "How does this work?"" Button
        self.btnHowDoesThisWork.clicked.connect(self.show_custom_trail_color_info)

        #"Help Me Set These" Button
        self.btnHelpMeSetThese.clicked.connect(self.open_cursor_boundary_measuring_tool)

        #Scrollbar for "About" page
        self.vscrollAbout.valueChanged.connect(self.scroll_label)

        #Scrollbar for "Known Issues" page
        self.vscrollKnownIssues.valueChanged.connect(self.scroll_label)

        #Scrollbar for "License" page
        self.vscrollLicense.valueChanged.connect(self.scroll_label)

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Miscellaneous UI setup
        
        #Band-aid bug fix in which compiling UI with frame object disabled by default would not re-enable child widgets when frame was enabled
        self.frameCustomSprite.setEnabled(False)

        #Enables scrolling of the lblRequirements object. I cannot for the life of me figure out how to properly use the QScrollArea widget properly, so this is my workaround.
        #It would be really nice, however, if the user did not have to mouse-over the scrollRequirements scrollbar in order to scroll the label, but could instead mouse-over the label itself.
        self.scrollable_labels_initial_geometries = {
            self.vscrollRequirements.objectName() : (self.lblRequirements.x(), self.lblRequirements.y(), self.lblRequirements.geometry().width(), self.lblRequirements.geometry().height(), self.scrollareaRequirements.geometry().height()),
            self.vscrollAbout.objectName() : (self.lblAbout.x(), self.lblAbout.y(), self.lblAbout.geometry().width(), self.lblAbout.geometry().height(), self.scrollareaAbout.geometry().height()),
            self.vscrollKnownIssues.objectName(): (self.lblKnownIssues.x(), self.lblKnownIssues.y(), self.lblKnownIssues.geometry().width(), self.lblKnownIssues.geometry().height(), self.scrollareaKnownIssues.geometry().height()),
            self.vscrollLicense.objectName() : (self.lblLicense.x(), self.lblLicense.y(), self.lblLicense.geometry().width(), self.lblLicense.geometry().height(), self.scrollareaLicense.geometry().height())
        }

        #load initial custom sprite into preview
        self.update_preview(self.custom_sprite_preview_group)

        #load previously opened profile (stored in ScurryConfig.ini)
        self.profile_load(STARTUP=True)
   
    def config_apply(self, reversed=False, called_by_save_function=False): #applies all attribute versions of parameters to self.current_config. If reversed=True, does the opposite: reverts all attribute versions of parameters to values of self.current_config()
        if not reversed: #default operation
            for key in self.current_config.keys(): 
                value = getattr(self, key)    
                self.current_config.update({key : value})
        else: #reversed operation
            for item in self.current_config.items():
                key = item[0]
                value = item[1]

                setattr(self, key, value)

        self.refresh_gui()
        self.btnApply.setText("Apply")
        if not called_by_save_function: #avoid redundancy
            self.profile_save(overwrite_current_profile=True) #overwrites currently active config file at self.profile_config to apply changes without prompting the user to select a save location.

    def config_changed(self, return_boolean=False): #check if current config has changed from loaded config. Add decorative text to the apply button if changed. Update self.profile_name. Update the text of self.lblCurrentProfile
        config_changed = False
        config_default = True
        
        for item in self.current_config.items():
            key = item[0]
            value = item[1]

            if key == 'custom_sprite_filepath': #relative and absolute filepaths are equivalent and should not count as a change in the config
                if not os.path.abspath(self.custom_sprite_filepath) == os.path.abspath(self.current_config['custom_sprite_filepath']):
                    config_changed = True
                if not os.path.abspath(self.custom_sprite_filepath) == os.path.abspath(self.DEFAULT_CONFIG['custom_sprite_filepath']):
                    config_default = False
            else:
                if not getattr(self, key) == value:
                    config_changed = True
                if not getattr(self, key) == self.DEFAULT_CONFIG[key]:
                    config_default = False

        if config_changed:
            self.btnApply.setText("**Apply**")
        else:
            self.btnApply.setText("Apply")

        if os.path.abspath(self.profile_filepath) == os.path.abspath(self.DEFAULT_CONFIG['profile_filepath']): #no profile loaded
            if config_default:
                self.profile_name = 'DEFAULT'
            else:
                self.profile_name = 'NONE'
        else: self.profile_name = os.path.basename(self.profile_filepath)[:-4]

        self.lblCurrentProfile.setText('Current Profile: ' + self.profile_name)

        if return_boolean:
            return config_changed

    def config_restore_defaults(self): #displays a confirmation dialog to the user. If user confirms, un-loads current profile, and then sets self.current_config = self.DEFAULT_CONFIG.copy()
        if not self.profile_name == 'DEFAULT': #redundant to execute logic when config is already default.
            warning = QMessageBox()
            warning.setWindowTitle("Confirm Restore Default")
            warning.setWindowIcon(self.icon)
            warning.setIcon(QMessageBox.Icon.Warning)
            warning.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            warning.setDefaultButton(QMessageBox.StandardButton.No)

            if self.profile_name == "NONE": #no profile loaded
                warning.setText('Are you sure you would like to restore all settings to default?\n\nYou will lose all settings unless you save them to a profile.')
            elif self.config_changed(return_boolean=True): #profile loaded, but has un-applied changes
                warning.setText(f'You have not applied your changes to profile: {self.profile_name}.\n\nIf you restore all settings to default, you will lose your un-applied changes to this profile.\n\nWould you like to continue?')
            else: #profile loaded, config has already been applied.
                warning.setText(f'Are you sure you would like to restore all settings to default?\n\nYour current profile ({self.profile_name}) will be un-loaded but it will NOT be erased')

            response = warning.exec()

            if response == QMessageBox.StandardButton.Yes:
                self.current_config = self.DEFAULT_CONFIG.copy()
                self.config_apply(reversed=True)

    def config_revert(self): #calls self.config_apply(reversed=true). I don't think I can set the event handler for self.btnRevert to call self.config_apply() with kwargs, so this is my solution. works good enough for me.
        self.config_apply(reversed=True)

    def config_validate_parameters(self, config_dictionary, invalid_parameters=set()): #used in conjunction with self.profile_load(), contains all of the logic for determining whether the value of any given parameter is valid. updates and returns a set of invalid parameters, as well as a boolean.
        # I orignally wanted to be nice and try to recover as much valid data as possible from a corrupted config file. But the amount of logic involved became more tedious than I was willing to put up with.
        # So now I've chosen to be mean because it's easier. For related parameters, (such as lower_x_boundary, upper_x_boundary, etc.) if one of the parameters is invalid, scurry will treat all of them as invalid. sorry, not sorry.
        
        for item in config_dictionary.items():
            key = item[0]
            value = item[1]

            if not key in invalid_parameters: #not worth checking data we already know is invalid. prevents TypeErrors as well.
                
                # being nice was too hard. I tried to use logic to determine all of the edge cases and whether or not they were recoverable,
                # but there were just too many things to try and keep track of. so now any parameter that raises an exception will be considered invalid.
                try: 
                    if key == 'app_window_width':
                        if not 128 <= value <= 4096:
                            invalid_parameters.add(key)
                    elif key == 'app_window_height':
                        if not 128 <= value <= 2160:
                            invalid_parameters.add(key)
                    elif key in self.color_groups.values(): #checks ALL colors
                        for color in value:
                            if not 0 <= color <= 255:
                                invalid_parameters.add(key)
                    #elif key == 'background_color'
                        #pass #all colors already checked
                    elif key == 'fps':
                        if not 1 <= value <= 480:
                            invalid_parameters.add(key)
                    elif key in {'lower_x_boundary', 'upper_x_boundary', 'lower_y_boundary', 'upper_y_boundary'}: 
                        all_valid = True

                        try: #use try block in case elements are missing from config_dictionary
                            if not -8000 <= config_dictionary['lower_x_boundary'] <= config_dictionary['upper_x_boundary'] <= 8000:
                                all_valid = False
                            
                            if not -8000 <= config_dictionary['lower_y_boundary'] <= config_dictionary['upper_y_boundary'] <= 8000:
                                all_valid = False
                        except:
                            all_valid = False
                        
                        if not all_valid:
                            invalid_parameters.add('lower_x_boundary')
                            invalid_parameters.add('upper_x_boundary')
                            invalid_parameters.add('lower_y_boundary')
                            invalid_parameters.add('upper_y_boundary')

                    elif key == 'centered_cursor_mode':
                        if not value in range(3):
                            invalid_parameters.add(key)
                    elif key == 'sensitivity':
                        if not 0.01 <= value <= 10:
                            invalid_parameters.add(key)
                    elif key == 'trail_lifetime':
                        if not 0 <= value <= 2:
                            invalid_parameters.add(key)
                    #elif key == 'enable_cursor_idle_reset':
                        #pass #no need to check booleans 
                    elif key == 'cursor_idle_reset':
                        if not 0.1 <= value <= 2:
                            invalid_parameters.add(key)
                    #elif key == 'wrapping_mode':
                        #pass #no need to check booleans
                    elif key == 'trail_thickness':
                        if not 1 <= value <= 128:
                            invalid_parameters.add(key)
                    elif key == 'trail_sample_rate':
                        if not 30 <= value <= 1000:
                            invalid_parameters.add(key)
                    elif key == 'velocity_smoothing':
                        if not 0 <= value <= 9:
                            invalid_parameters.add(key)
                    elif key in {'circle_sprite_size', 'circle_outline_size'}:
                        all_valid = True
                        
                        try: #use try block in case elements are missing from config_dictionary
                            for size in {'circle_sprite_size', 'circle_outline_size'}:
                                if not 0 <= config_dictionary[size] <= 128:
                                    all_valid = False
                            
                            if config_dictionary['circle_outline_size'] > config_dictionary['circle_sprite_size']:
                                all_valid = False
                        except:
                            all_valid = False

                        if not all_valid:
                            invalid_parameters.add('circle_sprite_size')
                            invalid_parameters.add('circle_outline_size')
                    #elif key == 'circle_sprite_color':
                        #pass #all colors already checked
                    #elif key == 'circle_outline_size':
                        #pass already checked
                    #elif key == 'circle_outline_color':
                        #pass #all colors already checked
                    #elif key == 'use_custom_sprite':
                        #pass #no need to check booleans
                    elif key == 'custom_sprite_size':
                        if not 1 <= value <= 128:
                            invalid_parameters.add(key)
                    #elif key == 'prefer_relative_filepath':
                        #pass #no need to check booleans
                    #elif key == 'custom_sprite_filepath':
                        #pass #case handled already in self.valid_filepath() and self.update_preview()
                    elif key in {'animate_sprite', 'rotate_sprite'}: #I lied. these booleans depend on other parameters and must be validated
                        valid = False #we don't need to invalidate both parameters here if one of them is invalid. the logic is simple enough to write out explicitly.

                        try: #use try block in canse list elements are missing from config_dictionary
                            if key == False: #false value always valid
                                valid = True
                            elif 'custom_sprite_filepath' in config_dictionary.keys(): #neither parameter is valid if sprite filepath is non-existent or not valid
                                if self.valid_filepath(config_dictionary['custom_sprite_filepath']):
                                    if key == 'rotate_sprite': #any valid custom sprite can be rotated
                                        valid = True
                                    else:
                                        sprite_sheet = QPixmap(self.custom_sprite_filepath)

                                        sprite_sheet_width = sprite_sheet.width()
                                        sprite_sheet_height = sprite_sheet.height()
                                            
                                        #decide if sprite sheet is animateable. 
                                        if sprite_sheet_width % sprite_sheet_height == 0 and sprite_sheet_width != sprite_sheet_height: #sprite sheet is animateable
                                            valid = True

                                        del sprite_sheet #idk if this is necessary but it feels good to clean up after myself. images can be pretty big files after all
                        except:
                            valid = False

                        if not valid:
                            invalid_parameters.add(key)
                    elif key == 'animation_speed':
                        if not 0.05 <= value <= 10: #if you actually set your animation speed to 10....you're probably also the kind of person who sets their sensitivity to 10 and disables draw_mouse_sprite, draw_trail_dots, and draw_trail_lines simultaneously xD
                            invalid_parameters.add(key)
                    #elif key == 'draw_mouse_sprite':
                        #pass #no need to check booleans
                    #elif key == {'draw_trail_dots', 'draw_trail_lines'}:
                        #pass # all combinations of these two booleans are valid
                    #elif key == 'slow_trail_color':
                        #pass #all colors already checked
                    #elif key == 'medium_fast_trail_color':
                        #pass #all colors already checked
                    #elif key == 'very_fast_trail_color':
                        #pass #all colors already checked
                    elif key == {'slow_color_upper_boundary', 'medium_fast_color_lower_boundary', 'medium_fast_color_upper_boundary', 'very_fast_color_lower_boundary'}:
                        all_valid = True

                        try: #use try block in case elements are missing from config_dictionary
                            if not 0 <= config_dictionary['slow_color_upper_boundary'] <= config_dictionary['medium_fast_color_lower_boundary'] <= config_dictionary['medium_fast_color_upper_boundary'] <= config_dictionary['very_fast_color_lower_boundary'] <= 100:
                                all_valid = False
                        except:
                            all_valid = False  

                        if not valid:        
                            invalid_parameters.add('slow_color_upper_boundary')
                            invalid_parameters.add('medium_fast_color_lower_boundary')
                            invalid_parameters.add('medium_fast_color_upper_boundary')
                            invalid_parameters.add('very_fast_color_lower_boundary')

                except:
                    invalid_parameters.add(key)
        
        #A config is only valid it it does not contain any invalid parameters.
        if len(invalid_parameters) == 0:
            valid_config_file = True
        else:
            valid_config_file = False

        return(valid_config_file, invalid_parameters)
                    
    def convert_filepath(self, filepath, convert_to_relative=True): #converts a filepath from relative to absolute or vise verse. also replaces "\" characters with "/" for quality of life reasons.
        if convert_to_relative:
            filepath = os.path.relpath(filepath)
            if filepath[1] != ".":
                filepath = "./" + filepath
        else:
            filepath = os.path.abspath(filepath)

        converted_filepath = filepath.replace("\\", "/")
        
        return converted_filepath

    def cycle_custom_sprite_frames(self): #callback for the self.btnCycleFrames object. Cycles through the frames of an animated sprite in the preview.
        self.custom_sprite_current_frame += 1
        if self.custom_sprite_current_frame > len(self.custom_sprite_frames):
            self.custom_sprite_current_frame = 1

        self.lblCustomSpritePreview.setPixmap(self.custom_sprite_frames[self.custom_sprite_current_frame - 1])
        self.btnCycleFrames.setText(f"Cycle Frames ({self.custom_sprite_current_frame}/{len(self.custom_sprite_frames)})")

    def get_color_group(self, object_name): #determines which group in self.color_groups an given object belongs to. returns the name of the group and the attribute associated with it.
        for group in self.color_groups.keys():
            if group in object_name: 
                return group, self.color_groups.get(group)
        
        #if for some reason this function is called and the object provided does not belong to a group, then return None
        return None

    def get_object_type(self, object_name): #determines the type of GUI element a given object name refers to by analyzing it's prefix.
        for prefix in self.PREFIXES:
            if object_name[:len(prefix)] == prefix:
                return prefix
        
        #if for some reason this function is called and the object provided does not belong to a group, then return None
        return None

    def launch_scurry(self): #launches the main scurry app and passes a copy of self.current_config as an argument. Shows a confirmation dialog if user has un-applied changes.
        global scurry_mouse_visualizer_launcher
        abort = False

        if self.config_changed(return_boolean=True):
            profile_name = ""
            
            if not self.profile_name in {'DEFAULT', 'NONE'}:
                profile_name = self.profile_name

            message = QMessageBox()
            message.setWindowIcon(self.icon)
            message.setWindowTitle("Apply Changes?")
            message.setIcon(QMessageBox.Icon.Information)
            message.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            message.setDefaultButton(QMessageBox.StandardButton.Cancel)
            message.setText(
                f'You have not applied changes to your current configuration{profile_name}. Would you like to apply them before launching?'
            )

            response = message.exec()

            if response == QMessageBox.StandardButton.Yes:
                self.config_apply()
            elif response == QMessageBox.StandardButton.No:
                self.config_revert()
            elif response == QMessageBox.StandardButton.Cancel:
                abort = True

        if not abort:
            config = self.current_config.copy()
            config['profile_name'] = self.profile_name #add parameter for scurry to put in the WindowTitle when initializing.

            scurry_mouse_visualizer_launcher.hide()
        
            ScurryMouseVisualizer.run(config) 
            # I'm pretty sure that all global variables created in ScurryMouseVisualizer.initialize() do not persist once the function call is complete
            # because ScurryMouseVisualizer.run(config) is not assigned to an object. And even if it was, it would not persist after this function has finished executing. 
            # Please correct my lack of understanding if I am mistaken here.

            scurry_mouse_visualizer_launcher.show() #It was a fun experiment to see what happens if I comment this line out. Don't do it please xD

    def open_cursor_boundary_measuring_tool(self): #self explanatory. executes the CursorBoundaryTool.run() method and grabs data returned when the tool is closed.
        scurry_mouse_visualizer_launcher.hide()
        (response, min_x, max_x, min_y, max_y) = CursorBoundaryTool.run(window_icon=self.icon)
        scurry_mouse_visualizer_launcher.show()

        if response == 1 and min_x != "NONE" and max_x != "NONE" and min_y != "NONE" and max_y != "NONE": #response == 1 when user clicks "Ok". else response = 0
            self.comboCursorBoundaries.setCurrentIndex(6)
            self.spinLowerX.setEnabled(True)
            self.spinUpperX.setEnabled(True)
            self.spinLowerY.setEnabled(True)
            self.spinUpperY.setEnabled(True)
            
            #IMPORTANT!!! - SET THE VALUES OF THE SPINBOXES FIRST.
            self.spinLowerX.setValue(int(min_x))
            self.spinUpperX.setValue(int(max_x))
            self.spinLowerY.setValue(int(min_y))
            self.spinUpperY.setValue(int(max_y))
            
            #If you set these values first, and then apply them to the spinboxes, you will have bugs caused by the logic in self.update_cursor_boundaries()
            self.lower_x_boundary = self.spinLowerX.value()
            self.upper_x_boundary = self.spinUpperX.value()
            self.lower_y_boundary = self.spinLowerY.value()
            self.upper_y_boundary = self.spinUpperY.value()

    def profile_load(self, filepath=None, STARTUP=False): #Reads and parses .ini files for saved configs. Validates config files and their contents. Used in conjunction with self.config_validate_parameters.
        #LOAD FUNCTIONALITY FLOW:
            #AQUIRE TARGET FILEPATH
                #If no target filepath supplied, decide which filepath to load from
                    #If STARTUP, then try to locate the last loaded profile, and target its filepath,
                        #Target default profile if there are any problems
                    #Else open file chooser to select .ini file to load from.
            
            #ATTEMPT TO READ FROM TARGET FILEPATH. FILE IS UNRECOVERABLE IF UNABLE. ABORT
                #Profile is recoverable if target filepath can be read
            #TRANSFER INFO TO DICTIONARY OBJECT
                #Track invalid parameters. A config is not valid if it contains any missing/invalid parameters.
            #ATTEMT TO TYPECAST TRANSFERRED INFO. RECORD ANY PARAMETERS THAT FAIL TO TYPECAST AS INVALID
            #CHECK TYPECASTED CONFIG FOR MISSING PARAMETERS. ADD MISSING PARAMETERS TO INVALID PARAMETERS
            #VALIDATE THE TYPECASTED CONFIGURATION. RETURN A BOOLEAN AND A SET OF INVALID PARAMETERS

            #ATTEMPT TO RECOVER IF RECOVERABLE. ELSE ABORT AND REVERT TO CURRENTLY LOADED PROFILE
                #If target filepath is default and file is not recoverable, overwrite default profile and perform load operation
                #If STARTUP, cannot abort load operation.
                    #target filepath cannot be default here, as that case is handled above
                    #If non-default profile is unrecoverable, call load function again with target filepath == default profile filepath
            
            #IF FILE IS VALID, RECOVERED, OR OVERWRITTEN, PERFORM LOAD OPERATION
            #ELIF STARTUP, CALL LOAD FUNCTION AGAIN AND ATTEMPT TO LOAD DEFAULT PROFILE
            #ELSE ABORT
        
        SECTION = "SCURRY_CONFIG_PARAMETERS"
        parser = configparser.ConfigParser()
        invalid_parameters = set() #we will attempt to recover any partially invalid config files and replace invalid parameters with default values.        
        valid_config_file = True
        recoverable = False
        abort = False

        if not filepath: #target filepath not supplied. Decide which filepath to load from
            if STARTUP: #called by self.__init__(). read the ./ScurryConfig.ini file and look for the last actively loaded profile. Create a ScurryConfig.ini file if none exists.
                if not os.path.exists(self.DEFAULT_CONFIG['profile_filepath']):
                    message = QMessageBox()
                    message.setWindowIcon(self.icon)
                    message.setIcon(QMessageBox.Icon.Warning)
                    message.setWindowTitle("Missing Config")
                    message.setText(f"Primary configuration file ({os.path.basename(self.DEFAULT_CONFIG['profile_filepath'])}) could not be found. Scurry will now create a new one.")
                    message.setStandardButtons(QMessageBox.StandardButton.Ok) 

                    message.exec()

                    self.current_config = self.DEFAULT_CONFIG.copy()
                    self.config_apply(reversed=True)

                    filepath = self.DEFAULT_CONFIG['profile_filepath']
                else: #ScurryConfig.ini exists
                    try: 
                        parser.read(self.DEFAULT_CONFIG['profile_filepath'])
                        filepath = parser.get('PROFILE_INFO', 'profile_filepath')
                    except:
                        message = QMessageBox()
                        message.setWindowIcon(self.icon)
                        message.setIcon(QMessageBox.Icon.Warning)
                        message.setWindowTitle("Error Loading Profile")
                        message.setText(f"Scurry is unable to determine your last loaded profile. Scurry will now attempt to load the default profile.")
                        message.setStandardButtons(QMessageBox.StandardButton.Ok)

                        message.exec()

                        filepath = self.DEFAULT_CONFIG['profile_filepath'] #exists

                    if not os.path.exists(filepath): #default config file points to a non-existent profile.
                        message = QMessageBox()
                        message.setWindowIcon(self.icon)
                        message.setIcon(QMessageBox.Icon.Warning)
                        message.setWindowTitle("Missing Profile")
                        message.setText(f"Previously loaded profile ({os.path.basename(filepath)}) could not be found. Scurry will load the default profile instead.")
                        message.setStandardButtons(QMessageBox.StandardButton.Ok) 

                        message.exec()

                        filepath = self.DEFAULT_CONFIG['profile_filepath'] #load default profile, which we know is readable
                
            else:
                filepath = QFileDialog.getOpenFileName(QDialog(),"Load Custom Profile", os.getcwd(), "Configuration Files (*ini)")[0] #use index 0 because QFileDialog returns a tuple.
                if filepath == "":
                    abort = True
        
        filepath = os.path.abspath(filepath) #idk if this is redundant but I want to ensure that filepaths match exactly so all filepaths will be converted to abspaths by using the os.path.abspath() method.
        #validate config file. valid_config_file and recoverable booleans will be used to decide how to handle the load operation.
        if not abort:
            try: #if parser cannot read file, file is invalid and unrecoverable
                parser.read(filepath)
                if not parser.has_section(SECTION): #section is missing or corrupted
                    valid_config_file = False
            except:
                valid_config_file = False

            #recoverable == False by default
            if valid_config_file: #file has correct section
                recoverable = True #From here onwards, we will determine the value of valid_config_file by checking the length of invalid_parameters
                
                reference_config = self.DEFAULT_CONFIG.copy() #create a config that resembles the a valid configuration.
                reference_config.pop('profile_filepath') #no need to validate profile_filepath because we know that it pointed us to a valid config file.

                loaded_config = {}
                for option in parser.options(SECTION): 
                    if option in reference_config.keys(): #extract all valid parameters from ini file.
                        loaded_config[option] = parser.get(SECTION, option) #any invalid options will be caught later when we check for missing elements
            
                typecast_config = {}
                for item in loaded_config.items(): #attempt to properly typecast all data read from ini file
                    key = item[0]
                    value = item[1]

                    expected_type = type(reference_config[key])

                    try: #any parameter that fails to typecast is invalid
                        if expected_type == int:
                            typecast_value = int(value)

                        elif expected_type == float:
                            typecast_value = round(float(value),2)

                        elif expected_type == bool:
                            if value.upper() in {'TRUE', 'FALSE'}:
                                typecast_value = eval(value) #Note to self.. the bool typecast will return true if the string is not empty.
                            else:
                                invalid_parameters.add(key)

                        elif expected_type == tuple:
                                #value is a string, index refers to character number
                                if value[0] == "(" and value[-1] == ")" and value.count(", ") == 2:
                                    comma_indexes = []

                                    for index in range(len(value)):
                                        if value[index] == ",":
                                            comma_indexes.append(index)
                                    
                                    num1 = value[1 : comma_indexes[0]]
                                    num2 = value[comma_indexes[0] + 2 : comma_indexes[1]]
                                    num3 = value[comma_indexes[1] + 2: -1]

                                    typecast_value = (int(num1), int(num2), int(num3))
                                else:
                                    invalid_parameters.add(key)

                        elif expected_type == str:
                            typecast_value = value #config parser returns only string values

                        else:
                            typecast_value = None
                            invalid_parameters.add(key)
                        
                        if not type(typecast_value) == type(None): #Band-aid bug fix in which typecast_value = 0 would cause the statement "if typecast_value:" to be false.
                            typecast_config[key] = typecast_value
                    
                    except:
                        invalid_parameters.add(key)
                
                if not len(typecast_config) == len(reference_config): #typecast_config is missing elements. 
                    for key in reference_config.keys(): #try to catch any parameters that are fully missing from the config file
                        if not key in typecast_config.keys(): #I know that invalid parameters will also get flagged here but I don't care.
                            valid_config_file = False
                            invalid_parameters.add(key)
                
                #screen typecast_config for invalid parameter values
                (valid_config_file, invalid_parameters) = self.config_validate_parameters(typecast_config, invalid_parameters)

                if len(invalid_parameters) > 0:
                    valid_config_file = False

            #Decide how to handle the load operation
            if not recoverable: #inform the user and abort the load operation
                message = QMessageBox()
                message.setWindowIcon(self.icon)
                message.setWindowTitle("Invalid Config File")
                message.setIcon(QMessageBox.Icon.Critical)
                message.setStandardButtons(QMessageBox.StandardButton.Ok)

                if os.path.abspath(filepath) == os.path.abspath(self.DEFAULT_CONFIG['profile_filepath']): #ScurryConfig.ini is unreadable. Overwrite ScurryConfig.ini with defaults.
                    message.setText(f'Default config file ({os.path.basename(filepath)}) cannot be read or parsed. It will be overwritten to default configuration.')

                    message.exec()

                    typecast_config = self.DEFAULT_CONFIG.copy()
                    abort = False #load config as normal
                else: #non-default profile is not recoverable.
                    if STARTUP:
                        message.setText(f'Previously loaded  profile ({os.path.basename(filepath)}) cannot be read or parsed. scurry will attempt to load the default profile instead.')
                    else:
                        message.setText(f'Config file ({os.path.basename(filepath)}) cannot be read or parsed. Please load a different config file or create a new one using the "Save Profile," button.')                  
                    
                    message.exec()
                    abort = True
            elif not valid_config_file: #invalid config file can be recovered. prompt the user to continue.
                #create a string containing the list of invalid parameters. this will be displayed to the user.
                list_invalid_parameters = ""
                for key in reference_config.keys():
                    if key in invalid_parameters:
                        list_invalid_parameters += (str(key) + "\n")
                
                message = QMessageBox()
                message.setWindowTitle('Error Reading Config File')
                message.setWindowIcon(self.icon)
                message.setIcon(QMessageBox.Icon.Warning)
                message.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
                message.setDefaultButton(QMessageBox.StandardButton.Cancel)
                
                if os.path.abspath(filepath) == os.path.abspath(self.DEFAULT_CONFIG['profile_filepath']): #Default config (Scurryconfig.ini) contains invalid values. Replace invalid values with default, without giving the user a choice,
                    message.setText(
                        f'Default config file ({os.path.basename(filepath)}) contains missing/invalid parameters. Scurry will replace the invalid parameters with their default values. ' + 
                        'For a detailed list, click the "Details" button below.'
                    )
                    message.setStandardButtons(QMessageBox.StandardButton.Ok)
                else:
                    message.setText(
                        f'Config file ({os.path.basename(filepath)}) contains missing/invalid parameters. Scurry can repair the file by substituting invalid ' +
                        'parameters with defaults. For a detailed list, click the "Details" button below.\n\nWould you like to continue?'
                    )
                
                message.setDetailedText(
                f'The following parameters were either missing from your config file or contain invalid values:\n\n{list_invalid_parameters}'
                )
                
                response = message.exec()

                if response == QMessageBox.StandardButton.Yes or response == QMessageBox.StandardButton.Ok:
                    for item in typecast_config.items(): #replace all invalid parameters in typecast_config with default values, then pass on to normal load operation
                        key = item[0]
                        value = item[1]
                        if key in invalid_parameters:
                            typecast_config[key] = reference_config[key]
                else:
                    abort = True
            
        if not abort:
            #apply typecast_config to current_config and apply using self.apply()
            for item in typecast_config.items():
                key = item[0]
                value = item[1]

                self.current_config[key] = value
            
            #ensure user preference to save and load relative filepaths is respected before applying config.
            if self.current_config['prefer_relative_filepath'] == True:
                filepath = os.path.relpath(filepath)
            else:
                filepath = os.path.abspath(filepath)

            self.current_config['profile_filepath'] = filepath

            self.config_apply(reversed=True) #applies the config and calls the self.profile_save() function to save the loaded config filepath in ScurryConfig.ini
        elif STARTUP:
            self.profile_load(filepath=self.DEFAULT_CONFIG['profile_filepath'], STARTUP=True)

    def profile_save(self, overwrite_current_profile=False): #Creates and overwrites configs as .ini files.
        save_new_profile = not overwrite_current_profile
        # BAND AID BUG FIX: save_new_profile was supposed to be set to true by default as an argument/parameter, 
        # but apparently when this function is called by receiving a signal from the self.btnSaveProfile object, 
        # no default parameters are created, which would cause save_new_profile to be false by default when the user clicks the save button
        
        #SAVE FUNCTIONALITY FLOW:

            #WHEN USER CLICKS SAVE BUTTON:
                #IF CURRENT CONFIG HAS UNAPPLIED CHANGES:
                    #CALL self.apply() to apply unapplied changes. We will assume the user wants to apply changes if they intend to save a new profile.
                #PROMPT FOR SAVE LOCATION
                    #DO NOT ALLOW filenames "DEFAULT", "NONE", "N0NE". This is for app safety/security reasons.
                #SET self.current_config[profile_filepath] to specified filepath.
                #WRITE self.current_config.items() to a new file or overwrite existing at specified filepath.
            #WHEN USER CLICKS APPLY BUTTON:
                #self.config_apply() sets values of self.current_config.values()
                #OVERWRITE currently loaded ini file at self.current_config[profile_filepath] with updated parameters
                #OVERWRITE ScurryConfig.ini [PROFILE_INFO] profile_filepath option to self.current_config[profile_filepath]
            #WHEN USER CLICKS RESTORE DEFAULTS:
                #SET self.current_config = self.DEFAULT_CONFIG.copy()
                #OVERWRITE ScurryConfig.ini with all default values, including [PROFILE_INFO] profile_filepath option. This does not affect the currently loaded profile.
                #CALL self.config_apply(reversed=True) to set all attributes and refresh GUI with defaults

        parser = configparser.ConfigParser()
        abort = False

        if save_new_profile: #user clicked the btnSaveProfile object
            profile_filepath = ""
            enter_loop = True #this solution feels a bit clunky for handling the logic of this loop but it's the best way I can think of, because an empty string is the best possible starting value for profile_filepath
            while enter_loop or (os.path.basename(profile_filepath)[:-4]).strip().upper() in {'DEFAULT', 'NONE', 'N0NE'}: #Check for filename matching Scurry default filenames
                enter_loop = False
                profile_filepath = QFileDialog.getSaveFileName(QDialog(),"Save Custom Profile",os.getcwd(),"Configuration Files (*.ini)")[0] #use index 0 because QFileDialog returns tuple
            
                if profile_filepath == "": #user clicked "cancel" or the red x.
                    abort = True
                elif (os.path.basename(profile_filepath)[:-4]).strip().upper() in {'DEFAULT', 'NONE', 'N0NE'}: #Do not allow reserved filenames for app safety/security reasons.
                    message = QMessageBox()
                    message.setWindowIcon(self.icon)
                    message.setIcon(QMessageBox.Icon.Information)
                    message.setWindowTitle('Invalid Filename')
                    message.setText('The filenames "DEFAULT" and "NONE" are reserved by Scurry for core app functionality.\n\nPlease choose a different filename')
                    message.setStandardButtons(QMessageBox.StandardButton.Ok)
                    
                    message.exec() #prompt user to choose a different filename
                    
                else: #receive valid filepath from user
                    self.profile_filepath = profile_filepath

        else: #function was called with an explicit filepath to write/overwrite to.
            profile_filepath = self.profile_filepath
        
        if os.path.abspath(profile_filepath) == os.path.abspath(self.DEFAULT_CONFIG['profile_filepath']): #Will save to default profile. Happens when user clicks Apply or if they choose to overwrite ScurryConfig.ini
            profile_filepath = self.DEFAULT_CONFIG['profile_filepath'] #ensure relative filepath is always used to store default config file.
            self.profile_filepath = self.DEFAULT_CONFIG['profile_filepath']
            save_to_default = True
        else:
            save_to_default = False

        if not abort:
            if self.config_changed(return_boolean=True): #If the user presses the save button, it is reasonable to assume they would like to apply changes they have made.
                self.config_apply(called_by_save_function=True) #avoid calling self.profile_save twice
            
            #at this point it is guaranteed that attribute versions and dictionary versions of current config parameters are the same.
            if self.prefer_relative_filepath: #respect the "prefer_relative_filepath" setting.
                profile_filepath = os.path.relpath(profile_filepath)
            elif not save_to_default: #ensure default profile always saved with relative filepath.
                profile_filepath = os.path.abspath(profile_filepath) 
            
            parameters_section_title = "SCURRY_CONFIG_PARAMETERS"
            profile_info_section_title = "PROFILE_INFO"

            #Prepare to overwrite file at user-collected profile_filepath. may or may not be ScurryConfig.ini
            parser.add_section(parameters_section_title)
            for item in self.current_config.items():
                key = item[0]
                value = item[1]
                
                if not key == 'profile_filepath': #filepath info will be stored in the physical file's filepath. storing in file contents is redundant and annoying to validate in self.config_validate_parameters()
                    parser.set(parameters_section_title, str(key), str(value))

            timestamp = datetime.datetime.now(datetime.UTC)
            config_header_message = ( ";" +
            f"This file was generated by Scurry Mouse Visualizer Launcher at UTC: {timestamp}." + "\n;" + 
                "You can technically edit this file directly but it is much easier to use the config GUI." + "\n;" +
                "Scurry will validate the contents of this file and overwrite any invalid settings to default." + "\n\n"
            )

            default_profile_note = ';NOTE: The parameters listed in the "SCURRY_CONFIG_PARAMETERS" section will only be applied if no other profile is loaded. In other words, if "profile_filepath" is not "ScurryConfig.ini", the settings below will not apply.\n'

            
            #save/overwrite destination file.
            with open(profile_filepath, "w") as configfile: #overwrite previous config file 
                configfile.write(config_header_message)

            if save_to_default: #currently writing to default config file = "./ScurryConfig.ini"
                with open(profile_filepath, "a") as configfile:
                    configfile.write(default_profile_note) #append default profile note to ScurryConfig.ini
        
            with open(profile_filepath, "a") as configfile: #append config settings
                parser.write(configfile)
                
            parser.clear() #prepare to overwrite default config file--this will allow scurry to remember which profile was last loaded.
            
            #only ScurryConfig.ini will have this section and option.
            parser.add_section(profile_info_section_title)
            parser.set(profile_info_section_title,'profile_filepath', profile_filepath) 

            if save_to_default: #just overwrote default config file
                with open(profile_filepath, "a") as configfile: #append profile info to default config file - this preserves the config contents of the "NONE" profile.
                    parser.write(configfile)
            else: #just wrote config to non-default config file. In this case we overwrite default config file parameters back to default settings and assume user will use settings from the profile just created.
                parser.add_section(parameters_section_title)   
                for item in self.DEFAULT_CONFIG.items(): 
                    key = item[0]
                    value = item[1]

                    if not key == 'profile_filepath': #profile filepath already included in [PROFILE_INFO] section.
                        parser.set(parameters_section_title, str(key), str(value))
                
                profile_filepath = self.DEFAULT_CONFIG['profile_filepath'] 
                with open(profile_filepath, "w") as configfile: 
                    configfile.write(config_header_message + default_profile_note) #overwrite default config file. Add header and default-profile note
        
                with open(profile_filepath, "a") as configfile: #append config settings, which includes profile_info section that points to currently loaded profile.
                    parser.write(configfile)

    def refresh_gui(self): #applies all values in self.current_config to corresponding GUI elements\
        config_casche = self.current_config.copy() 
        #BAND AID bug fix to account for the potential for any GUI element callback functions to change the values stored in self.current_config while this function is executing

        #app_window_width
        #app_window_height
        self.spinW.setValue(config_casche['app_window_width'])
        self.spinH.setValue(config_casche['app_window_height'])

        #background_color
        #circle_sprite_color
        #circle_outline_color
        #slow_trail_color
        #medium_fast_trail_color
        #very_fast_trail_color
        for item in self.color_groups.items():
            group_name = item[0]
            group_attribute = item[1]

            color = config_casche[group_attribute]
            getattr(self, self.SPIN + group_name + "R").setValue(color[0])
            getattr(self, self.SPIN + group_name + "G").setValue(color[1])
            getattr(self, self.SPIN + group_name + "B").setValue(color[2])

        #fps
        fps = config_casche['fps']
        if fps == 30:
            self.comboFPS.setCurrentIndex(0)
        elif fps == 60:
            self.comboFPS.setCurrentIndex(1)
        elif fps == 90:
            self.comboFPS.setCurrentIndex(2)
        elif fps == 120:
            self.comboFPS.setCurrentIndex(3)
        elif fps == 144:
            self.comboFPS.setCurrentIndex(4)
        elif fps == 180:
            self.comboFPS.setCurrentIndex(5)
        elif fps == 240:
            self.comboFPS.setCurrentIndex(6)
        elif fps == 360:
            self.comboFPS.setCurrentIndex(7)
        elif fps == 480:
            self.comboFPS.setCurrentIndex(8)
        else:
            self.comboFPS.setCurrentIndex(9)
        
        self.spinCustomFPS.setValue(fps)

        #lower_x_boundary
        #upper_x_boundary
        #lower_y_boundary
        #upper_y_boundary
        boundaries = (config_casche['lower_x_boundary'], 
                      config_casche['upper_x_boundary'], 
                      config_casche['lower_y_boundary'], 
                      config_casche['upper_y_boundary'])

        if boundaries == (0, 720, 0, 480):
            self.comboCursorBoundaries.setCurrentIndex(0)
        elif boundaries == (0, 1280, 0, 720):
            self.comboCursorBoundaries.setCurrentIndex(1)
        elif boundaries == (0, 1920, 0, 1080):
            self.comboCursorBoundaries.setCurrentIndex(2)
        elif boundaries == (0, 2560, 0, 1440):
            self.comboCursorBoundaries.setCurrentIndex(3)
        elif boundaries == (0, 3840, 0, 2160):
            self.comboCursorBoundaries.setCurrentIndex(4)
        elif boundaries == (0, 7680, 0, 4320):
            self.comboCursorBoundaries.setCurrentIndex(5)
        else:
            self.comboCursorBoundaries.setCurrentIndex(6)

        self.spinLowerX.setValue(boundaries[0])
        self.spinUpperX.setValue(boundaries[1])
        self.spinLowerY.setValue(boundaries[2])
        self.spinUpperY.setValue(boundaries[3])

        #centered_cursor_mode
        self.comboCenteredCursorMode.setCurrentIndex(config_casche['centered_cursor_mode'])

        #sensitivity
        self.dblspinSensitivity.setValue(config_casche['sensitivity'])

        #trail_lifetime
        self.dblspinTrailLifetime.setValue(config_casche['trail_lifetime'])

        #enable_cursor_idle_reset
        self.cbCursorIdleReset.setChecked(config_casche['enable_cursor_idle_reset'])

        #cursor_idle_reset
        self.dblspinCursorIdleReset.setValue(config_casche['cursor_idle_reset'])

        #wrapping_mode
        self.comboWrapStyle.setCurrentIndex(int(config_casche['wrapping_mode']))

        #trail_thickness
        self.spinTrailThickness.setValue(config_casche['trail_thickness'])

        #trail_sample_rate
        value = config_casche['trail_sample_rate']
        if value ==30:
            self.comboTrailSampleRate.setCurrentIndex(0)
        elif value ==100:
            self.comboTrailSampleRate.setCurrentIndex(1)
        elif value ==250:
            self.comboTrailSampleRate.setCurrentIndex(2)
        elif value ==500:
            self.comboTrailSampleRate.setCurrentIndex(3)
        elif value ==1000:
            self.comboTrailSampleRate.setCurrentIndex(4)
        else:
            self.comboTrailSampleRate.setCurrentIndex(5)

        self.spinTrailSampleRate.setValue(value)

        #velocity_smoothing:
        self.comboVelocitySmoothing.setCurrentIndex(config_casche['velocity_smoothing'])

        #circle_sprite_size
        self.spinCircleSpriteSize.setValue(config_casche['circle_sprite_size'])

        #circle_outline_size
        self.spinCircleOutlineSize.setValue(config_casche['circle_outline_size'])

        #use_custom_sprite
        if config_casche['use_custom_sprite']:
            self.radioCustomSprite.setChecked(True)
        else:
            self.radioDefaultColoredCircle.setChecked(True)

        #custom_sprite_size
        self.spinCustomSpriteSize.setValue(config_casche['custom_sprite_size'])

        #prefer_relative_filepath:
        self.cbPreferRelativeFilepath.setChecked(config_casche['prefer_relative_filepath'])

        #custom_sprite_filepath:
        self.txtCustomSpriteFilepath.setText(config_casche['custom_sprite_filepath'])

        #rotate_sprite
        self.cbRotateSprite.setChecked(config_casche['rotate_sprite'])
        
        #animate_sprite
        self.cbAnimateSprite.setChecked(config_casche['animate_sprite'])

        #animation_speed
        self.dblspinAnimationSpeed.setValue(config_casche['animation_speed'])

        #draw_mouse_sprite
        if not config_casche['draw_mouse_sprite']:
            self.radioNoSprite.setChecked(True)

        #draw_trail_dots
        #draw_trail_lines
        dots = config_casche['draw_trail_dots']
        lines = config_casche['draw_trail_lines']

        if dots and lines:
            self.radioBoth.setChecked(True)
        elif dots and not lines:
            self.radioColoredDots.setChecked(True)
        elif (not dots) and lines:
            self.radioColoredLineSegments.setChecked(True)
        else:
            self.radioNoTrailEffect.setChecked(True)

        #slow_color_upper_boundary
        #medium_fast_color_lower_boundary
        #medium_fast_color_upper_boundary
        #very_fast_color_upper_boundary
        self.spinSlowUpper.setValue(config_casche['slow_color_upper_boundary'])
        self.spinMedLower.setValue(config_casche['medium_fast_color_lower_boundary'])
        self.spinMedUpper.setValue(config_casche['medium_fast_color_upper_boundary'])
        self.spinFastLower.setValue(config_casche['very_fast_color_lower_boundary'])

        self.current_config = config_casche.copy() #Band-Aid ensures self.current_config is not changed by the self.refresh_gui() method

    def scroll_label(self): #I CAN'T FIGURE OUT HOW TO USE THE SCROLLAREA WIDGET IN QT DESIGNER T_T. This function is my workaround to create scroll functionality.
        #function uses the GUI naming conventions I described in the self.__init__() function to provide scroll functionality to self.lblRequirements and self.lblAbout
        
        trigger_object = self.tabwidgetPage.sender()
        trigger_object_name = trigger_object.objectName()
        initial_geometry = self.scrollable_labels_initial_geometries[trigger_object_name]

        vscroll_value = trigger_object.value() #will be between 0 - 100

        label_object = getattr(self, self.LBL + trigger_object_name[7:])
        initial_x = initial_geometry[0]
        initial_y = initial_geometry[1]
        label_width = initial_geometry[2]
        label_height = initial_geometry[3]
        scroll_area_height = initial_geometry[4]

        new_y = int(round(initial_y - ((vscroll_value / 100) * (label_height - scroll_area_height))))

        label_object.setGeometry(initial_x, new_y, label_width, label_height) #I would love to use the self.lblRequirements.geometry().setY() method to scroll the label but it just won't work and I can't figure out why

    def select_sprite_type(self): #Executes the logic for setting the values of self.draw_mouse_sprite and self.use_custom_sprite in response to the radio buttons on the "Sprite" tab
        selected_button = self.tabSprite.sender()

        if selected_button == self.radioDefaultColoredCircle:
            self.draw_mouse_sprite = True
            self.use_custom_sprite = False

            self.frameDefaultColoredCircle.setEnabled(True)
            self.frameCustomSprite.setEnabled(False)

        elif selected_button == self.radioCustomSprite:
            self.draw_mouse_sprite = True
            self.use_custom_sprite = True

            self.frameDefaultColoredCircle.setEnabled(False)
            self.frameCustomSprite.setEnabled(True)
        elif selected_button == self.radioNoSprite:
            self.draw_mouse_sprite = False
            self.use_custom_sprite = False

            self.frameDefaultColoredCircle.setEnabled(False)
            self.frameCustomSprite.setEnabled(False)
    
        self.config_changed()

    def set_trail_style(self): #Executes the logic for setting the values of self.draw_trail_dots and self.draw_trail_lines in response to the radio buttons on the "Customize" tab
        if self.radioBoth.isChecked():
            self.draw_trail_dots = True
            self.draw_trail_lines = True

        elif self.radioColoredDots.isChecked():
            self.draw_trail_dots = True
            self.draw_trail_lines = False

        elif self.radioColoredLineSegments.isChecked():
            self.draw_trail_dots = False
            self.draw_trail_lines = True

        elif self.radioNoTrailEffect.isChecked():
            self.draw_trail_dots = False
            self.draw_trail_lines = False

        self.config_changed()

    def show_custom_trail_color_info(self): #Displays an info dialogue to the user about how the custom trail colors work.
        infomessage = QMessageBox()
        infomessage.setWindowTitle("Info: Custom Trail Effect Color Gradient")
        infomessage.setWindowIcon(self.icon)
        infomessage.setIcon(QMessageBox.Icon.Information)
        infomessage.setText( #I know I can probably use triple quoted strings here. Too bad. The code is already written and I don't want to re-write it. I will now forever be remembered as a python noob xD
            "Scurry shows how quickly you move your mouse by changing the color of the trail effect. " + 
            "Specifically, Scurry uses a linear gradient between 3 colors that represent slow, medium-fast, and very fast mouse movements. " +
            "You can choose the color for each speed using either RGB or HEX colors \n\n" +    

            "To measure your mouse movement speed, Scurry uses a python module called \"pynput\" to track the position of your mouse cursor on the screen, " + 
            "and calculates velocity by measuring how many pixels the cursor moves in a given time. " +
            "It then takes the velocity and converts it to a number between 0 and 100, and displays it as a percentage. " + 
            "You can click the \"details\" button below if you would like to know the exact cursor speeds associated with each percentile. \n\n" + 

            "You can adjust the speeds associated with \"slow,\" \"medium-fast,\" and \"very fast\" by adjusting the thresholds below the gradient preview." +
            "The color will be solid between each lower and upper threshold, and Scurry will fill the space between the colors with a linear gradient."
        )
        infomessage.setDetailedText(
            "Scurry measures mouse velocity in pixels/second (px/s). It converts that velocity to a number between 1 and 100 by using the following logarithmic scale: \n\n" + 

            "percent = 10*log2(velocity/250) \n\n" +

            "The exact px/s speed associated with each 10th percentile is as follows: \n\n" +
            
            "0%: 250px/s\n10%: 500px/s\n20:%: 1000px/s\n30%: 2,000px/s\n40%: 4,000px/s\n50%: 8,000px/s\n60%: 16,000px/s\n70%: 32,000px/s\n80%: 64,000px/s\n90%: 128,000px/s\n100%: 256,000px/s\n\n" + 
            
            "NOTE: The \"Sensitivity \" slider in the \"General\" tab does NOT affect how Scurry measures these speeds. Moving that slider will change how far the sprite moves on your screen, but the trail colors and speeds associated with them will stay the same. " + 
            "Likewise, your in-game mouse sensitivity will most likely not affect these speeds either, because most games will use raw input from your mouse and apply sensitivity to that. " +
            "However, changing your mouse DPI, or changing your pointer speed in your OS WILL affect the speeds that Scurry calculates. However, there should be enough wiggle room between 200px/s and 256,000px/s for you to adjust the gradient to your liking, regardless of your DPI or pointer speed."
        )

        infomessage.exec()        

    def toggle_animate_sprite(self): #enables/disables self.animate_sprite and calls self.update_preview()
        self.animate_sprite = self.cbAnimateSprite.isChecked()

        if self.animate_sprite:
            self.dblspinAnimationSpeed.setEnabled(True)
        else:
            self.dblspinAnimationSpeed.setEnabled(False)

        self.update_preview(self.custom_sprite_preview_group)
        self.config_changed()

    def toggle_cursor_idle_reset(self): #enables/disables self.cursor_idle_reset and calls self.config_changed()
        self.enable_cursor_idle_reset = self.cbCursorIdleReset.isChecked()

        if self.enable_cursor_idle_reset:
            self.dblspinCursorIdleReset.setEnabled(True)
        else:
            self.dblspinCursorIdleReset.setEnabled(False)
        
        self.config_changed()

    def toggle_prefer_relative_filepath(self): #enables/disables self.prefer_relative_filepath. if the filepath exists, calls self.convert_filepath and self.config_changed()
        self.prefer_relative_filepath = self.cbPreferRelativeFilepath.isChecked()

        filepath = self.txtCustomSpriteFilepath.text()

        if self.valid_filepath(filepath): 
            if self.prefer_relative_filepath:
                converted_filepath = self.convert_filepath(filepath)
            else:
                converted_filepath = self.convert_filepath(filepath,False)

            self.custom_sprite_filepath = converted_filepath
            self.txtCustomSpriteFilepath.setText(converted_filepath)

        self.config_changed()         

    def toggle_rotate_sprite(self): #enables/disables self.rotate_mouse_sprite and calls self.config_changed()
        self.rotate_sprite = self.cbRotateSprite.isChecked()
        self.config_changed()

    def update_animation_speed(self): #updates self.animation_speed. calls self.config_changed()
        self.animation_speed = round(self.dblspinAnimationSpeed.value(),2)
        self.config_changed()

    def update_app_dimensions(self): #updates the values of self.app_window_width and self.app_window_height. calls self.config_changed()
        self.app_window_width = self.spinW.value()
        self.app_window_height = self.spinH.value()
        self.config_changed()

    def update_centered_cursor_mode(self): #updates the value of self.centered_cursor_mode and calls self.config_changed()
        self.centered_cursor_mode = self.comboCenteredCursorMode.currentIndex()
        self.config_changed()

    def update_circle_sprite_properties(self): #validates new values for self.circle_sprite_size and self.circle_outline_size. calls self.config_changed()
        if self.spinCircleOutlineSize.value() <= self.spinCircleSpriteSize.value(): #valid settings
            self.spinCircleOutlineSize.setStyleSheet('QSpinBox#spinCircleOutlineSize {font: 12pt "Arial";}')
            self.spinCircleSpriteSize.setStyleSheet('QSpinBox#spinCircleSpriteSize {font: 12pt "Arial";}')

            self.circle_sprite_size = self.spinCircleSpriteSize.value()
            self.circle_outline_size = self.spinCircleOutlineSize.value()
            self.update_preview(self.circle_sprite_color_group) #self.circle_outline_color_group would also work as an argument here. the argument just tells the update_preview function with preview object(s) to perform update operation on
        else:
            self.spinCircleSpriteSize.setStyleSheet('QSpinBox#spinCircleSpriteSize {font: 12pt "Arial"; background-color: red;}')
            self.spinCircleOutlineSize.setStyleSheet('QSpinBox#spinCircleOutlineSize {font: 12pt "Arial"; background-color: red;}')
        
        self.config_changed()

    def update_color_picker(self): #updates all values associated with the color group that the signal originated from.
        trigger_object_name = self.tabwidgetPage.sender().objectName()
        trigger_object_type = self.get_object_type(trigger_object_name) #decide whether the trigger object is a textbox (line edit) or a spinbox.

        #group name used to identify all widgets associated with the color picker being updated
        group_name, config_setting = self.get_color_group(trigger_object_name)

        R_object = getattr(self, self.SPIN + group_name + "R")
        G_object = getattr(self, self.SPIN + group_name + "G")
        B_object = getattr(self, self.SPIN + group_name + "B")
        text_object = getattr(self, self.TXT + group_name + "Hex")

        R = R_object.value()
        G = G_object.value()
        B = B_object.value()            

        if trigger_object_type == self.SPIN: #sender was a spinbox from the color picker. update the HEX textbox accordingly
            rgb_ints = (R, G, B)
            hex_output = ""

            for x in rgb_ints: #I know this logic is a little clunky and there's probably a better way to do the 0-padding, but it works.
                new_hex = hex(x).upper()
                if len(new_hex) == 3:
                    new_hex = "0" + new_hex[-1:]
                else:
                    new_hex = new_hex[-2:]
                
                hex_output += new_hex

            text_object.setText(hex_output)    
        elif trigger_object_type == self.TXT: #trigger object was the HEX textbox. update the 3 RGB spinboxes accordingly.
            #only allow uppercase letters
            uppercasetext = text_object.text()
            uppercasetext = uppercasetext.upper()
            text_object.setText(uppercasetext)
            
            hex_string = text_object.text()
            
            if self.valid_hex_color(hex_string): #only update if textbox contains a valid hex color.
                text_object.setStyleSheet(f'QLineEdit#txt{group_name}Hex {{font: 12pt "Arial"}}') #inidcates valid hex
            
                R = hex_string[0:2]
                G = hex_string[2:4]
                B = hex_string[4:6]

                R = int(R, 16)
                G = int(G, 16)
                B = int(B, 16)

                R_object.setValue(R)
                G_object.setValue(G)
                B_object.setValue(B)
            else:
                text_object.setStyleSheet(f'QLineEdit#txt{group_name}Hex {{font: 12pt "Arial"; background-color: red;}}') #turn red to indicate invalid hex
        
        setattr(self, config_setting, (R, G, B)) #updates the corresponding attribute version of the color parameter.
        self.update_preview(group_name) #update the preview associated with the color picker
        self.config_changed() #update the status of the apply button and self.profile_name

    def update_cursor_boundaries(self): #executes the logic for updating the parameters associated with cursor boundaries. Calls self.valid_cur
        trigger_object_name = self.tabwidgetPage.sender().objectName()
        trigger_object_type = self.get_object_type(trigger_object_name)

        if trigger_object_type == self.COMBO:
            current_index = self.comboCursorBoundaries.currentIndex()

            if current_index == 6: #Custom boundaries enabled
                self.spinLowerX.setEnabled(True)
                self.spinUpperX.setEnabled(True)
                self.spinLowerY.setEnabled(True)
                self.spinUpperY.setEnabled(True)
            else:
                self.spinLowerX.setEnabled(False)
                self.spinUpperX.setEnabled(False)
                self.spinLowerY.setEnabled(False)
                self.spinUpperY.setEnabled(False)

                self.spinLowerX.setValue(0)
                self.spinLowerY.setValue(0)

            if current_index == 0: #720 x 480
                self.spinUpperX.setValue(720)
                self.spinUpperY.setValue(480)
            elif current_index == 1: #1280 x 720
                self.spinUpperX.setValue(1280)
                self.spinUpperY.setValue(720)
            elif current_index == 2: #1920 x 1080 - default
                self.spinUpperX.setValue(1920)
                self.spinUpperY.setValue(1080)
            elif current_index == 3: #2560 x 1440
                self.spinUpperX.setValue(2560)
                self.spinUpperY.setValue(1440)
            elif current_index == 4: #3840 x 2160
                self.spinUpperX.setValue(3840)
                self.spinUpperY.setValue(2160)
            elif current_index ==5: #7680 x 4320
                self.spinUpperX.setValue(7680)
                self.spinUpperY.setValue(4320)
        elif trigger_object_type == self.SPIN and self.valid_cursor_boundaries(return_boolean=True):
            #dont change these values before they are validated.
            self.lower_x_boundary = self.spinLowerX.value()
            self.upper_x_boundary = self.spinUpperX.value()
            self.lower_y_boundary = self.spinLowerY.value()
            self.upper_y_boundary = self.spinUpperY.value()
        
        self.config_changed()

    def update_cursor_idle_reset(self): #updates self.cursor_idle_reset, calls self.config_changed()
        self.cursor_idle_reset = round(self.dblspinCursorIdleReset.value(),2)
        self.config_changed()

    def update_custom_sprite_filepath(self): #collects the updated filepath from the user, validates it by calling the self.valid_filepath() method, and converts it to absolute or relative path depending on self.prefer_relative_filepath.
        trigger_object = self.tabwidgetPage.sender()

        if trigger_object == self.txtCustomSpriteFilepath: #user either typed filepath or cut and pasted
            filepath = self.txtCustomSpriteFilepath.text()
            valid_filepath = self.valid_filepath(filepath)
                
            if valid_filepath: #only update filepath if valid
                self.txtCustomSpriteFilepath.setStyleSheet('QLineEdit#txtCustomSpriteFilepath {font: 10pt "Arial";}')
                self.custom_sprite_filepath = self.txtCustomSpriteFilepath.text()
                self.update_preview(self.custom_sprite_preview_group) 
            else: 
                self.txtCustomSpriteFilepath.setStyleSheet('QLineEdit#txtCustomSpriteFilepath {font: 10pt "Arial"; background-color: red}')                

        elif trigger_object == self.btnBrowse:
            filepath = QFileDialog.getOpenFileName(QDialog(),"Load Custom Sprite/Sprite Sheet", os.getcwd() + "/Assets", "PNG Image (*png)")[0] #returns a tuple ("filepath", "filetype")

            if self.valid_filepath(filepath): #need this here because clicking the "cancel" button in the dialogue will return whichever directory the user is looking in.
                if self.prefer_relative_filepath:
                    converted_filepath = self.convert_filepath(filepath)
                else:
                    converted_filepath = self.convert_filepath(filepath, False)

                self.custom_sprite_filepath = converted_filepath
                self.txtCustomSpriteFilepath.setText(converted_filepath)
                self.update_preview(self.custom_sprite_preview_group)
        
        self.config_changed()

    def update_custom_sprite_size(self): #updates self.custom_sprite_size and calls self.update_preview() and self.config_changed()
        self.custom_sprite_size = self.spinCustomSpriteSize.value()

        self.update_preview(self.custom_sprite_preview_group)
        self.config_changed()

    def update_fps(self): #updates the value of self.fps and calls self.config_changed()
        trigger_object = self.tabGeneral.sender()
        
        if trigger_object == self.comboFPS:
            index = self.comboFPS.currentIndex()
            
            if index == 9: #custom FPS
                self.spinCustomFPS.setEnabled(True)
            else:
                self.spinCustomFPS.setEnabled(False)
            
            #have to manually specify setValue(value) because CurrentText may contain non-numeric characters like "*"
            if index == 0: self.spinCustomFPS.setValue(30)
            if index == 1: self.spinCustomFPS.setValue(60)
            if index == 2: self.spinCustomFPS.setValue(90) 
            if index == 3: self.spinCustomFPS.setValue(120) 
            if index == 4: self.spinCustomFPS.setValue(144) 
            if index == 5: self.spinCustomFPS.setValue(180) 
            if index == 6: self.spinCustomFPS.setValue(240) 
            if index == 7: self.spinCustomFPS.setValue(360)
            if index == 8: self.spinCustomFPS.setValue(480)  

        self.fps = self.spinCustomFPS.value()
        self.config_changed()

    def update_preview(self, group_name): #handles updates to any of the various groups of preview widgets. Divided into sections depending on which preview is receiving focus.
        #when called, requires a group name as an argument to tell the function which preview to update. this is done by searching the meta-groups I described in the self.__init__() method.
        if group_name in self.preview_groups[self.background_preview_group]: #update background previews. 
            R = self.background_color[0]
            G = self.background_color[1]
            B = self.background_color[2]    

            #update the background color of all preview widgets.
            self.lblBackgroundPreview.setStyleSheet(f'QLabel#lblBackgroundPreview {{background-color:rgb({R},{G},{B});}}')
            self.lblCircleBackgroundPreview.setStyleSheet(f'QLabel#lblCircleBackgroundPreview {{background-color:rgb({R},{G},{B});}}')
            self.lblCustomSpriteBackgroundPreview.setStyleSheet(f'QLabel#lblCustomSpriteBackgroundPreview {{background-color:rgb({R},{G},{B});}}')

        elif group_name in self.preview_groups.get(self.circle_sprite_preview_group): #update circle sprite preview
            #draw a colored circle with the size and outline specified

            #measure label geometry, so we can resize labels and place their centers over the same point.
            border_center_x = self.lblCircleBackgroundPreview.geometry().center().x() #will serve as constant center for circle outline and circle
            border_center_y = self.lblCircleBackgroundPreview.geometry().center().y()

            #create tuples for iterating over in a for loop.
            circle_sizes = (self.circle_sprite_size, self.circle_sprite_size - self.circle_outline_size)
            circle_groups = (self.circle_outline_color_group, self.circle_sprite_color_group)
            
            # This was a little tricky to get right. The only way I could think of to draw a circle was by using the css border-radius property in the QSS style sheet, which essentially just rounds the corners of the label.
            # However, it was really finicky and straight up would not work unless the border radius was strictly <= half of min(label_width, label_height), which only worked when the label width was an even number of pixels.
            # It was also tricky to get the centers of both the outline circle and the main color circle to align perfectly over the same pixel, because they might have even or odd label widths. The solution I decided to go 
            # with was to force all circles to be confined in labels that had odd widths. The algorithm turned out to be fairly simple, but it took a bit of trial and error to get right. It's touchy, and so I probably wouldn't 
            # mess with it unless you have a better way of drawing circle previews that I don't know about. In that case, be my guest. 

            #draw circles
            for i in range(2):
                size = circle_sizes[i]
                group = circle_groups[i]

                if size % 2 == 0: 
                    even_size = True #we need to have an integer center point, so we will not allow even lengths for label objects.
                else: 
                    even_size = False
                
                if even_size: size -= 1 #create smaller odd numbered width to force an integer pixel center.

                circle_left = border_center_x - size // 2
                circle_top = border_center_y - size // 2
                
                R = getattr(self, self.color_groups.get(group))[0]
                G = getattr(self, self.color_groups.get(group))[1]
                B = getattr(self, self.color_groups.get(group))[2]
                    
                border_radius = (size - 1) // 2
                if even_size: border_radius -= 1 #compensate for smaller label size. the cardinal points of this circle will be cut off, but the effect shouldn't be noticeable. It will be certainly less noticeable than a moving center would be.

                getattr(self, self.LBL + group + "Preview").setGeometry(circle_left, circle_top, size, size) #set the size of the label containing the circle
                getattr(self, self.LBL + group + "Preview").setStyleSheet(f'QLabel#lbl{group}Preview {{background-color: rgb({R},{G},{B}); border-radius: {border_radius}px}}') #set the radius of the rounded corners on the label to mimic a circle

        elif group_name in self.preview_groups[self.custom_sprite_preview_group]: #update custom sprite preview
            #there is a bit of nuance in the logic here because multiple parameters can only be valid under certain conditions.
            
            if self.valid_filepath(self.custom_sprite_filepath): #avoids file not found exception
                #enable relevant parameters and clear StyleSheet feedback associated with invalid filepath.
                self.lblCustomSpritePreview.setStyleSheet("") 
                self.lblCustomSpritePreview.setText("")
                self.cbRotateSprite.setEnabled(True) #any sprite with a valid filepath can be rotated.

                background_center_x = self.lblCustomSpriteBackgroundPreview.geometry().center().x() #will serve as constant center for custom sprite preview
                background_center_y = self.lblCustomSpriteBackgroundPreview.geometry().center().y() #not important to distinguish between even and odd centers though because we only have 1 sprite as opposed to 2 circles that share the same center point.
                    
                size = self.custom_sprite_size

                custom_sprite_left = background_center_x - size // 2
                custom_sprite_top = background_center_y - size // 2

                self.lblCustomSpritePreview.setGeometry(custom_sprite_left, custom_sprite_top,size,size) #resize the label containing the custom sprite preveiew according to self.custom_sprite_size
                
                sprite_sheet = QPixmap(self.custom_sprite_filepath)

                sprite_sheet_width = sprite_sheet.width()
                sprite_sheet_height = sprite_sheet.height()

                #decide if sprite sheet is animateable. enable/disable relevent settings
                if sprite_sheet_width % sprite_sheet_height == 0 and sprite_sheet_width != sprite_sheet_height: #sprite sheet is animateable
                    able_to_animate = True
                    self.cbAnimateSprite.setEnabled(True) 
                else:
                    able_to_animate = False
                    self.cbAnimateSprite.setChecked(False) 
                    self.cbAnimateSprite.setEnabled(False)
                    self.animate_sprite = False

                if self.animate_sprite: #able to animate AND animate sprite checkbox checked
                    self.custom_sprite_frames = [] 
                    
                    #take the sprite sheet and slice it into a list of square pixmaps to represent each frame
                    num_frames = sprite_sheet_width // sprite_sheet_height

                    for frame in range(num_frames):
                        pixmap = sprite_sheet.copy(frame * sprite_sheet_height, 0, sprite_sheet_height, sprite_sheet_height)
                        self.custom_sprite_frames.append(pixmap)

                    pixmap = self.custom_sprite_frames[0]
                    self.custom_sprite_current_frame = 1

                elif able_to_animate: #cbAnimateSprite is unchecked. Capture only the first frame for the preview
                    pixmap = sprite_sheet.copy(0,0,sprite_sheet_height, sprite_sheet_height)
                else: #custom sprite filepath points to a non-square image that cannot be used as a sprite sheet
                    pixmap = sprite_sheet #scale image to perfect square
                
                self.lblCustomSpritePreview.setPixmap(pixmap)
            else:
                #create a "no image found" message over the preview
                self.lblCustomSpritePreview.setGeometry(self.lblCustomSpriteBackgroundPreview.geometry())
                self.lblCustomSpritePreview.setStyleSheet('QLabel#lblCustomSpritePreview {background-color: red; border-style: solid; border-width: 16; font: 12pt "Arial Black";}')
                self.lblCustomSpritePreview.setText('NO\n IMAGE\n FOUND')
                

                #disable any objects relevant to the custom sprite except for the filepath
                self.cbRotateSprite.setEnabled(False) #we don't need to set self.cbRotateSprite to unChecked because any valid sprite will be rotateable, so either checked or unchecked will be valid if a valid sprite is loaded.
                self.cbAnimateSprite.setChecked(False)
                self.cbAnimateSprite.setEnabled(False)
                self.animate_sprite = False

                if self.custom_sprite_filepath == self.txtCustomSpriteFilepath.text(): #We want to be sure that the text in self.txtCustomSpriteFilepath points to an invalid or nonexistent png image before we turn the field red.
                    self.txtCustomSpriteFilepath.setStyleSheet('QLineEdit#txtCustomSpriteFilepath {font: 10pt "Arial"; background-color: red}')

            #self.animate_sprite can only be true if an animateable sprite sheet was loaded into the preview already. it is set to false in all other cases.    
            if self.animate_sprite:
                self.btnCycleFrames.setHidden(False) 
                self.btnCycleFrames.setText(f"Cycle Frames ({self.custom_sprite_current_frame}/{len(self.custom_sprite_frames)})")
            else:
                self.btnCycleFrames.setHidden(True)

        elif group_name in self.preview_groups[self.trail_gradient_preview_group]: #update trail color gradient preview.
            #While there are lots and lots of parameters required to construct the trail gradient preview, the actual code to do so packs them in in a neat and satisfying way.
            stop1 = self.slow_color_upper_boundary / 100
            stop2 = self.medium_fast_color_lower_boundary / 100
            stop3 = self.medium_fast_color_upper_boundary / 100
            stop4 = self.very_fast_color_lower_boundary / 100

            slowRGB = str(self.slow_trail_color)
            medRGB = str(self.medium_fast_trail_color)
            fastRGB = str(self.very_fast_trail_color)

            self.lblGradientPreview.setStyleSheet(
                f'''QLabel#lblGradientPreview {{
                    background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:0, 
                        stop:{stop1} rgb{slowRGB}, 
                        stop:{stop2} rgb{medRGB}, 
                        stop:{stop3} rgb{medRGB}, 
                        stop:{stop4} rgb{fastRGB}
                    )
                }}'''
            )

    def update_sens(self): #updates self.sensitivity and performs the logic necessary to connect the hslider with the doublespinbox using a base 10 logarithmic scale. then calls self.config_changed()
        trigger_object_name = self.tabwidgetPage.sender().objectName()
        trigger_object_type = self.get_object_type(trigger_object_name) #gets the type of object by analyzing the prefix of the sender widget's name.

        if trigger_object_type == self.DBLSPIN: #double spinbox was changed. update the position of the hslider
            new_sens_value = round(self.dblspinSensitivity.value(),2)
            new_slider_value = int(round(200 + 100 * (math.log10(new_sens_value)))) #for sens values between 0.01 and 10.0, this formula will return a an integer between 0 and 300
            self.hsliderSensitivity.setValue(new_slider_value)

        elif trigger_object_type == self.HSLIDER: #hslider was moved. update the value of the double spinbox.
            new_slider_value = self.hsliderSensitivity.value()
            new_sens_value = float(round(0.01 * (10 ** (new_slider_value / 100)),2)) #for slider values between 0 and 300, this formula will return a float between 0.01 and 10.0
            self.dblspinSensitivity.setValue(new_sens_value)            

        self.sensitivity = round(self.dblspinSensitivity.value(),2)

        self.config_changed()

    def update_trail_gradient_boundaries(self): #executes the logic necessary to determine whether the configuration of the slow, medium-fast, and veryfast boundaries are valid. attribute versions of these parameters are only updated when the entire configuration of 4 parameters is valid.
        ORDERED_SPINBOXES = (self.spinSlowUpper, self.spinMedLower, self.spinMedUpper, self.spinFastLower) #create tuple as a quick and easy reference to iterate over in a for loop

        if 0 <= ORDERED_SPINBOXES[0].value() <= ORDERED_SPINBOXES[1].value() <= ORDERED_SPINBOXES[2].value() <= ORDERED_SPINBOXES[3].value() <= 100: #Valid settings
            for spinbox in ORDERED_SPINBOXES: #return spinboxes to their normal colors
                spinbox.setStyleSheet(f'QSpinBox#{spinbox.objectName()} {{font: 12pt "Arial";}}')

            self.slow_color_upper_boundary = self.spinSlowUpper.value()
            self.medium_fast_color_lower_boundary = self.spinMedLower.value()
            self.medium_fast_color_upper_boundary = self.spinMedUpper.value()
            self.very_fast_color_lower_boundary = self.spinFastLower.value()

            self.update_preview(self.trail_gradient_preview_group)
        else: #invalid settings. determine which values are invalid and turn their spinboxes red.
            for spinbox in ORDERED_SPINBOXES:
                spinbox_index = ORDERED_SPINBOXES.index(spinbox)

                invalid = False
                for i in range(len(ORDERED_SPINBOXES)):
                    if spinbox_index == i:
                        pass
                    elif spinbox_index < i:
                        if spinbox.value() > ORDERED_SPINBOXES[i].value():
                            invalid = True
                            break
                    elif spinbox_index > i:
                        if spinbox.value() < ORDERED_SPINBOXES[i].value():
                            invalid = True
                            break

                if invalid:
                    spinbox.setStyleSheet(f'QSpinBox#{spinbox.objectName()} {{font: 12pt "Arial"; background-color: red}}')
                else:
                    spinbox.setStyleSheet(f'QSpinBox#{spinbox.objectName()} {{font: 12pt "Arial";}}')

        self.config_changed()
                
    def update_trail_lifetime(self): #updates self.trail_lifetime and calls self.config_changed()
        self.trail_lifetime = round(self.dblspinTrailLifetime.value(),2)
        self.config_changed()

    def update_trail_sample_rate(self): #updates self.trail_sample_rate and calls self.config_changed()
        trigger_object = self.tabwidgetPage.sender()

        if trigger_object == self.comboTrailSampleRate:
            index = self.comboTrailSampleRate.currentIndex()
            
            if index == 5: #custom
                self.spinTrailSampleRate.setEnabled(True)
            else:
                self.spinTrailSampleRate.setEnabled(False)

            if index == 0: #MIN
                self.spinTrailSampleRate.setValue(30)
            elif index == 1: #Low
                self.spinTrailSampleRate.setValue(100)
            elif index == 2: #Medium
                self.spinTrailSampleRate.setValue(250)
            elif index == 3: #High
                self.spinTrailSampleRate.setValue(500)
            elif index == 4: #MAX
                self.spinTrailSampleRate.setValue(1000)

        self.trail_sample_rate = self.spinTrailSampleRate.value()

        self.config_changed()

    def update_trail_thickness(self): #updates self.trail_thickeness and calls self.config_changed()
        self.trail_thickness = self.spinTrailThickness.value()
        self.config_changed()

    def update_velocity_smoothing(self): #updates self.velocity_smoothing and calls self.config_changed()
        self.velocity_smoothing = self.comboVelocitySmoothing.currentIndex()
        self.config_changed()

    def update_wrapping_mode(self): #updates self.wrapping_mode and calls self.config_changed
        self.wrapping_mode = bool(self.comboWrapStyle.currentIndex()) #0 = False = Spawn Center, 1 = True = Wrap Across
        self.config_changed()

    def valid_cursor_boundaries(self, return_boolean=False): #exicutes the logic for determining if the configureation of cursor boundaries is valid. turns spinboxes with invalid values red, and returns a boolean if requested by the function calling it.
        valid = True

        if self.spinLowerX.value() > self.spinUpperX.value():
            valid = False
            self.spinLowerX.setStyleSheet('QSpinBox#spinLowerX {font: 12pt "Arial"; background-color: red;}')
            self.spinUpperX.setStyleSheet('QSpinBox#spinUpperX {font: 12pt "Arial"; background-color: red;}')
        else:
            self.spinLowerX.setStyleSheet('QSpinBox#spinLowerX {font: 12pt "Arial";}')
            self.spinUpperX.setStyleSheet('QSpinBox#spinUpperX {font: 12pt "Arial";}')
        
        if self.spinLowerY.value() > self.spinUpperY.value():
            valid = False
            self.spinLowerY.setStyleSheet('QSpinBox#spinLowerY {font: 12pt "Arial"; background-color: red;}')
            self.spinUpperY.setStyleSheet('QSpinBox#spinUpperY {font: 12pt "Arial"; background-color: red;}')
        else:
            self.spinLowerY.setStyleSheet('QSpinBox#spinLowerY {font: 12pt "Arial";}')
            self.spinUpperY.setStyleSheet('QSpinBox#spinUpperY {font: 12pt "Arial";}')
        
        if return_boolean:
            return valid

    def valid_filepath(self, filepath): #determines, if, given a filepath as an argument, that filepath exists and points to a png file. returns a boolean.
        #honestly, this probably doesn't need to be its own function but it's already written and it works so I'm going to leave it.
        if os.path.exists(filepath) and filepath[-4:] == ".png":
            return True
        else:
            return False

    def valid_hex_color(self, hex_string): #determines if, given a string as an argument, that string represents a valid hex color.
        #knowing my luck, python probably has some built in function for doing this. oh well. I got to build an algorithm and I get to be proud of it.

        #this function assumes all alphabetical characters are uppercase. lowercase alphabetical characters will be considered invalid. 
        #perhaps an unneccesary constraint, but I like the aesthetics of capital letters.
        output = False
        if type(hex_string) == str:
            if len(hex_string) == 6:
                for char in hex_string:
                    if char in self.HEX_CHARS:
                        invalid = False
                    else:
                        invalid = True
                        break
                
                if not invalid: output = True
        
        return output
 
def crash_report(exception_type, exception_value, exception_traceback): #Send a custom crash report to the user if the app encounters and unexpected exception.
    message = QMessageBox()
    message.setWindowTitle('R.I.P Scurry (App Crashed)')
    message.setIcon(QMessageBox.Icon.Critical)
    message.setText('Congratulations, you found a bug! :D\n\nScurry has encountered an unexpected error and needs to close.\n\n' +
                    'Information about the error can be found by clicking the "Show Details" button below. It would be much appreciated if you could send that information to Contemplaytion so he can find the bug and squash it.')
    
    tb_exc = traceback.format_exception(exception_type, exception_value, exception_traceback)
    
    tb_as_string = ''
    for line in tb_exc:
        tb_as_string += line
        
    message.setDetailedText(
        f'Platform: {platform.system()}, {platform.version()} \n' +
        f'Exception Type: {exception_type.__name__} \n' + 
        f'Exception Value: {exception_value}\n' + 
        f'Exception Traceback: {tb_as_string}'
        )
    
    message.exec()
    sys.exit()

def main():
    global scurry_mouse_visualizer_launcher
    
    #set up custom exception handler to pass custom app crash message to user.
    sys.excepthook = crash_report #set up custom crash report widget

    #NOTE:  I didn't realize until very late in the development of this app, as I tried to test the script on different platforms 
    #       on virtual machines, that I needed to manually specify a style for the QApplication in order for the app to look the 
    #       same on cross platform. It was at that moment that I realized that the 'Fusion' style follows your system light and 
    #       dark mode preference, and I discovered how abysmal the dark mode version of the app looks. I've decided to force the 
    #       use of light mode, at least on windows, because I don't know how to on linux.

    if platform.system() == 'Windows':
        force_light_theme = sys.argv + ['-platform', 'windows:darkmode=1']
        app = QApplication(force_light_theme)
    else:
        app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    scurry_mouse_visualizer_launcher = QDialog()
    scurry_mouse_visualizer_launcher.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
    ui = mainUI(scurry_mouse_visualizer_launcher)
    scurry_mouse_visualizer_launcher.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
