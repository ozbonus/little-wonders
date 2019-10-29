import os
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageOps, ImageDraw, ImageFont


################################################################################
# SETTINGS


DATA_DIR = pathlib.Path('data')
IMAGES_DIR = pathlib.Path('images') 

# Use you own data.
DATA = DATA_DIR / 'doom2max12948.zip'

# Customize the graphic by making changes here.
HEADER = IMAGES_DIR / 'doom2.png'
INFORM = ['DOOM 2 UV-MAX IN 1:29:48 BY CYBERDEMON 1:29:48',
          'MAPS 01 - 32, USING PRBOOM+ 2.5.1.4 C12',
          'https://www.stream.me/Cyberdemon531, https://www.youtube.com/user/Cyberdemon531']
LENGTH = 35 # Length of the data portion of the figure. Default 30.
LABELS = IMAGES_DIR / 'labels.png'
FOOTER = ['CREATED BY u/OzBonus, ozbonus@gmail.com',
           'https://github.com/ozbonus/little-wonders/tree/master/doom-speedrun-data']

OUTPUT = 'doom2max12948.png'

################################################################################
# GAME AND TIME DATA


COLUMN_NAMES = ['player_health',
                'player_armor',
                'player_momentum',
                'equipped_weapon', 
                'equipped_ammo', 
                'ammo_bullet', 
                'ammo_shell', 
                'ammo_rocket', 
                'ammo_cell', 
                'level_episode_number', 
                'level_map_number', 
                'level_secret_count', 
                'level_total_secrets', 
                'level_kill_count', 
                'level_monster_count', 
                'power_ironfeet', 
                'power_invisibility', 
                'power_invulnerability', 
                'power_light', 
                'power_berserk', 
                'game_tics']


def make_game_df(data):
    """
    Take a CSV file (can be zipped) in the proper format and return a pandas
    DataFrame containing gameplay data.
    """

    # Create the DataFrame.
    game = pd.read_csv(data,
                       skiprows = 2,
                       usecols = [i for i in range(2, 23)],
                       names = COLUMN_NAMES,
                       dtype='object')

    # Find the final row of unknown values and remove everything after.
    # Somtimes ValueLogger will produce some junk data after normal gameplay is
    # over, which appears after the final row of unknown values.
    last = game['game_tics'].eq('?????').last_valid_index()
    game = game.truncate(after=last)

    # Find and remove every row filled with unknown values.
    good_rows = game['player_health'] != '?????'
    game = game[good_rows]

    # Set everything to numeric after the presence of the question marks caused
    # everything to have been cast as strings. Then drop the small number of
    # duplicates made by logging every 27 milliseconds when each game tic takes
    # just over 28 milliseconds. Finally, create a new index starting from zero
    # to make plotting easier.
    # game = game.apply(pd.to_numeric)
    game = game.astype('int64')
    game = game.drop_duplicates()
    game = game.reset_index(drop=True)
    game.at[0, 'player_health'] = 100

    return game


def seconds_to_hms(seconds):
    """
    Take an integer representing a number of seconds and return a string
    formatted in m:s format or h:m:s format if the time is long enough.
    """

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h:
        return f'{h}:{m:02}:{s:02}'
    else:
        return f'{m:02}:{s:02}'


def make_time_df(game_df):
    """
    Take the game DataFrame and create another DataFrame wherein the
    completion times for each map are recorded in the order that they were
    complete. Completion are stored in several ways: as the total number of
    elapsed game tics, the number of seconds (rounded down), and the number
    of seconds in h:m:s format. There are also columns for cumulative time in
    seconds and h:m:s format.
    """

    unique_levels = game_df['level_map_number'].unique()
    times = pd.DataFrame(columns=['level_map_number', 'game_tics'])

    for lvl in unique_levels:
        selection = game_df['level_map_number'] == lvl
        final_row = game_df[selection].iloc[-1]
        times = times.append(final_row[['level_map_number', 'game_tics']])

    times = times.assign(seconds = times['game_tics'] // 35)
    times = times.assign(cum_seconds = times['seconds'].cumsum())
    times = times.assign(hms = times['seconds'].apply(seconds_to_hms))
    times = times.assign(cum_hms = times['cum_seconds'].apply(seconds_to_hms))

    return times


################################################################################
# PLOTTING


def plot_data(game_df, time_df, length):

    # These arrays will be used for selecting columns, labeling, and styling.
    ammo = ['ammo_cell', 'ammo_rocket', 'ammo_shell', 'ammo_bullet']
    powers = ['power_berserk', 'power_invulnerability',
              'power_invisibility', 'power_light', 'power_ironfeet']
    maps = [f'M{m:02} {t}' for (m, t) in time_df[['level_map_number','hms']].values]
    oranges = ['#2D0E01', '#441401', '#5A1B01', '#712201']
    blues = ['#172A47', '#152741', '#13233B', '#111F34', '#0F1B2E']

    fig = plt.figure(figsize=(length, 5),
                    dpi=72,
                    facecolor='black',
                    edgecolor='black',
                    frameon=True)
    plt.rcParams.update({'font.family': 'monospace'})
    plt.subplots_adjust(hspace=0.0)
    spec = fig.add_gridspec(24, 1)

    # This convoluted figure is divided into 24 rows. The ammo plots each span
    # two rows, the power plots each span one row, and the health and armor
    # plot spans 8. There is a final plot that spans all of the rows and is
    # used to mark map completion times across all of the other plots.
    ax0 = fig.add_subplot(spec[0:3,0])
    ax1 = fig.add_subplot(spec[3:6,0])
    ax2 = fig.add_subplot(spec[6:9,0])
    ax3 = fig.add_subplot(spec[9:12,0])
    ax4 = fig.add_subplot(spec[12,0])
    ax5 = fig.add_subplot(spec[13,0])
    ax6 = fig.add_subplot(spec[14,0])
    ax7 = fig.add_subplot(spec[15,0])
    ax8 = fig.add_subplot(spec[16,0])
    ax9 = fig.add_subplot(spec[17:,0])
    ax10 = fig.add_subplot(spec[0:,0])

    for ax in fig.axes:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim(game_df.index.min(), game_df.index.max()+20)
        ax.margins(x=0, y=0)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
    # Ammo plots.
    for i, ax in enumerate(fig.axes[0:4]):
        ax.stackplot(game_df.index, game_df[ammo[i]], colors=['darkorange'])
        ax.set_ylim(0, game_df[ammo[i]].max()*1.1)
        ax.set_facecolor(oranges[i])

    # Powers plots. Very much a hack.
    for i, ax in enumerate(fig.axes[4:9]):
        ax.stackplot(game_df.index, game_df[powers[i]].astype('bool'), colors='seagreen')
        ax.set(facecolor = blues[i])

    # Health and armor plot.
    ax9.stackplot(
        game_df.index, game_df['player_health'],
        game_df['player_armor'],
        colors=['firebrick', 'seagreen'],
        baseline='sym')
    ax9.set(facecolor = 'black')

    ax10.vlines(time_df.index, 0, 1, colors='white', linewidth=1)
    ax10.set_facecolor('none')
    ax10.set_xticks(time_df.index)
    ax10.set_xticklabels(maps)
    ax10.tick_params(labelsize=8, labelcolor='white', labelrotation=90, length=0)

    plt.savefig('fig.png',
                bbox_inches='tight',
                transparent=False,
                facecolor='black',
                dpi=200,
                pad_inches=0)


################################################################################
# TEXT AND IMAGE ASSEMBLY


def prepare_figure(file):
    """
    Rotate and pad 'fig.png' produced elsewhere.
    """

    image = Image.open('fig.png')
    image = image.rotate(270, expand=True)
    image = ImageOps.expand(image, border=(5, 0, 0, 0), fill='black')

    return image


def multiline_writer(text, width, font, size):
    """
    Convert a list of strings into an image, with each element of that list
    given its own line.
    """
    font = ImageFont.truetype(font, size=size)

    line_sizes = (font.getsize(line) for line in text)
    height = sum(s[1] for s in line_sizes)

    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    draw.multiline_text((5, 0),
                        '\n'.join(text),
                        font=font,
                        fill='white',
                        spacing=0)
    
    image = ImageOps.expand(image, border=(0, 0, 0, 10))

    return image


def max_width_total_height(images):
    """
    Return the total height and maximum width of an array of images.
    """

    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    return max_width, total_height


def stack_images(images):
    """
    Take an array of images as input an return a single image wherein each
    image from the array has been stacked vertically, beginning from the top.
    """

    width, height = max_width_total_height(images)
    img = Image.new('RGB', (width, height), color='black')

    x = 0
    y = 0
    
    for i in images:
        img.paste(i, (x, y))
        y = y + i.size[1]

    return img


################################################################################
# MAIN


if __name__ == '__main__':

    game_df = make_game_df(DATA)
    time_df = make_time_df(game_df)
    plot_data(game_df, time_df, LENGTH)

    header = Image.open(HEADER)
    inform = multiline_writer(INFORM, 905, 'DooM.ttf', 18)
    labels = Image.open(LABELS)
    figure = prepare_figure('fig.png')
    footer = multiline_writer(FOOTER, 905, 'DooM.ttf', 14)

    os.remove('fig.png')
    images = (header, inform, labels, figure, footer)

    infographic = stack_images(images)
    infographic.save(OUTPUT)