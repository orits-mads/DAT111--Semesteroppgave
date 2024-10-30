import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider   #Bytter RadioButtons med Slider
import matplotlib.image as mpimg
import matplotlib.patches as mpatches

#Generater random data for a year
# centervals are values average values for each month
# samedata = false, new data each time program is called
import random
from random import randint
def GenereateRandomYearDataList(intencity:float, seed:int=0) -> list[int]:
    """
    :param intencity: Number specifying size, amplitude
    :param seed: If given, same data with seed is generated
    :return:
    """
    if seed != 0:
        random.seed(seed)
    centervals = [200,150,100, 75,75,75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intencity for x in centervals]
    nox = centervals[0]
    inc = True
    noxList = []
    for index in range(1,365):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(2.0, max(0.5, nox / center ))
        nox =  nox + randint(1,5) / dx if inc else nox - randint( 1, 5) * dx
        nox = max(10, nox)
        noxList.append(nox)
    return noxList

kron_nox_year = GenereateRandomYearDataList(intencity=1.0, seed = 2)
nord_nox_year = GenereateRandomYearDataList(intencity=.3, seed = 1)


#create figure and 3 axis
fig = plt.figure(figsize=(13, 5))

axNok = fig.add_axes((0.05, 0.2, 0.45, 0.75))
axInterval = fig.add_axes((0.1, 0.05, 0.35, 0.05))
axBergen = fig.add_axes((0.5, 0.05, 0.5, 0.9))

axInterval.patch.set_alpha(0.5)

coordinates_Nordnes = (550,320)
coordinates_Kronstad = (900,900)
days_interval = (1,365)
marked_point = (0,0)



def on_day_interval(kvartal):
    global days_interval, marked_point
    axNok.cla()
    days_interval = (1,365)
    if kvartal == '1. Kvartal':
        days_interval = (1,90)
    if kvartal == '2. Kvartal':
        days_interval = (90, 180)
    if kvartal == '3. Kvartal':
        days_interval = (180,270)
    if kvartal == '4. Kvartal':
        days_interval = (270,365)
    marked_point = (0, 0)
    plot_graph()

def on_click(event) :
    global marked_point
    if ax := event.inaxes:
        if ax == axBergen:
            marked_point = (event.xdata, event.ydata)
            plot_graph()

#estimate NOX value based on the two measuring stations
def CalcPointValue(valN, valK):
    distNordnes = math.dist(coordinates_Nordnes, marked_point)
    distKronstad = math.dist(coordinates_Kronstad, marked_point)
    distNordnesKronstad = math.dist(coordinates_Nordnes, coordinates_Kronstad)
    val = (1 - distKronstad /(distKronstad+distNordnes)) * valK  + (1 - distNordnes /(distKronstad+distNordnes))* valN
    val = val * ( distNordnesKronstad / (distNordnes + distKronstad) ) ** 4

    return val

# Make two circles in Nordnes and Kronstad
def draw_circles_stations():
    circle = mpatches.Circle((550,320), 25, color='blue')
    axBergen.add_patch(circle)
    circle = mpatches.Circle((900,900), 25, color='red')
    axBergen.add_patch(circle)

def draw_label_and_ticks():
    num_labels = 12
    xlabels = ['J' ,'F' ,'M' ,'A' ,'M' ,'J', 'J', 'A', 'S', 'O', 'N', 'D']
    xticks = np.linspace(15, 345, num_labels)
    if days_interval[1] == 90:
        xticks = [15,45,75]
        xlabels = ['Jan', 'Feb', 'Mars']
    if days_interval[1] == 180:
        xticks = [15,45,75]
        xlabels = ['April', 'Mai', 'Juni']
    if days_interval[1] == 270:
        xticks = [15, 45, 75]
        xlabels = ['July', 'Aug', 'Sept']
    if days_interval[0] == 270:
        xticks = [15, 45, 75]
        xlabels = ['Okt', 'Nov', 'Des']
    axNok.set_xticks(xticks)
    axNok.set_xticklabels(xlabels)

def plot_graph():
    axNok.cla()
    axBergen.cla()
    nord_nox = nord_nox_year[days_interval[0]:days_interval[1]]
    kron_nox = kron_nox_year[days_interval[0]:days_interval[1]]
    days = len(nord_nox)
    list_days = np.linspace(1, days, days)

    # draw the marked point & the orange graph
    l3 = None
    nox_point = []
    if marked_point != (0,0):
        nox_point = [CalcPointValue(nord_nox[i], kron_nox[i]) for i in range(days)]
        l3, = axNok.plot(list_days, nox_point, 'darkorange')
        circle = mpatches.Circle((marked_point[0], marked_point[1]), 25, color='orange')
        axBergen.add_patch(circle)

    l1, = axNok.plot(list_days, nord_nox, 'blue')
    l2, = axNok.plot(list_days, kron_nox, 'red')
    axNok.set_title("NOX verdier")
    axInterval.set_title("Intervall")

    # Add average NOX value box
    if marked_point != (0,0):
        avg_nordnes = np.mean(nord_nox)
        avg_kronstad = np.mean(kron_nox)
        avg_marked = np.mean(nox_point)
        avg_text = f'Gjennomsnitt NOX:\nNordnes: {avg_nordnes:.1f}\nKronstad: {avg_kronstad:.1f}\nMarkert: {avg_marked:.1f}'
        axNok.text(0.02, 0.98, avg_text, transform=axNok.transAxes, 
                  bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'),
                  verticalalignment='top', fontsize=9)

    lines = [l1, l2] if l3 is None else [l1,l2, l3]
    axNok.legend(lines, ["Nordnes", "Kronstad", "Markert plass"])
    axNok.grid(linestyle='--')
    draw_label_and_ticks()

    #Plot Map of Bergen
    axBergen.axis('off')
    img = mpimg.imread('python/bergen.png')
    img = axBergen.imshow(img)
    axBergen.set_title("Kart Bergen")
    draw_circles_stations();
    plt.draw()

plot_graph()

# Lager en slider for å velge intervall
def create_interval_slider():
    slider = Slider(
        ax=axInterval,
        label='Kvartal',
        valmin=0,
        valmax=4,
        valinit=0,
        valstep=1,
        color='lightblue'
    )
    
    def slider_callback(val):
        quarters = {
            0: (1, 365),    # Hele året
            1: (1, 90),     # 1. kvartal
            2: (90, 180),   # 2. kvartal
            3: (180, 270),  # 3. kvartal
            4: (270, 365)   # 4. kvartal
        }
        global days_interval
        days_interval = quarters[int(val)]
        plot_graph()
        
    slider.on_changed(slider_callback)
    return slider

slider = create_interval_slider()

# noinspection PyTypeChecker
plt.connect('button_press_event', on_click)

plt.show()

