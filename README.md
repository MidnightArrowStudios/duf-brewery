# What is DUF Brewery?
DUF Brewery is a collection of short test scripts (elsewhere called a "cookbook") for [the DUFMan package](https://github.com/MidnightArrowStudios/dufman). It demonstrates how to use DUFMan to import DSON files, used by Daz Studio, into Blender.

You can find them in the `/brews` folder.

Right now, DUFMan is under active development. These scripts are for testing purposes only. They're liable to change, and they aren't suitable as the foundation for a full addon yet. Also, make sure you download the latest version from the repository when trying the scripts since they may rely on bugfixes or features that don't exist in older builds.

# How do I install DUFMan in Blender?
DUFMan is licensed under the MIT license, but any code that uses Blender's Python API must be licensed under the GPL. To avoid the GPL spreading to DUFMan's codebase, DUFMan must be installed separately from these test scripts. However, this process is fairly painless.

The recommended approach is to install the DUFMan package into an external script directory. The process to do that [is detailed in the Blender documentation](https://docs.blender.org/manual/en/latest/editors/preferences/file_paths.html#script-directories). To summarize:
1. Create a new folder on your file system ('/dufman', for instance) and create a '/modules' folder inside that.
2. Download the DUFMan package (https://github.com/MidnightArrowStudios/dufman) into the '/modules' folder.
3. Open Blender's preferences menu and go to the 'File Paths' tab.
4. Add the directory you created in step #1 (not the '/modules' folder, the one that contains it) to the 'Script Directories' section.

Once that's done, you should be able to import DUFMan from either the Python console or the text editor.

You can also install DUFMan into the '/scripts/modules' directory in your Blender install directory, but that's not recommended. The default directory is very cluttered, and every new release of Blender creates a new folder, so you'll have to continually reinstall DUFMan every time a new version comes out.

Once DUFMan is installed, you can load or copy-paste the Python files located in 'duf-brewery/brews' into Blender's text editor and run them with minimal tweaks. Remember to alter the content directory path to match your own Daz Studio installation.
