import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageOps

data_dir = pathlib.Path('./data/')
images_dir = pathlib.Path('./images/')

# Use your own data.
data = data_dir / 'AddressLogs-10182019-004712.zip'

# Customize the graphic by making changes here.
header = images_dir / 'doom2a.png'
inform = ['Line1', 'Line2', 'etc']
labels = images_dir / 'labels.png'
figure = 'fig.png'
footer = images_dir / 'footer.png'

################################################################################
# DATA PREPARATION
################################################################################

# Define names for pandas to use.
column_names = ['player_health',
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

# Create the pandas DataFrame.
game = pd.read_csv(data,
                   skiprows = 2, # The first two rows are not useful.
                   usecols = [i for i in range(2, 23)], # The timecode columns are not useful.
                   names = column_names)

# Find the final row of unknown values and remove everything after. Somtimes
# ValueLogger will produce some junk data after normal gameplay is over, which
# appears after the final row of unknown values.
last = game['game_tics'].eq('?????').last_valid_index()
game = game.truncate(after=last)

# Find and remove every row filled with unknown values.
good_rows = game['player_health'] != '?????'
game = game[good_rows]

# Set everything to numeric after the presence of the question marks caused
# everything to have been cast as strings. Then drop the small number of
# duplicates made by logging every 27 milliseconds when each game tic takes
# just over 28 milliseconds. Finally, create a new index starting from zero to
# make plotting easier.
game = game.apply(pd.to_numeric)
game = game.drop_duplicates()
game = game.reset_index(drop=True)

# Create a function that takes an integer representing a number of seconds and
# convert it into h:m:s or m:s format, returned as a string.
def seconds_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f'{h}:{m:02}:{s:02}'
    else:
        return f'{m:02}:{s:02}'

# Create a DataFrame for storing level completion times and related information
# in columns holding: level map number, game tics, game tics -> seconds,
# cumulative seconds, h:m:s format, cumulative h:m:s format. Not all of these
# will be used in the final infographic as I designed it.
unique_levels = game['level_map_number'].unique()
times = pd.DataFrame(columns=['level_map_number', 'game_tics'])

for lvl in unique_levels:
    selection = game['level_map_number'] == lvl
    final_row = game[selection].iloc[-1]
    times = times.append(final_row[['level_map_number', 'game_tics']])

times = times.assign(seconds = times['game_tics'] // 35)
times = times.assign(cum_seconds = times['seconds'].cumsum())
times = times.assign(hms = times['seconds'].apply(seconds_to_hms))
times = times.assign(cum_hms = times['cum_seconds'].apply(seconds_to_hms))

################################################################################
# PLOTTING
################################################################################

# These arrays will be used for selecting columns, labeling, and styling.
ammo = ['ammo_cell', 'ammo_rocket', 'ammo_shell', 'ammo_bullet']
powers = ['power_berserk','power_invulnerability','power_invisibility','power_light', 'power_ironfeet']
maps = [f'M{m:02} {t}' for (m, t) in times[['level_map_number','hms']].values]
oranges = ['#2D0E01', '#441401', '#5A1B01', '#712201']
blues = ['#172A47', '#152741', '#13233B', '#111F34', '#0F1B2E']

fig = plt.figure(figsize=(30, 5),
                 dpi=72,
                 facecolor='black',
                 edgecolor='black',
                 frameon=True)
plt.rcParams.update({'font.family': 'monospace'})
plt.subplots_adjust(hspace=0.0)
spec = fig.add_gridspec(24, 1)

# This convoluted figure is divided into 24 rows. The 
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
    ax.set_xlim(game.index.min(), game.index.max()+20)
    ax.margins(x=0, y=0)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
# Ammo plots.
for i, ax in enumerate(fig.axes[0:4]):
    ax.stackplot(game.index, game[ammo[i]], colors=['darkorange'])
    ax.set_ylim(0, game[ammo[i]].max()*1.1)
    ax.set_facecolor(oranges[i])

# Powers plots.
for i, ax in enumerate(fig.axes[4:9]):
    ax.stackplot(game.index, game[powers[i]].astype('bool'), colors='seagreen')
    ax.set(facecolor = blues[i])

# Health and armor plot.
ax9.stackplot(
    game.index, game['player_health'],
    game['player_armor'],
    colors=['firebrick', 'seagreen'],
    baseline='sym')
ax9.set(facecolor = 'black')

ax10.vlines(times.index, 0, 1, colors='white', linewidth=1)
ax10.set_facecolor('none')
ax10.set_xticks(times.index)
ax10.set_xticklabels(maps)
ax10.tick_params(labelsize=8, labelcolor='white', labelrotation=90, length=0)

plt.savefig('fig.png',
            bbox_inches='tight',
            transparent=False,
            facecolor='black',
            dpi=200,
            pad_inches=0)