import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread

def selected_points(img, n_points, title):

    while True:
        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.set_title(f"{title} - Select {n_points} points")

        points = plt.ginput(n_points, timeout=0)

        for i, (x, y) in enumerate(points):
            ax.plot(x, y, 'rx')  # Mark the selected point with a red 'x'
            ax.annotate(str(i + 1), (x, y), textcoords="offset points", xytext=(6, 6), color='red')

        fig.canvas.draw()
        plt.show(block=False)
        plt.pause(0.1)  # Allow the plot to update

        antwort = input(f"Are you satisfied with the selected points? (y/n): ").strip().lower()
        plt.close(fig)  # Close the figure after user input

        if antwort in ("j", "ja", "y", "yes"):
            return points
        else:
            print("Please select the points again.")

def pixel_distance(p1, p2):
    #Calculate the Euclidean distance between two points in pixel coordinates.
    return np.abs(p2[0] - p1[0])

def user(bildpfad):
    img = imread(bildpfad)

    p0 = selected_points(img, 1, "Select the first Maxiumum of order 0")
    x0 = p0[0][0]
    print (f"Selected point for Maxiumum of order 0: {p0[0]}")

    p10 = selected_points(img, 2, "Select two points that are 10mm apart")
    dist_10mm = pixel_distance(p10[0], p10[1])
    print(f"Selected points for 10mm distance: {p10[0]}, {p10[1]} with pixel distance: {dist_10mm}")

    verhaeltnis = dist_10mm / 10.0  # Pixel distance per mm

    some_points = selected_points(img, 5, "Select 5 additional points for analysis")

    gitterkonstante = float(input("Enter the Gitterkonstante (in nm): "))
    entfernung = float(input("Enter Entfernung zum Schirm (in mm): "))
    


    ergebnisse = {
        "Maxiumum of order 0": x0,
        "10mm Points": p10,
        "Pixel Distance for 10mm": dist_10mm,
        "verhaeltnis (pixels/mm)": verhaeltnis,
        "Additional Points": some_points,
        "Gitterkonstante (nm)": gitterkonstante,
        "Entfernung zum Schirm (mm)": entfernung
    }


    return ergebnisse

if __name__ == "__main__":
    bildpfad = r"C:\Users\Akademie\Documents\Code\probes\spektrum_1.png" #WICHTG!!!!!
    user(bildpfad)