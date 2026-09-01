import user
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter, ImageOps
import scipy as sp
from astropy.modeling import models, fitting

image_path = r"C:\Users\leolu\OneDrive\DSA2026\Code\probes\spektrum_1.png"           #WICHTIG!!!!!!!!!!!!
dark_image_path = r"C:\Users\leolu\OneDrive\DSA2026\Code\darks\dark.png"     #WICHTIG!!!!!!!!!!!!

def main():
    

    # Funktion aufrufen, um das Spektrum zu verarbeiten und zu visualisieren.
    filter_image(image_path, dark_image_path)
    process_spectrum_image(image_path)




def filter_image(image_path, dark_image_path):

    with Image.open(dark_image_path) as dark_image, Image.open(image_path) as probe_image:
        # Beide Bilder in Graustufen konvertieren
        dark_gray = dark_image.convert("L")
        probe_gray = probe_image.convert("L")

        size = (probe_image.width, 1)

        probe_image = ImageOps.fit(probe_gray, size)
        dark_image = ImageOps.fit(dark_gray, size)

        # Die Pixelwerte der beiden Bilder in NumPy-Arrays umwandeln
        dark_array = np.array(dark_image, dtype=np.float32)
        probe_array = np.array(probe_image, dtype=np.float32)

        # Subtraktion der Dunkelstromwerte vom Probenbild
        corrected_array = probe_array - dark_array

        # Negative Werte auf 0 setzen (keine negativen Intensitäten)
        corrected_array[corrected_array < 0] = 0

        # Das korrigierte Array wieder in ein Bild umwandeln
        corrected_image = Image.fromarray(corrected_array.astype(np.uint8))

        # Das korrigierte Bild speichern
        corrected_image.save("corrected_probe.png")

def process_spectrum_image(corrected_image_path="corrected_probe.png"):
    # Bild öffnen und verarbeiten
    # Hier wird das Quellbild geladen, das das Spektrum enthält.
    im = Image.open(corrected_image_path)
    # In RGB konvertieren, damit später mit Farbkanälen gearbeitet werden kann.
    # Die extrahierte Einzelzeile in Graustufen umwandeln.
    # So wird aus der Farbinformation eine Intensitätskurve.
    gray_array = np.array(im.convert("L"), dtype=np.uint8)
    # Das Graustufenbild in ein eindimensionales Array umformen.
    y_werte = gray_array.reshape(-1)

    # Pixelpositionen als x-Achse verwenden.
    # Jede Position entspricht einer Wellenlänge im Spektrum.
    x_werte = np.arange(len(y_werte))
    x_werte = Wellenlänge_zu_Pixel(x_werte)  # Umrechnung der Pixelpositionen in Wellenlängen


    fig, ax = plt.subplots()

    #Ohne Fiter 
    #ax.plot(x_werte, y_werte)
    
    
    y_werte = sp.ndimage.gaussian_filter1d(y_werte, sigma=1)  # Glättung der Intensitätskurve mit Gauß-Filter
    ax.plot(x_werte, y_werte, color='blue', label='Smoothed')

    peaks = sp.signal.find_peaks(y_werte, height=50)[0]  # Finden der Peaks in der geglätteten Kurve
    # Peaks in Pixel-Indizes umrechnen zu Wellenlängen für korrekte Position auf der x-Achse
    ax.plot(x_werte[peaks], y_werte[peaks], "x", label='Peaks', color='red')  # Markieren der Peaks im Plot


    ax.set_xlabel("Wellenlänge (nm)")
    ax.set_ylabel("intensity")
    ax.set_title("Spectral Intensity Distribution")
    # Achsengrenzen so setzen, dass der gesamte Bereich sichtbar ist.
    ax.set_xlim(380, 780)
    ax.set_ylim(0, 255)
    
    fig.tight_layout()
    plt.show()

    im.close()

def Wellenlänge_zu_Pixel(pixel_position):

    ergebnisse = user.user(image_path)
    Wellen, los_points = calc_reference(ergebnisse)


    pixel_reference = np.array([Wellen[0], Wellen[1], Wellen[2], Wellen[3], Wellen[4]])
    Wellenlänge_reference = np.array([los_points[0], los_points[1], los_points[2], los_points[3], los_points[4]])

    fit_poly = fitting.LinearLSQFitter()
    model = models.Polynomial1D(degree=1)
    wl_calib = fit_poly(model, pixel_reference, Wellenlänge_reference)
    wavelength = wl_calib(pixel_position)
    return wavelength

def calc_reference(ergebnisse):

    # Berechnung der Referenzwerte basierend auf den ausgewählten Punkten
    x0 = ergebnisse["Maxiumum of order 0"]
    verhaeltnis = ergebnisse["verhaeltnis (pixels/mm)"]
    some_points = ergebnisse["Additional Points"]
    gitterkonstante = ergebnisse["Gitterkonstante (nm)"]
    entfernung = ergebnisse["Entfernung zum Schirm (mm)"]

    wellenlängen = []
    los_points = []

    for point in some_points:
        point = float(point[0])
        e = ((point - x0) / (verhaeltnis)) * 10**-3  # Umrechnung der Pixelposition in m basierend auf dem Verhältnis

        lambda_0 = float(gitterkonstante * 10**-9) * ((e) / (((entfernung*10**-3)**2 + (e)**2)**0.5))  # Berechnung der Wellenlänge für das Maximum der Ordnung 0
        lambda_1 = lambda_0 * 10**9  # Umrechnung der Wellenlänge in nm

        wellenlängen.append(float(lambda_1))  # Hinzufügen der berechneten Wellenlänge zur Liste
        los_points.append(point)  # Hinzufügen der Pixelposition zur Liste der ausgewählten Punkte

    return wellenlängen, los_points  # Rückgabe der Liste der berechneten Wellenlängen und ausgewählten Punkte

if __name__ == "__main__":
    main()