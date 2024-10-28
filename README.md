# What is DUF Brewery?
DUF Brewery is a collection of short test scripts (elsewhere called a "cookbook") for [the DUFMan package](https://github.com/MidnightArrowStudios/dufman). It demonstrates how to use DUFMan to import DSON files, used by Daz Studio, into Blender.

You can find them in the `/brews` folder.

# How do I install DUFMan in Blender?
DUFMan is licensed under MIT, but any code that uses Blender's Python API must be licensed under GPL. To avoid the GPL license spreading to DUFMan's codebase, DUFMan must be installed separately from these test scripts. However, this process is fairly painless.

The recommended approach is to install the DUFMan package into an external script directory. The process to do that [is detailed in the Blender documentation](https://docs.blender.org/manual/en/latest/editors/preferences/file_paths.html#script-directories). To summarize:
1. Create a folder on your file system with a `/modules` folder inside it.
2. Copy the DUFMan package (https://github.com/MidnightArrowStudios/dufman) into a folder named `dufman`.
3. Open Blender's preferences menu.
4. Go to the `File Paths` tab.
5. Add the directory you created (not the `/modules` folder, the folder containing it) to the `Script Directories` section.

Now, you should be able to import DUFMan in either the Python console or the text editor.

You can also install DUFMan into the `/scripts/modules` directory in your Blender install directory, but that is not recommended since the default directory is very cluttered and you'll need to reinstall DUFMan every time a new version of Blender is released.

As soon as DUFMan is installed, you should be able to load the Python files located in `duf-brewery` directly into Blender's text editor and run them with minimal tweaks. 

Remember to alter the content directory path to match your own Daz Studio installation!
