#bloc ouverture fichiers

table = Read Table from tab-separated file: "/home/batou/Documents/TAL/Synthèse vocale/dico_UTF8.txt"


nom$ = "../faure"
## il faudra changer le nom faure par le nom de mon enregistrement
son$ = nom$ + ".wav"
grille$ = nom$ + ".TextGrid"

son = Read from file: son$
##permet de préciser où est le milieu du phoneme, ça fait là où l'intersection avec 0 et les intersections montantes
intersections = To PointProcess (zeroes): 1, "yes", "no"
grille = Read from file: grille$



nombre_intervalles = Get number of intervals: 1



##############################################"
phrase_ortho$ = "tsigane vodka parcmètre"

#on fait une condition pour ajouter un espace à la fin de la phrase parceque sinon cela fait un pb dans la boucle while elle ne s'arrete jamais car il faut que longueur phrase = 0 pour couper stoper le while
if right$(phrase_ortho$, 1) != " "
	phrase_ortho$ = phrase_ortho$ + " " 
endif


longueur_phrase = length(phrase_ortho$)

while longueur_phrase > 0
	espace = index(phrase_ortho$, " ")

	premier_mot$ = left$(phrase_ortho$, espace-1)
	phrase_ortho$ = right$(phrase_ortho$, longueur_phrase-espace)

	@phonetisation

	phrase_phon$ =  phrase_phon$ + mot_phon$ + "_"
	longueur_phrase = length(phrase_ortho$)
	pause  'premier_mot$' // 'mot_phon' // 

endwhile

###################################################

procedure phonetisation
	select table
	extraction_ligne = Extract rows where column (text): "orthographe", "is equal to", premier_mot$
	#select extraction_ligne
	mot_phon$ = Get value: 1, "phonetique"
endproc




#######################################################



## le mot_phon$ = "vodka" est supprimé car pris dans le dictionnaire au tout début du programme
longueur_mot = length(phrase_phon$)

for toto from 1 to longueur_mot-1 
	diphone$ = mid$(phrase_phon$,toto,2)
	phoneme1$ = mid$(diphone$,1,1)
	phoneme2$ = mid$(diphone$,2,1)
	
	@extraction_diphone
	pause 'phoneme1$' / 'phoneme2$'
endfor

######################################################

select diphone1
for b from 2 to longueur_mot -1
	plus diphone'b'
endfor

Concatenate
Concatenate with overlap: 0.005
Play





######################################################




procedure extraction_diphone

	for a from 1 to nombre_intervalles -1
		select 'grille'
		phoneme$ = Get label of interval: 1, a
		phoneme_suivant$ = Get label of interval: 1, a+1
		
		#pause le phoneme est : /'phoneme$'/ ('debut_intervalle':'fin_intervalle')
	
		

		if (phoneme$ = phoneme1$ and phoneme_suivant$ = phoneme2$)
			debut_intervalle1 = Get start time of interval: 1, a
			fin_intervalle1 = Get end time of interval: 1, a
			milieu_intervalle1 = (debut_intervalle1+fin_intervalle1)/2
		
			debut_intervalle2 = Get start time of interval: 1, a+1
			fin_intervalle2 = Get end time of interval: 1, a+1
			milieu_intervalle2 = (debut_intervalle2+fin_intervalle2)/2

			select intersections
			index_intersection = Get nearest index: milieu_intervalle1
			milieu_intervalle1 = Get time from index: index_intersection

			## on peut laisser le même nom index_intersection, on écrase index_intersection pour mettre la nouvelle variable
			index_intersection = Get nearest index: milieu_intervalle2
			milieu_intervalle2 = Get time from index: index_intersection
		
			select son
			diphone'toto' = Extract part: milieu_intervalle1, milieu_intervalle2, "rectangular", 1, "no"
			#pause diphone'toto'

		
		
		endif
	
	endfor


pause 'milieu_intervalle1' ............ 'milieu_intervalle2'
endproc
####################################




 
 