import parselmouth
import textgrids
import matplotlib.pyplot as plt
from pathlib import Path
from parselmouth.praat import call

extrait = None
debut = None
choix_phrase = None  

def ouverture_fichier(chemin_doc, chemin_resultat):

    global diphones, debut, son, synthese, sound
    son = chemin_doc + 'cocatenation5.wav'
    grille = chemin_doc + "concatenation5.TextGrid"
    synthese = chemin_resultat + "resultat_synthese.wav"

    sound = parselmouth.Sound(son)
    segmentation = textgrids.TextGrid(grille)

    diphones = segmentation['phonemes']
    debut = sound.extract_part(0, 0.01, parselmouth.WindowShape.RECTANGULAR, 1, False)



def dictionnaire_prononciation(chemin_dico):

    global dico
    dico = {}
    with chemin_dico.open('r') as file:
        for line in file:
            key, value = line.strip().split('\t')
            dico[key] = value



def phrase_a_synthetiser():
    """
     Conversion d'une phrase orthographique en phonétique.

    Affiche une liste de phrases disponibles à la synthèse vocale, permet à l'utilisateur de choisir
    une phrase en saisissant un numéro, et convertit la phrase orthographique en phonétique.
    La représentation phonétique est stockée dans la variable globale 'phrase_phonetique'."""


    global phrase_phonetique
    print("Quelle phrase voulez-vous synthétiser ? Vous avez le choix entre les phrases suivantes :\n")
    with open("SyntheseVocale/Doc/phrases.txt", "r") as phrases_file:
        phrases_ortho = phrases_file.readlines()

    for i, phrase in enumerate(phrases_ortho):
        print(f"{i} : {phrase}")

        # Sélection de la phrase à synthétiser

    while True:
        try:
            choix_phrase = int(input("Entrez le numéro de la phrase que vous souhaitez synthétiser : "))
            if 0 <= choix_phrase < len(phrases_ortho):
                break
            else:
                print("Numéro de phrase invalide. Veuillez réessayer.")
        except ValueError:
            print("Veuillez entrer un numéro valide.")
        except Exception as e:
            print(f'Erreur de type : {e}')

    phrase_selectionnee = phrases_ortho[choix_phrase].strip()
    print(f"Vous avez choisi la phrase : {phrase_selectionnee}")

    # Conversion de la phrase orthographique en phonétique

    phrase_phonetique = []
    for mot in phrase_selectionnee.split(" "):
        phrase_phonetique.append(dico.get(mot, ""))
    phrase_phonetique = "".join(phrase_phonetique)
    print(phrase_phonetique)



def extraction_diphones():
    """
    Extrait les diphones du fichier audio en fonction des modifications spécifiées par l'utilisateur.

    Cette fonction guide l'utilisateur dans l'extraction des diphones en lui demandant s'il souhaite
    que la phrase soit interrogative. En fonction de la réponse, elle parcourt les phonèmes de la phrase phonétique,
    extrait les parties correspondantes du son, applique des modifications, et les concatène au fichier audio."""

    global extrait, debut
    diphones_manquants = []

    while True:
        try:
            modification = input("Voulez-vous que la phrase soit interrogative (oui/non): ").lower()
            if modification == "oui":
                for phoneme in range(len(phrase_phonetique)-1):
                    phoneme1 = phrase_phonetique[phoneme]
                    phoneme2 = phrase_phonetique[phoneme+1]

                    for a in range(len(diphones)):
                        b = a + 1
                        if diphones[a].text == phoneme1 and diphones[b].text == phoneme2:
                            milieu_phoneme1 = trouver_milieu_phoneme(diphones[a])
                            milieu_phoneme2 = trouver_milieu_phoneme(diphones[b])
                            extrait = sound.extract_part(milieu_phoneme1, milieu_phoneme2, parselmouth.WindowShape.RECTANGULAR, 1, False)

                            modif_duree(extrait)
                            choix_manipulation_pitch(choix_phrase)

                            debut = debut.concatenate([debut, extrait])
                            break
                        elif a == len(diphones)-1:             ##si des diphones manquants ils ton ajoutés à la liste diphones manquants
                            diphones_manquants.append(phoneme1 + phoneme2)

            elif modification == "non":
                for phoneme in range(len(phrase_phonetique)-1):
                    phoneme1 = phrase_phonetique[phoneme]
                    phoneme2 = phrase_phonetique[phoneme+1]

                    for a in range(len(diphones)):
                        b = a + 1
                        if diphones[a].text == phoneme1 and diphones[b].text == phoneme2:
                            milieu_phoneme1 = trouver_milieu_phoneme(diphones[a])
                            milieu_phoneme2 = trouver_milieu_phoneme(diphones[b])
                            extrait = sound.extract_part(milieu_phoneme1, milieu_phoneme2, parselmouth.WindowShape.RECTANGULAR, 1, False)

                            debut = debut.concatenate([debut, extrait])
                            break
                        elif a == len(diphones)-1:
                            diphones_manquants.append(phoneme1 + phoneme2)

            print(f'diphones manquants {diphones_manquants}')
            break

        except Exception as e:
            print(f"Erreur lors de la modification de la f0 : {e}")
            continue


def choix_manipulation_pitch(choix_phrase):
    """Applique une manipulation de hauteur spécifique en fonction du diphone et de la phrase choisis."""


    mots_interrogatifs_par_phrase = {
        0: ["At", "n_"],
        1: ["le"],
        2: ["n_"],
        3: ["i_"],
        4: ["n_"]
    }

    
    mots_interrogatifs = mots_interrogatifs_par_phrase.get(choix_phrase, []) # Récupération de la liste de mots interrogatifs associée à la choix_phrase actuelle
    if diphones in mots_interrogatifs: # Vérification si le diphone actuel est dans la liste de mots
        manipulation_pitch(0.9)



def trouver_milieu_phoneme(phoneme):
    """trouve milieu des phonemes"""

    milieu_phoneme = phoneme.xmin + (phoneme.xmax - phoneme.xmin) / 2
    return sound.get_nearest_zero_crossing(milieu_phoneme, 1)



def modif_duree(extrait):
    """modification de la durée pour rendre la synthese plus fluide"""

    allongement = 0.5
    manipulation = call(extrait, "To Manipulation", 0.01, 75, 600)
    duration_tier = call(manipulation, "Extract duration tier")
    call(duration_tier, "Remove points between", 0, extrait.duration)
    call(duration_tier, "Add point", extrait.duration / 2, allongement)
    call([manipulation, duration_tier], "Replace duration tier")
    extrait = call(manipulation, "Get resynthesis (overlap-add)")




def manipulation_pitch(hauteur):
    """Manipule la hauteur (fréquence) du signal audio extrait"""

    manipulation = call(extrait, "To Manipulation", 0.01, 75, 600)
    pitch_tier = call(manipulation, "Extract pitch tier")
    call(pitch_tier, "Get number of points")
    call(pitch_tier, "Multiply frequencies", extrait.xmin, extrait.xmax, hauteur)
    call([manipulation, pitch_tier], "Replace pitch tier")
    extrait = call(manipulation, "Get resynthesis (overlap-add)")






def affichage_signal(extrait, chemin_sauvegarde):
    """Affiche du signal audio extrait et le sauvegarde"""

    plt.figure()
    plt.plot(extrait.xs(), extrait.values.T)
    plt.xlabel('time')
    plt.ylabel('amplitude')
    affichage = input("Voulez-vous voir le signal audio ? (oui/non): ").lower()

    if affichage == "oui":
        plt.show()
    else:
        print("Le signal ne sera pas affiché. Il a été sauvegardé dans le fichier Signal")
    plt.savefig(chemin_sauvegarde)  # sauvegarde du signal

def main():
    """Projet de synthétisation de la parole"""

    global debut
    chemin_dico = Path("SyntheseVocale/Doc/dico_UTF8.txt")
    ouverture_fichier('SyntheseVocale/Doc/', 'SyntheseVocale/résultat/')
    dictionnaire_prononciation(chemin_dico)
    phrase_a_synthetiser()
    extraction_diphones()
    debut.save(synthese, parselmouth.SoundFileFormat.WAV)  # enregistrement du fichier
    affichage_signal(extrait, 'SyntheseVocale/Signal/signal.png')



if __name__ == "__main__":
    main()
