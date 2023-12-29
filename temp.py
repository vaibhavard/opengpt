import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the ellipse function
def ellipse(angle, a, b): 
    return a * np.cos(angle), b * np.sin(angle)

# Create the figure and axis
fig, ax = plt.subplots()

# Set the axis limits
ax.set_xlim(-2, 2)
ax.set_ylim(-1, 1)

# Create a blank line. We will update the line in the animate function
line, = ax.plot([], [], 'b-')

# Initialization function:  plot the background of each frame
def init(): 
    line.set_data([], [])
    return line,

# Animation function. This is called sequentially
def animate(i): 
    angle = np.linspace(0, 2 * np.pi, 100)
    x, y = ellipse(angle, 1, 0.5)
    x, y = x * np.cos(np.radians(i)), y * np.sin(np.radians(i))
    line.set_data(x, y)
    return line,

# Call the animator. blit=True means only re-draw the parts that have changed.
ani = animation.FuncAnimation(fig, animate, init_func=init, frames=360, interval=20, blit=True, repeat=False)
writergif = animation.PillowWriter(fps=30) 
ani.save("a.gif", writer=writergif)


# Close the plot
plt.close(fig)