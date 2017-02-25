from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, BasicTicker
from bokeh.plotting import figure, show
from bokeh.sampledata.periodic_table import elements
from csv import reader
from pandas import options
from matplotlib.colors import Normalize, to_hex
import matplotlib.cm as cm
import argparse
options.mode.chained_assignment = None

#Parse arguments
parser = argparse.ArgumentParser(description='Plot periodic trends as a heat map over the periodic table of elements')
parser.add_argument('filename',type=str,help='Filename (with extension) of CSV-formatted data')
parser.add_argument('--width',type=int,default=1050,help='Width (in pixels) of figure')
parser.add_argument('--palette_choice',type=int,default=0,choices=range(0,4),help='Color palette choice: 0 = Plasma, 1 = Inferno, 2 = Magma, 3 = Viridis')
parser.add_argument('--fill_alpha',type=float,default=0.65,help='Alpha value for color scale (ranges from 0 to 1)')
parser.add_argument('--extended',type=int,choices=range(0,2),help='Keyword for excluding (0) or including (1) the lanthanides and actinides (will automatically enable if lanthanides or actinides are present in the dataset')
parser.add_argument('--cbar_height',type=int,help='Height (in pixels) of color bar')

args = parser.parse_args()
filename = args.filename
width = args.width
palette_choice = args.palette_choice
fill_alpha = args.fill_alpha
extended = args.extended
cbar_height = args.cbar_height

if width < 0:
	raise argparse.ArgumentTypeError("--width must be a positive integer")

if fill_alpha < 0 or fill_alpha > 1:
	raise argparse.ArgumentTypeError("--fill_alpha must be between 0 and 1")

#Assign palette based on input argument
palette_options = ['plasma','inferno','magma','viridis']
if palette_choice == 0:
	cmap = cm.plasma
	bokeh_palette = 'Plasma256'
elif palette_choice == 1:
	cmap = cm.inferno
	bokeh_palette = 'Inferno256'
elif palette_choice == 2:
	cmap = cm.magma
	bokeh_palette = 'Magma256'
elif palette_choice == 3:
	cmap = cm.viridis
	bokeh_palette = 'Viridis256'

#Read in data from CSV file
data_elements = []
data_list = []
for row in reader(open(filename)):
	data_elements.append(row[0])
	data_list.append(row[1])
data = [float(i) for i in data_list]

if len(data) != len(data_elements):
	print("ERROR: Unequal number of atomic elements and data points")

lanthanides = [x.lower() for x in elements["symbol"][56:70].tolist()]
actinides = [x.lower() for x in elements["symbol"][88:102].tolist()]

if args.extended is None:
	for i in range(len(data)):
	    lanthanide_flag = data_elements[i].lower() in lanthanides
	    actinide_flag = data_elements[i].lower() in actinides
	    if lanthanide_flag == True or actinide_flag == True:
	        extended = 1
	        break

#Add new element names and symbols
elements.name[112] = 'Nihomium'
elements.symbol[112] = 'Nh'
elements.name[114] = 'Moscovium'
elements.symbol[114] = 'Mc'
elements.name[116] = 'Tenessine'
elements.symbol[116] = 'Ts'
elements.name[117] = 'Oganesson'
elements.symbol[117] = 'Og'

#Define number of rows
period_label = ["1", "2", "3", "4", "5", "6", "7"]

#Modfiy lanthanides and actinides
if extended == 1:
	period_label.append("blank")
	period_label.append("La")
	period_label.append("Ac")

	count = 0
	for i in range(56,70):
	    elements.period[i] = 'La'
	    elements.group[i] = str(count+4)
	    count += 1

	count = 0
	for i in range(88,102):
	    elements.period[i] = 'Ac'
	    elements.group[i] = str(count+4)
	    count += 1

group_range = [str(x) for x in range(1, 19)]

#Define color map and set color value for blank entries
color_mapper = LinearColorMapper(palette = bokeh_palette, low=min(data), high=max(data))
blank_color = '#c4c4c4'
color_list = []
for i in range(len(elements)):
	color_list.append(blank_color)

#Normalize color values and convert from RGBA to hex
norm = Normalize(vmin = min(data), vmax = max(data))
color_scale = cm.ScalarMappable(norm=norm, cmap=cmap).to_rgba(data,alpha=None)

for i in range(len(data)):
	element_index = elements.symbol[elements.symbol.str.lower() == data_elements[i].lower()].index[0]
	color_list[element_index] = to_hex(color_scale[i])

#Define properties for producing periodic table
source = ColumnDataSource(
    data=dict(
        group=[str(x) for x in elements["group"]],
        period=[str(y) for y in elements["period"]],
        symx=[str(x)+":0.1" for x in elements["group"]],
        numbery=[str(x)+":0.8" for x in elements["period"]],
        sym=elements["symbol"],
        atomic_number=elements["atomic number"],
        type_color=color_list,
    )
)

#Plot the periodic table
p = figure(x_range=group_range, y_range=list(reversed(period_label)),tools='save')
p.plot_width = width
p.outline_line_color = None
p.toolbar_location='above'
p.rect("group", "period", 0.9, 0.9, source=source,
       fill_alpha=fill_alpha, color="type_color")
p.axis.visible = False
text_props = {
    "source": source,
    "angle": 0,
    "color": "black",
    "text_align": "left",
    "text_baseline": "middle"
}
p.text(x="symx", y="period", text="sym",
       text_font_style="bold", text_font_size="15pt", **text_props)
p.text(x="symx", y="numbery", text="atomic_number",
       text_font_size="9pt", **text_props)
color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(desired_num_ticks=10),
	border_line_color=None,label_standoff=6,location=(0,0),orientation='vertical',
    scale_alpha=fill_alpha)

if args.cbar_height is not None:
	color_bar.height = cbar_height

p.add_layout(color_bar,'right')
p.grid.grid_line_color = None
show(p)