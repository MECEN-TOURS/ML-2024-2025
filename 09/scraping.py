"""Description.

Script pour scraper la liste des entreprises du
SP500 via wikipedia.
"""

from requests import get
from bs4 import BeautifulSoup
from dataclasses import dataclass
import json

ADRESSE = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

reponse = get(ADRESSE)
assert reponse.status_code == 200

wiki_soupe = BeautifulSoup(reponse.text, features="lxml")
tables = wiki_soupe.find_all("table", attrs={"id": "constituents", "class": "wikitable"})
assert len(tables) == 1

table, = tables

lignes = table.find_all(
        lambda tag: tag.name == "tr" 
        and any(child.name == "td" for child in tag.children)
        )
assert len(lignes) == 503

@dataclass
class Ligne:
    symbole: str
    lien_nyse: str
    securite: str
    lien_wiki: str
    gics: str
    sous_gics: str
    localisation: str
    date_entree: str
    cik: str
    fondation: str

def genere_ligne(ligne: str) -> Ligne:
    (
        symbole, 
        securite, 
        gics, 
        sous_gics, 
        localisation, 
        date_entree, 
        cik, 
        fondation
    ) = [td.text.strip() for td in ligne.find_all("td")]
    try:
        lien_nyse, lien_wiki, *_ = [lien.attrs["href"] for lien in ligne.find_all("a")]
    except ValueError:
        lien_nyse = "NA"
        lien_wiki = "NA"
        print("Problème d'extraction de lien:")
        print(f"On attendait 3 liens, mais {len([lien.attrs['href'] for lien in ligne.find_all('a')])} récupérés")
        print([lien.attrs['href'] for lien in ligne.find_all('a')])
    return Ligne(
        symbole=symbole,
        lien_nyse=lien_nyse,
        securite=securite,
        lien_wiki="https://en.wikipedia.org" + lien_wiki,
        gics=gics,
        sous_gics=sous_gics,
        localisation=localisation,
        date_entree=date_entree,
        cik=cik,
        fondation=fondation
    )

entreprises = [genere_ligne(ligne) for ligne in lignes]

with open("entreprises.json", "w") as fichier:
    fichier.write(json.dumps([entreprise.__dict__ for entreprise in entreprises]))
