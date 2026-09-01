import user
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter, ImageOps
import scipy as sp
from astropy.modeling import models, fitting

image_path = r"C:\Users\Akademie\Documents\Code\probes\spektrum_1.png"         # Pfad zum Probenspektrum
dark_image_path = r"C:\Users\Akademie\Documents\Code\darks\dark_1.png"     # Pfad zum Dunkelbild

def main():
    # Hauptfunktion: Bild bearbeiten und Spektrum verarbeiten
    filter_image(image_path, dark_image_path)
    # process the corrected image saved by filter_image
    process_spectrum_image("corrected_probe.png")




def filter_image(image_path, dark_image_path):

    with Image.open(dark_image_path) as dark_image, Image.open(image_path) as probe_image:
        # Dark- und Probebild öffnen und in Graustufen bringen
        dark_gray = dark_image.convert("L")
        probe_gray = probe_image.convert("L")

        size = (probe_image.width, 1)

        probe_image = ImageOps.fit(probe_gray, size)
        dark_image = ImageOps.fit(dark_gray, size)

        # Zeilenbilder in NumPy-Arrays konvertieren
        dark_array = np.array(dark_image, dtype=np.float32)
        probe_array = np.array(probe_image, dtype=np.float32)

        # Dunkelstrom vom Probearray subtrahieren
        corrected_array = probe_array - dark_array

        # Negative Intensitäten auf 0 setzen
        corrected_array[corrected_array < 0] = 0
        
        # Korrigiertes Array in Bild zurückwandeln
        corrected_image = Image.fromarray(corrected_array.astype(np.uint8))

        # Korrigiertes Bild speichern
        corrected_image.save("corrected_probe.png")

def process_spectrum_image(corrected_image_path = "corrected_image_path.png"):
    # Öffnet das korrigierte Bild und extrahiert die Intensitätslinie
    im = Image.open(corrected_image_path)
    # In Graustufen konvertieren, um Intensitäten zu erhalten
    gray_array = np.array(im.convert("L"), dtype=np.uint8)
    # Eindimensionales Intensitätsarray erstellen
    y_werte = gray_array.reshape(-1)

    # Pixelindizes als x-Achse (später in Wellenlänge umgerechnet)
    x_werte = np.arange(len(y_werte))
    x_werte = Wellenlänge_zu_Pixel(x_werte)  # Umrechnung der Pixelpositionen in Wellenlängen
    

    fig, ax = plt.subplots()

    # Plot der geglätteten Intensität
    
    
    y_werte = sp.ndimage.gaussian_filter1d(y_werte, sigma=1)  # Gauß-Glättung
    ax.plot(x_werte, y_werte, color='blue', label='Smoothed')

    peaks = sp.signal.find_peaks(y_werte, height=50)[0]  # Peaks finden
    # Gefundene Peaks als Marker zeichnen
    #ax.plot(x_werte[peaks], y_werte[peaks], "x", label='Peaks', color='red')


    ax.set_xlabel("Wellenlänge (nm)")
    ax.set_ylabel("intensity")
    ax.set_title("Spectral Intensity Distribution")
    # Achsenbereiche setzen
    ax.set_xlim(380, 780)
    ax.set_ylim(23, 255)
    
    fig.tight_layout()
    plt.show()

    im.close()

def Wellenlänge_zu_Pixel(pixel_position):

    # Lade Kalibrierungswerte vom Benutzer-Input und berechne Referenzen
    ergebnisse = user.user(image_path)
    Wellen, los_points = calc_reference(ergebnisse)


    # Wähle Referenzpunkte für die lineare Kalibrierung
    pixel_reference = np.array(los_points[:5])
    Wellenlänge_reference = np.array(Wellen[:5])

    # Lineare Anpassung zur Umrechnung von Pixeln in Wellenlänge
    fit_poly = fitting.LinearLSQFitter()
    model = models.Polynomial1D(degree=1)
    wl_calib = fit_poly(model, pixel_reference, Wellenlänge_reference)
    wavelength = wl_calib(pixel_position)
    return wavelength

def calc_reference(ergebnisse):

    # Berechnet Wellenlängen aus Benutzereingaben (Referenzpunkte)
    x0 = ergebnisse["Maxiumum of order 0"]
    verhaeltnis = ergebnisse["verhaeltnis (pixels/mm)"]
    some_points = ergebnisse["Additional Points"]
    gitterkonstante = ergebnisse["Gitterkonstante (nm)"]
    entfernung = ergebnisse["Entfernung zum Schirm (mm)"]

    wellenlängen = []
    los_points = []

    for point in some_points:
        point = float(point[0])
        # Pixeldifferenz in Meter umrechnen
        e = ((point - x0) / (verhaeltnis)) * 10**-3
        # Wellenlänge aus Gittergleichung (m) und Umrechnung in nm
        lambda_0 = float(gitterkonstante * 10**-9) * ((e) / (((entfernung*10**-3)**2 + (e)**2)**0.5))
        lambda_1 = lambda_0 * 10**9
        wellenlängen.append(float(lambda_1))
        los_points.append(point)

    return wellenlängen, los_points

if __name__ == "__main__":
    main()