# Doom Speedrun Data

This Python script and associated files were created to extract and analyze data from gameplay videos of [*Doom*][1] and [*Doom II*][2]. I got the idea for this from the [*Doom II* episode][3] of [Watch Out for Fireballs][4], a fantastic gaming podcast.

Given data presented in a particular format, this script produces an infographic summarizing a play session of either of these games.

[1]: https://en.wikipedia.org/wiki/Doom_(1993_video_game)
[2]: https://en.wikipedia.org/wiki/Doom_II:_Hell_on_Earth
[3]: http://duckfeed.tv/woff/110
[4]: http://duckfeed.tv/watchoutforfireballs/

# Collecting Your Own Data

The first to collecting data is get a demo file, which is file of recorded player inputs during gameplay. These can be made personally with most versions of the games, or obtained from speedrunning enthusiast websites. The speedruns included in this repository were all obtains from the [COMPETE-N][5] database of speedruns, which seems to be the most popular place to showcase runs of "pure" versions of the games.

After a lot of false starts, I settled on the following programs, and versions thereof, to extract the play data:

* Windows only
* [cndoom 3.0.0 alpha 2][6]
* [Cheat Engine 7.0 64-bit ][7]
* The Cheat Engine table from this repository
* [AddressLogger plugin for Cheat Engine][8]

[5]: https://www.doom.com.hr/
[6]: https://github.com/fx02/cndoom/
[7]: https://github.com/cheat-engine/cheat-engine/
[8]: https://github.com/d-e-x-t-e-r/CheatEngine-AddressLogger

I tried several Doom source ports, but the Address Logger plugin was only able to successfully pull data from the particular one above.

Of course you'll need the original game data files, DOOM.WAD and DOOM2.WAD, which can be purchased from your friendly neighborhood online game storefront.

After installing the programs, get the data from a gameplay demo into `csv` format by following this rather complex procedure:

1. Create a `bat` file that will launch cndoom and run your demo file. For example: `.\cndoom.exe -iwad .\DOOM.WAD -playdemo .\mydemo.lmp`
1. Open Cheat Engine.
1. In Cheat Engine -> Settings -> General Settings, set it to automatically attach to a process named `cndoom.exe`.
1. Open cndoom.
1. In Cheat Engine -> File -> Open File, search for and open `cndoom.CT`.
1. In Cheat Engine -> Settings -> Extra, click "Log Changes to Cheat Table Addresses" and set "Logging Interval" to 27ms.
1. Click "OK" and again search for and open `cndoom.CT`.
1. On the main screen of Cheat Engine, click "Stop AddressLogger". Delete the log files if you want to.
1. Close cndoom.
1. Click "Start AddressLogger".
1. Launch your `bat` file.
1. Click "Stop AddressLogger" after the demo finishes.

You need to set or timer or keep an eye on the game screen, or AddressLogger will record forever.

# Using Your Data

Here are the requirements to run the Python script:

* Python 3.5 or higher.
* Matplotlib
* pandas
* Pillow

The first section of the script, called Settings, provides a simple way to plug in your own data and customize your infographic.

| Variable | Use |
| -------- | --- |
| DATA | Your CSV file, ideally in the default data directory. |
| HEADER | The image you want to be at the top. I've included `doom1.png` and `doom2.png`. |
| INFORM | Text that will be displayed at the top of the graphic. Each item in the list will be given its own line. |
| LENGTH | How far you want the data portion of the infographic to stretch out. |
| LABELS | An image file that labels each plot. Not likely to need changed. |
| FOOTER | Supplementary text at the bottom. Hopefully you will credit me here. |
| OUTPUT | The output file name. |

# Credits

Doom and Doom II were produced by id Software, Inc.

Speedruns are sourced from [COMPETE-N][9] or [The DooMed Speed Demos Archive][10].

I got `DooM.ttf` from [Dafont][12], but there was no attribution information.

Sprite graphics for the labels were provided by [SupremeZanne][11].

[9]: https://www.doom.com.hr/
[10]: http://doomedsda.us/
[11]: https://www.reddit.com/user/SupremoZanne/
[12]: https://www.dafont.com/doom.font