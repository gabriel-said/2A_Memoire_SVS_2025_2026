from ij import IJ
from ij.text import TextWindow
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij import ImagePlus
import os
import time
from java.lang import Thread
from ij.plugin import WindowOrganizer
from ij.gui import NonBlockingGenericDialog
import glob
import shutil
from ij.measure import ResultsTable
import csv
from ij.measure import Measurements
import shutil
from math import pi
from ij.gui import WaitForUserDialog
from java.awt import Color
from java.io import File
from ij.io import DirectoryChooser

print("============================")
print("DEBUT DU CODE")
print("============================")
def format_time(seconds):     
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return "%02d:%02d:%02d" % (hrs, mins, secs)
global_start = time.time()

#===================Chemin d'accès et d'enregistrement des données=====================================
#Chemin pour le dossier principal
base_folder = "/Users/gabrielsaid/Documents/ENS/2A/Memoire_2A/Data/443_Plan3-P2_AIT3"

# Récupérer le nom du dernier dossier
folder_name = os.path.basename(base_folder)  # --> "0_Plan1-P2_CT1-bAla"

# Chemin pour l'image des noyaux
nuclei_path = os.path.join(base_folder, "nuclei.tif")


#Chemin pour les roi des noyaux issus de Multi Channel Nuclear Analysis
roi_zip_path = os.path.join(base_folder, "Analysis/nucleiRoiSet.zip")

#Chemin pour les autres dossiers et images du dossier
other_folder = os.path.join(base_folder, "other_channels")

# Chemins des autres images
fiber1_path = os.path.join(other_folder, "fiber_1.tif")
fiber2_path = os.path.join(other_folder, "fiber2B_2X.tif")
lactylated_nuclei_path = os.path.join(other_folder, "lactylated_nuclei.tif")

#Chemin pour l'enregistrement des csv et roi
output_folder_V1  = "/Users/gabrielsaid/Documents/ENS/2A/Memoire_2A/Data_csv_roi"
output_folder = "/Users/gabrielsaid/Documents/ENS/2A/Memoire_2A/Data_csv_roi_V2"
save_folder = os.path.join(output_folder, folder_name)
if not os.path.exists(save_folder):
    os.makedirs(save_folder)
    
#Fichier pour les ROi des fibres 1
fiber_1_folder = os.path.join(save_folder, "fiber1")
if not os.path.exists(fiber_1_folder):
    os.makedirs(fiber_1_folder)
    
#Fichier pour les ROi des fibres 2A
fiber_2A_folder = os.path.join(save_folder, "fiber2A")
if not os.path.exists(fiber_2A_folder):
    os.makedirs(fiber_2A_folder)
    
#Fichier pour les ROi des fibres 2B_2X
fiber_2B_2X_folder = os.path.join(save_folder, "fiber2B_2X")
if not os.path.exists(fiber_2B_2X_folder):
    os.makedirs(fiber_2B_2X_folder)
    
#Fichier pour les différents csv
csv_folder = os.path.join(save_folder, "CSV")
if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

#Fichier ZIP contenant les noyaux détectés lors du premier screening
all_nuclei_V1 = os.path.join(output_folder_V1, folder_name, "allnuclei.zip")
    
print("\n===================Initiation du code=====================================")
#===================Pré-requis avant démarrage du code=====================================
# Ferme toutes les fenêtres sans sauvegarder
print("\n===================Fermetures des fênêtres=====================================")
for w in WindowManager.getNonImageWindows():
    if isinstance(w, TextWindow):
        w.close()

# Utilisation du plugins Multi Channel Nuclear Analysis
print("\n===================Lancement de Multi Channel Nuclear Analysis=====================================")

IJ.run("Multi Channel Nuclear Analysis",
       "number=1 open area mean modal min centroid center perimeter feret's add nan redirect=None decimal=3")

# Ferme toutes les fenêtres sans sauvegarder
print("\n===================Fermetures des fênêtres=====================================")
for w in WindowManager.getNonImageWindows():
    if isinstance(w, TextWindow):
        w.close()

# Fermer toutes les fenêtres d'images
while WindowManager.getImageCount() > 0:
    imp = WindowManager.getCurrentImage()
    imp.changes = False  # éviter la demande de sauvegarde
    imp.close()


print("\n===================Création de l'hyperstack=====================================")
# Ouvrir les  images
# Vérifier si les fichiers existent
for path in [nuclei_path, fiber1_path, fiber2_path]:
    if not os.path.exists(path):
        print("⚠️ Fichier introuvable :", path)

# Ouvrir et afficher
nuclei_imp = IJ.openImage(nuclei_path)
if nuclei_imp: 
	nuclei_imp.show() 
	IJ.run ('Brightness/Contrast...')
	WaitForUserDialog ('Mouse clicks needed!', 'Click "Auto" and "Apply" in "B&C" window').show()
	IJ.selectWindow ('B&C')
	IJ.run ('Close')

fiber1_imp = IJ.openImage(fiber1_path)
if fiber1_imp: fiber1_imp.show()

fiber2_imp = IJ.openImage(fiber2_path)
if fiber2_imp: 
	fiber2_imp.show()
	IJ.run ('Brightness/Contrast...')
	WaitForUserDialog ('Mouse clicks needed!', 'Click "Auto" and "Apply" in "B&C" window').show()
	IJ.selectWindow ('B&C')
	IJ.run ('Close')

# Vérifier que toutes les images ont la même taille
w, h = nuclei_imp.getWidth(), nuclei_imp.getHeight()
for imp in [fiber1_imp, fiber2_imp]:
    if imp.getWidth() != w or imp.getHeight() != h:
        print("Les dimensions des images ne correspondent pas !")


# Créer un hyperstack (3 canaux, 1 slice, 1 frame)
IJ.run("Images to Stack", "name=Correction title=[] use")
stack_imp = IJ.getImage()  # récupère le stack créé

# Convertir en hyperstack
IJ.run(stack_imp, "Stack to Hyperstack...", "order=xyzct channels=3 slices=1 frames=1 display=Composite")
hyperstack_imp = IJ.getImage()  # maintenant c'est le hyperstack

# Afficher l'hyperstack
hyperstack_imp.show()
IJ.run("Arrange Channels...")

print("\n===================Ouverture Image noyau et affichage ROI=====================================")    
nuclei_imp = IJ.openImage(nuclei_path)
nuclei_imp.show()
IJ.run ('Brightness/Contrast...')
WaitForUserDialog ('Mouse clicks needed!', 'Click "Auto" and "Apply" in "B&C" window').show()
IJ.selectWindow ('B&C')
IJ.run ('Close')
	
rm = RoiManager.getRoiManager()
if rm is None:
    rm = RoiManager()

rm.reset()  # vider le RoiManager au cas où il y a déjà des ROIs
rm.runCommand("Open", roi_zip_path)


# Nombre de ROI avant import (pour ne modifier que les nouveaux)
initial_count = rm.getCount()

# Charger le ZIP
if os.path.exists(all_nuclei_V1):
    
    # Sauvegarder le nombre initial de ROI
    initial_count = rm.getCount()
    
    # Charger le ZIP
    rm.runCommand("Open", all_nuclei_V1)
    
    # Nombre après import
    final_count = rm.getCount()
    
    # Traiter les nouveaux ROI
    for i in range(initial_count, final_count):
        roi = rm.getRoi(i)
        
        if roi is not None:
            roi.setGroup(5)
            roi.setStrokeColor(Color(255, 0, 255))
            
            new_name = "NEW_%03d" % (i - initial_count + 1)
            rm.rename(i, new_name)
            
            rm.setRoi(roi, i)

else:
    print("Fichier introuvable = pas de noyau en V1 :", all_nuclei_V1)

# Rafraîchir l'affichage
rm.runCommand("Show All")

# Récupérer les fenêtres via WindowManager
def get_window_by_title(title):
    from ij import WindowManager
    for id in WindowManager.getIDList() or []:
        imp = WindowManager.getImage(id)
        if imp.getTitle() == title:
            return imp.getWindow()
    return None

nuclei_window = get_window_by_title(nuclei_imp.getTitle())
hyperstack_window = get_window_by_title(hyperstack_imp.getTitle())

# Positionner les fenêtres correctement
if nuclei_window and hyperstack_window:
    w_window = nuclei_window.getWidth()  # largeur réelle de la fenêtre
    nuclei_window.setLocation(30, 50)   # légèrement décalé du bord gauche
    hyperstack_window.setLocation(50 + w_window, 50)  # juste à droite
else:
    print("Les fenêtres ne sont pas encore créées")


# Activer le synchroniseur de fênetre
IJ.run("Synchronize Windows", "")  # Ouvre la boîte de dialogue

# Afficher le RoiManager
rm.show()        # s'assure qu'il est visible
rm.toFront()     # le met au premier plan


print("\n===================Correction Manuelle des ROI + enregistrement des ROI=====================================")
# Affiche une une boîte non modale pour mettre le script en pause
gd = NonBlockingGenericDialog("Pause pour correction des ROIs")
gd.addMessage("Veuillez corriger vos ROIs manuellement.\nFermez cette fenêtre quand vous avez terminé.")
gd.showDialog()  # ne bloque pas l'interaction avec Fiji

# Boucle d'attente jusqu'à ce que l'utilisateur ferme la boîte
while gd.wasCanceled() == False and gd.wasOKed() == False:
    time.sleep(0.5)  # pause courte pour ne pas surcharger le CPU
  
# --- Récupérer le RoiManager ---
rm = RoiManager.getRoiManager()
if rm is None:
    rm = RoiManager()

# --- Dossier et nom du fichier pour enregistrer les ROIs ---
save_name = "allnuclei.zip"
save_path = os.path.join(save_folder, save_name)

# --- Sauvegarder les ROIs ---
rm.runCommand("Save", save_path)
print("✅ ROIs de tous les noyaux enregistrées dans :", save_path)


def export_rois_par_groupe_robuste():
    rm = RoiManager.getInstance()
    if not rm:
        IJ.log("Erreur : Le ROI Manager doit etre ouvert.")
        return

    # --- CONFIGURATION DES CHEMINS ---
    imp = IJ.getImage()
    save_folder = os.path.join(output_folder, folder_name)

    # 1. On fait une copie de TOUS les ROIs en mémoire
    all_rois = rm.getRoisAsArray()
    if len(all_rois) == 0:
        IJ.log("Le ROI Manager est vide.")
        return

    # 2. On trie les objets ROI par groupe dans un dictionnaire
    # On stocke l'objet ROI lui-même, pas juste son index
    groups = {}
    for roi in all_rois:
        group_id = roi.getGroup()
        if group_id not in groups:
            groups[group_id] = []
        groups[group_id].append(roi)

    # 3. Processus d'exportation (Nettoyage et Sauvegarde)
    for group_id, roi_list in groups.items():
        # Déterminer le nom de dossier et de fichier
        if group_id == 1:
            sub = "fiber1"; name = "fiber1.zip"
        elif group_id == 2:
            sub = "fiber2A"; name = "fiber2A.zip"
        else:
            sub = "fiber2B_2X"; name = "fiber2B_2X.zip"

        final_dir = os.path.join(save_folder, sub)
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)
        
        full_path = os.path.join(final_dir, name)

        # --- ÉTAPE CRUCIALE ---
        # On vide complètement le ROI Manager
        rm.runCommand("Reset") 
        
        # On y ajoute UNIQUEMENT les ROIs de ce groupe
        for r in roi_list:
            rm.addRoi(r)
        
        # Maintenant que le Manager ne contient QUE ce groupe, 
        # la commande Save ne peut pas se tromper.
        rm.runCommand("Save", full_path)
        
        IJ.log("Export reussi : " + name + " (" + str(len(roi_list)) + " ROIs)")

    # 4. Restauration (Optionnel) : On remet tous les ROIs à la fin
    rm.runCommand("Reset")
    for r in all_rois:
        rm.addRoi(r)
    
    IJ.log("--- Operation terminee avec succes ---")

if __name__ in ['__main__', '__builtin__']:
    export_rois_par_groupe_robuste()
        
# Fermer toutes les fenêtres d'images
while WindowManager.getImageCount() > 0:
    imp = WindowManager.getCurrentImage()
    imp.changes = False  # éviter la demande de sauvegarde
    imp.close()
    
# Création des chemins d'accès des zips
fiber1_zip = os.path.join(fiber_1_folder, "fiber1.zip")
fiber2A_zip = os.path.join(fiber_2A_folder, "fiber2A.zip")
fiber2B_2X_zip = os.path.join(fiber_2B_2X_folder, "fiber2B_2X.zip")
    

print("\n===================Mesures des ROI sur l'image des noyaux=====================================")
# --- Fonction pour automatiser la mesure ---
def measure_zip_on_image(image_path, roi_zip_path, results_folder):
    if not os.path.exists(image_path):
        print("Erreur : Image non trouvee : " + image_path)
        return
    if not os.path.exists(roi_zip_path):
        print("Erreur : Zip ROI non trouve : " + roi_zip_path)
        return

    # Ouvrir l'image
    # Ouvrir l'image
    imp = IJ.openImage(image_path)
    if imp is None:
        print("Erreur critique : Impossible d'ouvrir l'image.")
        return
    imp.show()

    # Préparer le RoiManager
    rm = RoiManager.getInstance()
    if rm is None:
        rm = RoiManager()
    rm.reset()

    # Charger le zip de ROIs
    rm.runCommand("Open", roi_zip_path)

    # Activer toutes les mesures disponibles
    IJ.run(imp, "Set Measurements...", 
           "area mean standard min max integrated median skewness kurtosis area_fraction stack display redirect=None decimal=3 shape fit limit redirect=None")

    # Lancer la mesure
    rm.runCommand(imp, "Measure")

    # Sauvegarder les résultats dans un CSV
    rt = ResultsTable.getResultsTable()
    roi_name = os.path.basename(roi_zip_path).replace('.zip','')
    img_name = os.path.basename(image_path).replace('.tif','')
    csv_name = "{}_{}.csv".format(roi_name, img_name)
    csv_path = os.path.join(results_folder, csv_name)
    rt.saveAs(csv_path)
    print("CSV sauvegarde : " + csv_path)

    # Nettoyage
# 1. Dire à ImageJ que l'image n'a pas été modifiée (évite le "Save changes?")
    imp.changes = False 
    imp.close()

    # 2. Vider et fermer la table de résultats sans confirmation
    rt = ResultsTable.getResultsTable()
    rt.reset() # Vide les données
    
    # Trouver la fenêtre Results et la fermer proprement
    from ij import WindowManager
    results_window = WindowManager.getWindow("Results")
    if results_window:
        results_window.close() # .close() sur une fenêtre Results vide ne demande rien

    # 3. Nettoyer le ROI Manager
    rm = RoiManager.getInstance()
    if rm:
        rm.reset()

# Mesure des différents ROi
measure_zip_on_image(nuclei_path, fiber1_zip, csv_folder)
measure_zip_on_image(nuclei_path, fiber2A_zip, csv_folder)
measure_zip_on_image(nuclei_path, fiber2B_2X_zip, csv_folder)

#Fusion des csv des noyaux
# Créer une table vide pour la fusion
table_fusionnee_nuclei = ResultsTable()
# On definit le nom du dossier parent avant la boucle pour etre sur de l'avoir
parent_folder_name = os.path.basename(os.path.dirname(csv_folder))

csv_files = [
    "fiber1_nuclei.csv", 
    "fiber2A_nuclei.csv", 
    "fiber2B_2X_nuclei.csv"
]

files_found = 0

for file_name in csv_files:
    full_path = os.path.join(csv_folder, file_name)
    
    if os.path.exists(full_path):
        rt_temp = ResultsTable.open(full_path)
        files_found += 1
        
        for i in range(rt_temp.size()):
            table_fusionnee_nuclei.incrementCounter()
            table_fusionnee_nuclei.addValue("Sample_ID", parent_folder_name)
            table_fusionnee_nuclei.addValue("Screening", "V2")
            table_fusionnee_nuclei.addValue("Fibre_Group", file_name.replace(".csv", ""))
            
            roi_label = rt_temp.getLabel(i)
            if roi_label:
                table_fusionnee_nuclei.addLabel(roi_label)
            
            for col in range(rt_temp.getLastColumn() + 1):
                label = rt_temp.getColumnHeading(col)
                if label:
                    val = rt_temp.getValueAsDouble(col, i)
                    table_fusionnee_nuclei.addValue(label, val)
    else:
        print("Note : Le fichier " + file_name + " est absent, il sera ignore.")

# Sauvegarde uniquement si on a trouve au moins un fichier
if files_found > 0:
    output_nuclei_file = os.path.join(csv_folder, "nuclei_merged_" + parent_folder_name + ".csv")
    table_fusionnee_nuclei.saveAs(output_nuclei_file)
    print("Fusion terminee (" + str(files_found) + " fichiers identifies).")
else:
    print("Alerte : Aucun fichier CSV n'a ete trouve. Pas de fusion effectuee.")


print("\n===================Mesures des ROI sur l'image des noyaux lactylés=====================================")
# Mesure des différents ROI sur noyaux lactylés
measure_zip_on_image(lactylated_nuclei_path, fiber1_zip, csv_folder)
measure_zip_on_image(lactylated_nuclei_path, fiber2A_zip, csv_folder)
measure_zip_on_image(lactylated_nuclei_path, fiber2B_2X_zip, csv_folder)

#Fusion des csv des noyaux lactylés
# Créer une table vide pour la fusion
table_fusionnee_lactylated_nuclei = ResultsTable()
# On definit le nom du dossier parent avant la boucle pour etre sur de l'avoir
parent_folder_name = os.path.basename(os.path.dirname(csv_folder))

csv_files = [
    "fiber1_lactylated_nuclei.csv", 
    "fiber2A_lactylated_nuclei.csv", 
    "fiber2B_2X_lactylated_nuclei.csv"
]

files_found = 0

for file_name in csv_files:
    full_path = os.path.join(csv_folder, file_name)
    
    if os.path.exists(full_path):
        rt_temp = ResultsTable.open(full_path)
        files_found += 1
        
        for i in range(rt_temp.size()):
            table_fusionnee_lactylated_nuclei.incrementCounter()
            table_fusionnee_lactylated_nuclei.addValue("Sample_ID", parent_folder_name)
            table_fusionnee_lactylated_nuclei.addValue("Screening", "V2")
            table_fusionnee_lactylated_nuclei.addValue("Fibre_Group", file_name.replace(".csv", ""))
            
            roi_label = rt_temp.getLabel(i)
            if roi_label:
                table_fusionnee_lactylated_nuclei.addLabel(roi_label)
            
            for col in range(rt_temp.getLastColumn() + 1):
                label = rt_temp.getColumnHeading(col)
                if label:
                    val = rt_temp.getValueAsDouble(col, i)
                    table_fusionnee_lactylated_nuclei.addValue(label, val)
    else:
        print("Note : Le fichier " + file_name + " est absent, il sera ignore.")

# Sauvegarde uniquement si on a trouve au moins un fichier
if files_found > 0:
    output_lactylated_nuclei_file = os.path.join(csv_folder, "lactylated_nuclei_merged_" + parent_folder_name + ".csv")
    table_fusionnee_lactylated_nuclei.saveAs(output_lactylated_nuclei_file)
    print("Fusion terminee (" + str(files_found) + " fichiers identifies).")
else:
    print("Alerte : Aucun fichier CSV n'a ete trouve. Pas de fusion effectuee.")

global_elapsed = time.time() - global_start

print("============================")
print("FINI")
print("Temps total         :", format_time(global_elapsed))
print("============================")

