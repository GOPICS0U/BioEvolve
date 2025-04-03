"""
BioEvolve - Simulateur d'Évolution Biologique
Un jeu de simulation d'évolution basé sur des principes biologiques rigoureux

Ce simulateur implémente les mécanismes fondamentaux de l'évolution biologique :
- Variation génétique (mutations, recombinaison)
- Sélection naturelle et sélection sexuelle
- Dérive génétique et flux génétique
- Spéciation (allopatrique, sympatrique, etc.)
- Coévolution et interactions écologiques
- Régulation génétique et gènes architectes
- Endosymbiose et transfert horizontal de gènes
"""

import numpy as np
import pygame
import random
import math
import threading
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set, Any, Callable
import uuid
import json
import os
import itertools
import sys

# Importer les modules d'évolution avancés
try:
    from evolution_events import (
        EvolutionaryMechanism, SpeciationMode, EvolutionaryEvent,
        EvolutionaryRegistry, EvolutionaryPressure, EvolutionaryPressureSystem
    )
    from genetic_regulation import (
        GeneType, RegulatoryElement, ArchitectGene,
        GeneRegulatoryNetwork, create_gene_regulatory_network
    )
    from coevolution import (
        InteractionType, CoevolutionaryRelationship,
        CoevolutionSystem, create_coevolution_system
    )
    ADVANCED_EVOLUTION_ENABLED = True
except ImportError as e:
    print(f"Modules d'évolution avancés non disponibles: {e}")
    ADVANCED_EVOLUTION_ENABLED = False

# Constantes globales
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60
SIMULATION_SPEED = 5.0  # Multiplicateur de vitesse de simulation

# Paramètres de la carte
MAP_WIDTH = 6400   # Largeur de la carte (pixels)
MAP_HEIGHT = 3600  # Hauteur de la carte (pixels)
CELL_SIZE = 25     # Taille d'une cellule (pixels)
CHUNK_SIZE = 16    # Nombre de cellules par chunk pour le chargement dynamique

# Paramètres des cycles environnementaux
DAY_LENGTH = 1200  # Durée d'un jour complet en secondes de simulation
YEAR_LENGTH = 43200  # Durée d'une année en secondes de simulation (36 jours)
SEASONS_COUNT = 4  # Nombre de saisons (printemps, été, automne, hiver)
SEASON_LENGTH = YEAR_LENGTH / SEASONS_COUNT  # Durée d'une saison

# Configuration des contrôles (touches par défaut)
class Controls:
    """Classe pour gérer les contrôles personnalisables du jeu."""
    def __init__(self):
        # Touches de déplacement de la caméra
        self.move_left = pygame.K_LEFT
        self.move_right = pygame.K_RIGHT
        self.move_up = pygame.K_UP
        self.move_down = pygame.K_DOWN

        # Touches de zoom
        self.zoom_in = pygame.K_PLUS
        self.zoom_out = pygame.K_MINUS

        # Touches d'interaction
        self.pause = pygame.K_SPACE
        self.center_map = pygame.K_c
        self.follow_organism = pygame.K_f
        self.take_screenshot = pygame.K_s

    def save_to_file(self, filename="controls.json"):
        """Sauvegarde la configuration des contrôles dans un fichier."""
        # Convertir les touches en chaînes pour la sérialisation
        controls_dict = {
            "move_left": self.move_left,
            "move_right": self.move_right,
            "move_up": self.move_up,
            "move_down": self.move_down,
            "zoom_in": self.zoom_in,
            "zoom_out": self.zoom_out,
            "pause": self.pause,
            "center_map": self.center_map,
            "follow_organism": self.follow_organism,
            "take_screenshot": self.take_screenshot
        }

        try:
            with open(filename, 'w') as f:
                json.dump(controls_dict, f)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des contrôles: {e}")
            return False

    def load_from_file(self, filename="controls.json"):
        """Charge la configuration des contrôles depuis un fichier."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    controls_dict = json.load(f)

                # Mettre à jour les contrôles
                self.move_left = controls_dict.get("move_left", pygame.K_LEFT)
                self.move_right = controls_dict.get("move_right", pygame.K_RIGHT)
                self.move_up = controls_dict.get("move_up", pygame.K_UP)
                self.move_down = controls_dict.get("move_down", pygame.K_DOWN)
                self.zoom_in = controls_dict.get("zoom_in", pygame.K_PLUS)
                self.zoom_out = controls_dict.get("zoom_out", pygame.K_MINUS)
                self.pause = controls_dict.get("pause", pygame.K_SPACE)
                self.center_map = controls_dict.get("center_map", pygame.K_c)
                self.follow_organism = controls_dict.get("follow_organism", pygame.K_f)
                self.take_screenshot = controls_dict.get("take_screenshot", pygame.K_s)

                return True
            return False
        except Exception as e:
            print(f"Erreur lors du chargement des contrôles: {e}")
            return False

# Initialisation des contrôles
CONTROLS = Controls()
# Essayer de charger les contrôles personnalisés
CONTROLS.load_from_file()

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class BiomeType(Enum):
    OCEAN = 0
    DEEP_OCEAN = 1
    SHALLOW_WATER = 2
    CORAL_REEF = 3
    BEACH = 4
    GRASSLAND = 5
    SAVANNA = 6
    FOREST = 7
    RAINFOREST = 8
    SWAMP = 9
    MOUNTAIN = 10
    MOUNTAIN_FOREST = 11
    DESERT = 12
    DESERT_HILLS = 13
    TUNDRA = 14
    ICE = 15
    VOLCANIC = 16
    RIVER = 17
    LAKE = 18
    
class ResourceType(Enum):
    SUNLIGHT = 0
    WATER = 1
    MINERALS = 2
    OXYGEN = 3
    CO2 = 4
    ORGANIC_MATTER = 5

class OrganismType(Enum):
    UNICELLULAR = 0
    PLANT = 1
    HERBIVORE = 2
    CARNIVORE = 3
    OMNIVORE = 4

class TaxonomicRank(Enum):
    """Classification taxonomique hiérarchique des organismes."""
    DOMAIN = 0      # Domaine (Bacteria, Archaea, Eukarya)
    KINGDOM = 1     # Règne (Animalia, Plantae, Fungi, etc.)
    PHYLUM = 2      # Embranchement
    CLASS = 3       # Classe
    ORDER = 4       # Ordre
    FAMILY = 5      # Famille
    GENUS = 6       # Genre
    SPECIES = 7     # Espèce

class Taxonomy:
    """Système de classification taxonomique pour les organismes."""

    # Préfixes et suffixes pour la génération de noms taxonomiques
    DOMAIN_NAMES = {
        OrganismType.UNICELLULAR: ["Bacteria", "Archaea", "Protista"],
        OrganismType.PLANT: ["Plantae"],
        OrganismType.HERBIVORE: ["Animalia"],
        OrganismType.CARNIVORE: ["Animalia"],
        OrganismType.OMNIVORE: ["Animalia"]
    }

    KINGDOM_NAMES = {
        OrganismType.UNICELLULAR: ["Monera", "Protista", "Chromista"],
        OrganismType.PLANT: ["Plantae", "Chlorobionta", "Viridiplantae"],
        OrganismType.HERBIVORE: ["Animalia", "Metazoa"],
        OrganismType.CARNIVORE: ["Animalia", "Metazoa"],
        OrganismType.OMNIVORE: ["Animalia", "Metazoa"]
    }

    # Préfixes pour les noms de phylum
    PHYLUM_PREFIXES = {
        OrganismType.UNICELLULAR: ["Micro", "Nano", "Cyano", "Chloro", "Chromo", "Rhizo", "Actino", "Bacillo", "Spiro"],
        OrganismType.PLANT: ["Bryo", "Pterido", "Angio", "Gymno", "Chloro", "Rhodo", "Phyco", "Myco"],
        OrganismType.HERBIVORE: ["Arthro", "Echino", "Chordo", "Mollu", "Anne", "Nema", "Platy", "Pori"],
        OrganismType.CARNIVORE: ["Arthro", "Echino", "Chordo", "Mollu", "Anne", "Nema", "Platy", "Pori"],
        OrganismType.OMNIVORE: ["Arthro", "Echino", "Chordo", "Mollu", "Anne", "Nema", "Platy", "Pori"]
    }

    # Suffixes pour les noms de phylum
    PHYLUM_SUFFIXES = {
        OrganismType.UNICELLULAR: ["bacteria", "phyta", "mycota", "plasma", "protista"],
        OrganismType.PLANT: ["phyta", "flora", "bionta", "mycota", "thallophyta"],
        OrganismType.HERBIVORE: ["poda", "dermata", "zoa", "morpha", "sca", "fera"],
        OrganismType.CARNIVORE: ["poda", "dermata", "zoa", "morpha", "sca", "fera"],
        OrganismType.OMNIVORE: ["poda", "dermata", "zoa", "morpha", "sca", "fera"]
    }

    # Préfixes pour les noms de classe
    CLASS_PREFIXES = {
        OrganismType.UNICELLULAR: ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Acido", "Thermo", "Methano", "Halo"],
        OrganismType.PLANT: ["Mono", "Di", "Gymno", "Angio", "Lyco", "Fili", "Bryo", "Hepato"],
        OrganismType.HERBIVORE: ["Mamma", "Avi", "Reptil", "Amphi", "Insect", "Arach", "Diplo", "Cephalo"],
        OrganismType.CARNIVORE: ["Mamma", "Avi", "Reptil", "Amphi", "Insect", "Arach", "Diplo", "Cephalo"],
        OrganismType.OMNIVORE: ["Mamma", "Avi", "Reptil", "Amphi", "Insect", "Arach", "Diplo", "Cephalo"]
    }

    # Suffixes pour les noms de classe
    CLASS_SUFFIXES = {
        OrganismType.UNICELLULAR: ["bacteriae", "phyceae", "mycetes", "monadea", "plasmodea"],
        OrganismType.PLANT: ["opsida", "phyceae", "mycetes", "atae", "phytina"],
        OrganismType.HERBIVORE: ["lia", "iformes", "ida", "acea", "ata", "ina"],
        OrganismType.CARNIVORE: ["lia", "iformes", "ida", "acea", "ata", "ina"],
        OrganismType.OMNIVORE: ["lia", "iformes", "ida", "acea", "ata", "ina"]
    }

    # Préfixes pour les noms d'ordre
    ORDER_PREFIXES = {
        OrganismType.UNICELLULAR: ["Rhodo", "Chloro", "Cyano", "Flavo", "Nitro", "Sulfo", "Ferro", "Aceto"],
        OrganismType.PLANT: ["Faba", "Rosa", "Lilia", "Orchi", "Astera", "Poales", "Lamia", "Ranuncu"],
        OrganismType.HERBIVORE: ["Carni", "Herbi", "Omni", "Insecti", "Frugi", "Pisci", "Plankti", "Detrito"],
        OrganismType.CARNIVORE: ["Carni", "Herbi", "Omni", "Insecti", "Frugi", "Pisci", "Plankti", "Detrito"],
        OrganismType.OMNIVORE: ["Carni", "Herbi", "Omni", "Insecti", "Frugi", "Pisci", "Plankti", "Detrito"]
    }

    # Suffixes pour les noms d'ordre
    ORDER_SUFFIXES = {
        OrganismType.UNICELLULAR: ["ales", "ineae", "anae", "aria", "ida"],
        OrganismType.PLANT: ["ales", "ineae", "anae", "aria", "ida"],
        OrganismType.HERBIVORE: ["formes", "morpha", "odea", "oidea", "acea"],
        OrganismType.CARNIVORE: ["formes", "morpha", "odea", "oidea", "acea"],
        OrganismType.OMNIVORE: ["formes", "morpha", "odea", "oidea", "acea"]
    }

    # Préfixes pour les noms de famille
    FAMILY_PREFIXES = {
        OrganismType.UNICELLULAR: ["Bacill", "Strept", "Staph", "Clostr", "Pseud", "Actin", "Mycob", "Rhiz"],
        OrganismType.PLANT: ["Ros", "Fab", "Poac", "Aster", "Orchid", "Rubi", "Euphorb", "Lili"],
        OrganismType.HERBIVORE: ["Felid", "Canid", "Bovid", "Cervid", "Equid", "Lepor", "Mur", "Sciur"],
        OrganismType.CARNIVORE: ["Felid", "Canid", "Ursid", "Mustel", "Hyaen", "Viverr", "Procyon", "Otari"],
        OrganismType.OMNIVORE: ["Hominid", "Suid", "Ursid", "Corvid", "Formic", "Vespert", "Mur", "Sciur"]
    }

    # Suffixes pour les noms de famille
    FAMILY_SUFFIXES = {
        OrganismType.UNICELLULAR: ["aceae", "idae", "oideae", "eae", "inae"],
        OrganismType.PLANT: ["aceae", "idae", "oideae", "eae", "inae"],
        OrganismType.HERBIVORE: ["idae", "inae", "eae", "ini", "ina"],
        OrganismType.CARNIVORE: ["idae", "inae", "eae", "ini", "ina"],
        OrganismType.OMNIVORE: ["idae", "inae", "eae", "ini", "ina"]
    }

    # Préfixes pour les noms de genre
    GENUS_PREFIXES = {
        OrganismType.UNICELLULAR: ["Bacill", "Strept", "Staph", "Clostr", "Pseud", "Actin", "Mycob", "Rhiz",
                                  "Azot", "Nitro", "Therm", "Halo", "Methano", "Sulfo", "Ferro", "Acido"],
        OrganismType.PLANT: ["Quercus", "Pinus", "Acer", "Salix", "Rosa", "Lilium", "Tulipa", "Orchis",
                            "Malus", "Pyrus", "Citrus", "Solanum", "Triticum", "Zea", "Oryza", "Bambusa"],
        OrganismType.HERBIVORE: ["Bos", "Ovis", "Capra", "Cervus", "Equus", "Lepus", "Mus", "Sciurus",
                                "Elephas", "Giraffa", "Hippopotamus", "Rhinoceros", "Macropus", "Phascolarctos"],
        OrganismType.CARNIVORE: ["Felis", "Panthera", "Canis", "Vulpes", "Ursus", "Mustela", "Hyaena", "Viverra",
                                "Aquila", "Falco", "Buteo", "Crocodylus", "Alligator", "Varanus"],
        OrganismType.OMNIVORE: ["Homo", "Pan", "Gorilla", "Pongo", "Sus", "Ursus", "Corvus", "Rattus",
                               "Gallus", "Anas", "Anser", "Testudo", "Trachemys", "Iguana"]
    }

    # Racines pour les noms d'espèces
    SPECIES_ROOTS = {
        OrganismType.UNICELLULAR: ["coccus", "bacillus", "spirillum", "vibrio", "flagellum", "cilium", "plasma", "thrix"],
        OrganismType.PLANT: ["folia", "flora", "petala", "stamen", "radix", "caulis", "semen", "spore"],
        OrganismType.HERBIVORE: ["dentis", "cornua", "pellis", "ungula", "rostrum", "cauda", "oculus", "auris"],
        OrganismType.CARNIVORE: ["dentis", "cornua", "pellis", "ungula", "rostrum", "cauda", "oculus", "auris"],
        OrganismType.OMNIVORE: ["dentis", "cornua", "pellis", "ungula", "rostrum", "cauda", "oculus", "auris"]
    }

    # Adjectifs pour les noms d'espèces
    SPECIES_ADJECTIVES = {
        OrganismType.UNICELLULAR: ["alba", "rubra", "flava", "viridis", "nigra", "magna", "parva", "longa",
                                  "brevis", "rotunda", "ovalis", "acuta", "obtusa", "gracilis", "robusta"],
        OrganismType.PLANT: ["alba", "rubra", "flava", "viridis", "nigra", "magna", "parva", "longa",
                            "brevis", "rotunda", "ovalis", "acuta", "obtusa", "gracilis", "robusta"],
        OrganismType.HERBIVORE: ["major", "minor", "maximus", "minimus", "robustus", "gracilis", "agilis",
                                "velox", "tardus", "ferus", "domesticus", "montanus", "aquaticus", "terrestris"],
        OrganismType.CARNIVORE: ["ferox", "rapax", "vorax", "atrox", "magnus", "robustus", "agilis",
                                "velox", "ferus", "sylvestris", "montanus", "aquaticus", "terrestris"],
        OrganismType.OMNIVORE: ["sapiens", "habilis", "erectus", "robustus", "agilis", "velox",
                               "domesticus", "ferus", "sylvestris", "montanus", "aquaticus", "terrestris"]
    }

    # Dictionnaire pour stocker les taxonomies générées
    taxonomies = {}

    @classmethod
    def generate_taxonomy(cls, organism_type: OrganismType, parent_taxonomy_id=None, mutation_traits=None, species_id=None):
        """Génère une taxonomie complète pour un organisme."""
        taxonomy = {}

        # Si un parent est fourni, hériter de sa taxonomie jusqu'à un certain niveau
        if parent_taxonomy_id and parent_taxonomy_id in cls.taxonomies:
            parent_taxonomy = cls.taxonomies[parent_taxonomy_id]

            # Déterminer le niveau de divergence taxonomique en fonction des mutations
            divergence_level = cls._calculate_divergence_level(mutation_traits)

            # Copier les niveaux taxonomiques supérieurs du parent
            for rank in TaxonomicRank:
                if rank.value < divergence_level:
                    taxonomy[rank] = parent_taxonomy.get(rank, cls._generate_rank_name(rank, organism_type))

        # Générer les niveaux manquants
        for rank in TaxonomicRank:
            if rank not in taxonomy:
                taxonomy[rank] = cls._generate_rank_name(rank, organism_type)

        # Générer un identifiant unique pour cette taxonomie
        taxonomy_id = str(uuid.uuid4())
        cls.taxonomies[taxonomy_id] = taxonomy

        # Enregistrer l'espèce dans le registre global si un species_id est fourni
        if species_id:
            try:
                # Importer le registre des espèces
                from species_registry import global_species_registry, OrganismType as RegistryOrganismType

                # Convertir notre type d'organisme en type compatible avec le registre
                registry_type = RegistryOrganismType(organism_type.value)

                # Générer un nom scientifique complet (genre + espèce)
                scientific_name = f"{taxonomy[TaxonomicRank.GENUS]} {taxonomy[TaxonomicRank.SPECIES]}"

                # Générer un nom commun basé sur les caractéristiques
                common_name_parts = []

                # Ajouter un préfixe basé sur le type d'organisme
                type_prefixes = {
                    OrganismType.UNICELLULAR: ["Micro", "Bacté", "Proto"],
                    OrganismType.PLANT: ["Fleur", "Herbe", "Arbre", "Mousse"],
                    OrganismType.HERBIVORE: ["Brouteur", "Mangeur", "Herbier"],
                    OrganismType.CARNIVORE: ["Chasseur", "Prédateur", "Carnassier"],
                    OrganismType.OMNIVORE: ["Fourrageur", "Mangeur", "Omnivore"]
                }

                # Ajouter un suffixe basé sur des caractéristiques physiques
                physical_suffixes = {
                    OrganismType.UNICELLULAR: ["coque", "bacille", "spirille", "amibe"],
                    OrganismType.PLANT: ["feuille", "tige", "racine", "fleur"],
                    OrganismType.HERBIVORE: ["cornes", "sabots", "dents", "queue"],
                    OrganismType.CARNIVORE: ["griffes", "crocs", "mâchoires", "serres"],
                    OrganismType.OMNIVORE: ["mains", "doigts", "dents", "yeux"]
                }

                # Générer un nom commun aléatoire
                prefix = random.choice(type_prefixes.get(organism_type, ["Créature"]))
                suffix = random.choice(physical_suffixes.get(organism_type, ["commun"]))

                # Ajouter une variation aléatoire
                variations = ["des plaines", "des montagnes", "des forêts", "des marais",
                             "des océans", "des déserts", "du nord", "du sud", "géant",
                             "minuscule", "rapide", "lent", "coloré", "pâle"]
                variation = random.choice(variations)

                common_name = f"{prefix} {suffix} {variation}"

                # Déterminer l'espèce parente si elle existe
                parent_species_id = None
                if parent_taxonomy_id:
                    # Chercher l'espèce parente dans les organismes existants
                    # Cette logique dépend de comment les species_id sont stockés
                    parent_species_id = species_id.split('_')[0] if '_' in species_id else None

                # Enregistrer l'espèce
                global_species_registry.register_species(
                    species_id=species_id,
                    scientific_name=scientific_name,
                    common_name=common_name,
                    organism_type=registry_type,
                    parent_species_id=parent_species_id
                )
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de l'espèce: {e}")

        return taxonomy_id

    @classmethod
    def _calculate_divergence_level(cls, mutation_traits):
        """Calcule le niveau de divergence taxonomique en fonction des mutations."""
        if not mutation_traits:
            return TaxonomicRank.SPECIES.value

        # Nombre de mutations significatives
        mutation_count = mutation_traits.get('count', 0)
        # Importance des mutations (0-1)
        mutation_significance = mutation_traits.get('significance', 0.5)

        # Calculer le niveau de divergence
        if mutation_count > 10 and mutation_significance > 0.8:
            return TaxonomicRank.PHYLUM.value  # Divergence majeure - nouveau phylum
        elif mutation_count > 8 and mutation_significance > 0.7:
            return TaxonomicRank.CLASS.value  # Nouvelle classe
        elif mutation_count > 6 and mutation_significance > 0.6:
            return TaxonomicRank.ORDER.value  # Nouvel ordre
        elif mutation_count > 4 and mutation_significance > 0.5:
            return TaxonomicRank.FAMILY.value  # Nouvelle famille
        elif mutation_count > 2 and mutation_significance > 0.3:
            return TaxonomicRank.GENUS.value  # Nouveau genre
        else:
            return TaxonomicRank.SPECIES.value  # Nouvelle espèce uniquement

    @classmethod
    def _generate_rank_name(cls, rank: TaxonomicRank, organism_type: OrganismType):
        """Génère un nom pour un rang taxonomique spécifique."""
        if rank == TaxonomicRank.DOMAIN:
            return random.choice(cls.DOMAIN_NAMES.get(organism_type, ["Incertae"]))

        elif rank == TaxonomicRank.KINGDOM:
            return random.choice(cls.KINGDOM_NAMES.get(organism_type, ["Sedis"]))

        elif rank == TaxonomicRank.PHYLUM:
            prefix = random.choice(cls.PHYLUM_PREFIXES.get(organism_type, ["Proto"]))
            suffix = random.choice(cls.PHYLUM_SUFFIXES.get(organism_type, ["phyta"]))
            return prefix + suffix

        elif rank == TaxonomicRank.CLASS:
            prefix = random.choice(cls.CLASS_PREFIXES.get(organism_type, ["Neo"]))
            suffix = random.choice(cls.CLASS_SUFFIXES.get(organism_type, ["morpha"]))
            return prefix + suffix

        elif rank == TaxonomicRank.ORDER:
            prefix = random.choice(cls.ORDER_PREFIXES.get(organism_type, ["Crypto"]))
            suffix = random.choice(cls.ORDER_SUFFIXES.get(organism_type, ["ales"]))
            return prefix + suffix

        elif rank == TaxonomicRank.FAMILY:
            prefix = random.choice(cls.FAMILY_PREFIXES.get(organism_type, ["Neo"]))
            suffix = random.choice(cls.FAMILY_SUFFIXES.get(organism_type, ["idae"]))
            return prefix + suffix

        elif rank == TaxonomicRank.GENUS:
            # Les genres commencent par une majuscule
            return random.choice(cls.GENUS_PREFIXES.get(organism_type, ["Novum"]))

        elif rank == TaxonomicRank.SPECIES:
            # Les espèces sont en minuscules et peuvent être composées
            root = random.choice(cls.SPECIES_ROOTS.get(organism_type, ["novum"]))
            adj = random.choice(cls.SPECIES_ADJECTIVES.get(organism_type, ["commune"]))

            # 50% de chance d'avoir un nom composé
            if random.random() < 0.5:
                return root + adj.lower()
            else:
                return adj.lower()

    @classmethod
    def get_scientific_name(cls, taxonomy_id):
        """Retourne le nom scientifique complet (genre + espèce)."""
        if taxonomy_id not in cls.taxonomies:
            return "Incertae sedis"

        taxonomy = cls.taxonomies[taxonomy_id]
        genus = taxonomy.get(TaxonomicRank.GENUS, "Novum")
        species = taxonomy.get(TaxonomicRank.SPECIES, "ignotum")

        return f"{genus} {species}"

    @classmethod
    def get_full_taxonomy(cls, taxonomy_id):
        """Retourne la taxonomie complète sous forme de dictionnaire."""
        if taxonomy_id not in cls.taxonomies:
            return {rank.name: "Incertae sedis" for rank in TaxonomicRank}

        return {rank.name: cls.taxonomies[taxonomy_id].get(rank, "Incertae sedis") for rank in TaxonomicRank}

    @classmethod
    def get_common_name(cls, taxonomy_id, organism_type):
        """Génère un nom commun basé sur la taxonomie et le type d'organisme."""
        if taxonomy_id not in cls.taxonomies:
            return "Organisme inconnu"

        taxonomy = cls.taxonomies[taxonomy_id]

        # Éléments pour construire un nom commun
        descriptors = {
            OrganismType.UNICELLULAR: ["Microbe", "Bactérie", "Protiste", "Microorganisme"],
            OrganismType.PLANT: ["Plante", "Herbe", "Arbre", "Fleur", "Mousse", "Algue"],
            OrganismType.HERBIVORE: ["Herbivore", "Brouteur", "Ruminant", "Rongeur"],
            OrganismType.CARNIVORE: ["Carnivore", "Prédateur", "Chasseur", "Rapace"],
            OrganismType.OMNIVORE: ["Omnivore", "Fouisseur", "Opportuniste", "Charognard"]
        }

        adjectives = {
            OrganismType.UNICELLULAR: ["minuscule", "microscopique", "unicellulaire", "simple", "primitif"],
            OrganismType.PLANT: ["verdoyant", "feuillu", "épineux", "fleuri", "grimpant", "rampant"],
            OrganismType.HERBIVORE: ["paisible", "vigilant", "rapide", "lent", "massif", "agile"],
            OrganismType.CARNIVORE: ["féroce", "rusé", "rapide", "puissant", "agile", "nocturne"],
            OrganismType.OMNIVORE: ["adaptable", "intelligent", "curieux", "social", "solitaire"]
        }

        habitats = {
            OrganismType.UNICELLULAR: ["des eaux", "du sol", "des marais", "des sources chaudes"],
            OrganismType.PLANT: ["des forêts", "des prairies", "des montagnes", "des marais", "des déserts"],
            OrganismType.HERBIVORE: ["des plaines", "des forêts", "des montagnes", "des marais", "des savanes"],
            OrganismType.CARNIVORE: ["des forêts", "des montagnes", "des plaines", "des océans", "des rivières"],
            OrganismType.OMNIVORE: ["des forêts", "des plaines", "des montagnes", "des côtes", "des marais"]
        }

        # Construire le nom commun
        descriptor = random.choice(descriptors.get(organism_type, ["Créature"]))
        adjective = random.choice(adjectives.get(organism_type, ["étrange"]))
        habitat = random.choice(habitats.get(organism_type, ["inconnu"]))

        # Différentes structures de noms
        name_structures = [
            f"{descriptor} {adjective}",
            f"{descriptor} {adjective} {habitat}",
            f"{descriptor} {habitat}",
            f"{adjective.capitalize()} {descriptor} {habitat}"
        ]

        return random.choice(name_structures)

class Gene:
    """Représente un gène qui code pour un trait spécifique."""
    def __init__(self, gene_id: str, value: float, mutation_rate: float = 0.01):
        self.gene_id = gene_id
        self.value = value  # Valeur entre 0 et 1
        self.mutation_rate = mutation_rate
        self.dominance = random.random()  # Caractère dominant ou récessif
        self.epistasis = {}  # Interactions avec d'autres gènes
        self.pleiotropy = []  # Effets sur plusieurs traits
        self.expression_level = random.random()  # Niveau d'expression du gène

    def mutate(self) -> 'Gene':
        """Crée une copie mutée du gène avec un modèle plus réaliste de mutations."""
        # Copie de base
        new_gene = Gene(self.gene_id, self.value, self.mutation_rate)
        new_gene.dominance = self.dominance
        new_gene.epistasis = self.epistasis.copy()
        new_gene.pleiotropy = self.pleiotropy.copy()
        new_gene.expression_level = self.expression_level

        # Déterminer si une mutation se produit
        if random.random() < self.mutation_rate:
            # Types de mutations possibles
            mutation_types = [
                "point",       # Mutation ponctuelle (changement de valeur)
                "regulatory",  # Mutation régulatrice (expression)
                "dominance",   # Changement de dominance
                "epistatic",   # Changement d'interaction avec d'autres gènes
                "pleiotropic", # Changement d'effets multiples
                "meta"         # Mutation du taux de mutation lui-même
            ]

            # Sélectionner aléatoirement un ou plusieurs types de mutations
            num_mutations = random.choices([1, 2, 3], weights=[0.85, 0.13, 0.02])[0]
            selected_mutations = random.sample(mutation_types, min(num_mutations, len(mutation_types)))

            # Appliquer les mutations sélectionnées
            for mutation_type in selected_mutations:
                if mutation_type == "point":
                    # Distribution de mutation plus réaliste
                    # La plupart des mutations sont petites, quelques-unes sont plus importantes
                    mutation_size = random.choices(
                        [random.gauss(0, 0.02), random.gauss(0, 0.1), random.gauss(0, 0.3)],
                        weights=[0.7, 0.25, 0.05]
                    )[0]
                    new_gene.value = max(0, min(1, self.value + mutation_size))

                elif mutation_type == "regulatory":
                    # Mutation du niveau d'expression
                    regulatory_change = random.gauss(0, 0.1)
                    new_gene.expression_level = max(0, min(1, self.expression_level + regulatory_change))

                elif mutation_type == "dominance":
                    # Mutation de la dominance
                    dominance_change = random.gauss(0, 0.1)
                    new_gene.dominance = max(0, min(1, self.dominance + dominance_change))

                elif mutation_type == "epistatic":
                    # Mutation des interactions avec d'autres gènes
                    if random.random() < 0.5 and self.epistasis:
                        # Modifier une interaction existante
                        target_gene = random.choice(list(self.epistasis.keys()))
                        interaction_change = random.gauss(0, 0.2)
                        new_gene.epistasis[target_gene] = max(-1, min(1, self.epistasis.get(target_gene, 0) + interaction_change))
                    else:
                        # Ajouter une nouvelle interaction
                        new_target = f"gene_{random.randint(0, 10)}_{random.randint(0, 10)}"
                        new_gene.epistasis[new_target] = random.uniform(-0.5, 0.5)

                elif mutation_type == "pleiotropic":
                    # Mutation des effets multiples
                    if random.random() < 0.5 and self.pleiotropy:
                        # Modifier un effet existant
                        if self.pleiotropy:
                            effect_index = random.randint(0, len(self.pleiotropy) - 1)
                            trait, strength = self.pleiotropy[effect_index]
                            new_strength = max(-1, min(1, strength + random.gauss(0, 0.2)))
                            new_gene.pleiotropy[effect_index] = (trait, new_strength)
                    else:
                        # Ajouter un nouvel effet
                        possible_traits = ["metabolism", "speed", "strength", "immunity", "learning"]
                        new_trait = random.choice(possible_traits)
                        new_strength = random.uniform(-0.3, 0.3)
                        new_gene.pleiotropy.append((new_trait, new_strength))

                elif mutation_type == "meta":
                    # Mutation du taux de mutation lui-même
                    meta_change = random.gauss(0, 0.005)
                    # Les taux de mutation très élevés sont généralement désavantageux
                    # mais un certain niveau de variabilité est bénéfique
                    if new_gene.mutation_rate + meta_change > 0.1 and random.random() < 0.8:
                        # Tendance à réduire les taux de mutation très élevés
                        meta_change = -abs(meta_change)

                    new_gene.mutation_rate = max(0.0001, min(0.2, self.mutation_rate + meta_change))

            return new_gene
        else:
            # Pas de mutation, retourner une copie exacte
            return new_gene

class Chromosome:
    """Représente un chromosome contenant plusieurs gènes."""
    def __init__(self, genes: Dict[str, Gene] = None):
        self.genes = genes or {}
    
    def add_gene(self, gene: Gene):
        """Ajoute un gène au chromosome."""
        self.genes[gene.gene_id] = gene
    
    def mutate(self) -> 'Chromosome':
        """Crée une copie mutée du chromosome."""
        new_chromosome = Chromosome()
        for gene_id, gene in self.genes.items():
            new_chromosome.add_gene(gene.mutate())
        return new_chromosome
    
    @staticmethod
    def combine(chromosome1: 'Chromosome', chromosome2: 'Chromosome') -> 'Chromosome':
        """Combine deux chromosomes par recombinaison génétique."""
        new_chromosome = Chromosome()
        all_gene_ids = set(chromosome1.genes.keys()) | set(chromosome2.genes.keys())
        
        for gene_id in all_gene_ids:
            # Crossing-over aléatoire
            if gene_id in chromosome1.genes and gene_id in chromosome2.genes:
                if random.random() < 0.5:
                    new_chromosome.add_gene(chromosome1.genes[gene_id].mutate())
                else:
                    new_chromosome.add_gene(chromosome2.genes[gene_id].mutate())
            elif gene_id in chromosome1.genes:
                new_chromosome.add_gene(chromosome1.genes[gene_id].mutate())
            else:
                new_chromosome.add_gene(chromosome2.genes[gene_id].mutate())
        
        return new_chromosome

class Genome:
    """Représente le génome complet d'un organisme."""
    def __init__(self, chromosomes: List[Chromosome] = None):
        self.chromosomes = chromosomes or []
    
    def add_chromosome(self, chromosome: Chromosome):
        """Ajoute un chromosome au génome."""
        self.chromosomes.append(chromosome)
    
    def get_gene_value(self, gene_id: str) -> float:
        """Récupère la valeur effective d'un gène (en tenant compte de la dominance)."""
        gene_values = []
        gene_dominances = []
        
        for chromosome in self.chromosomes:
            for chrom_gene_id, gene in chromosome.genes.items():
                if chrom_gene_id == gene_id:
                    gene_values.append(gene.value)
                    gene_dominances.append(gene.dominance)
        
        if not gene_values:
            return 0.5  # Valeur par défaut si le gène n'existe pas
        
        # Expression génétique basée sur la dominance
        if len(gene_values) == 1:
            return gene_values[0]
        else:
            # Moyenne pondérée par la dominance
            total_dominance = sum(gene_dominances)
            if total_dominance == 0:
                return sum(gene_values) / len(gene_values)
            
            weighted_value = sum(value * dominance for value, dominance in zip(gene_values, gene_dominances)) / total_dominance
            return weighted_value
    
    @staticmethod
    def random_genome(gene_count: int = 100, chromosome_count: int = 23) -> 'Genome':
        """Crée un génome aléatoire avec des gènes et chromosomes spécifiés."""
        genome = Genome()
        genes_per_chromosome = max(1, gene_count // chromosome_count)
        
        # Créer des gènes fondamentaux pour différentes caractéristiques
        base_genes = [
            # Métabolisme
            "metabolism_efficiency", "energy_storage", "waste_processing",
            # Mobilité
            "speed", "agility", "strength",
            # Sensorialité
            "vision", "hearing", "smell", "touch", "taste",
            # Reproduction
            "fertility", "maturation_rate", "offspring_count",
            # Défense/Attaque
            "immune_system", "toxin_resistance", "offense", "defense",
            # Intelligence
            "learning_capacity", "memory", "problem_solving",
            # Adaptation
            "temperature_tolerance", "pressure_tolerance", "radiation_tolerance"
        ]
        
        # Distribution des gènes sur les chromosomes
        for i in range(chromosome_count):
            chromosome = Chromosome()
            
            # Ajouter des gènes fondamentaux au premier chromosome
            if i == 0:
                for gene_id in base_genes:
                    gene = Gene(gene_id, random.random())
                    chromosome.add_gene(gene)
            
            # Ajouter d'autres gènes aléatoires
            for j in range(genes_per_chromosome):
                gene_id = f"gene_{i}_{j}"
                if gene_id not in base_genes:  # Éviter les doublons
                    gene = Gene(gene_id, random.random())
                    chromosome.add_gene(gene)
            
            genome.add_chromosome(chromosome)
        
        return genome
    
    def mutate(self) -> 'Genome':
        """Crée une copie mutée du génome."""
        new_genome = Genome()
        for chromosome in self.chromosomes:
            new_genome.add_chromosome(chromosome.mutate())
        return new_genome
    
    @staticmethod
    def reproduce(genome1: 'Genome', genome2: 'Genome') -> 'Genome':
        """Combine deux génomes pour produire un nouvel individu avec un modèle plus réaliste de reproduction."""
        new_genome = Genome()

        # Vérifie que les génomes ont le même nombre de chromosomes
        min_chromosomes = min(len(genome1.chromosomes), len(genome2.chromosomes))

        # Probabilité d'anomalies chromosomiques (rare)
        chromosomal_anomaly = random.random() < 0.02

        # Possibilité de duplication chromosomique (très rare)
        chromosome_duplication = random.random() < 0.005

        # Possibilité de délétion chromosomique (très rare)
        chromosome_deletion = random.random() < 0.005 and min_chromosomes > 1

        # Reproduction normale avec crossing-over et recombinaison
        for i in range(min_chromosomes):
            if chromosome_deletion and i == random.randint(0, min_chromosomes - 1):
                # Sauter ce chromosome (délétion)
                continue

            # Recombinaison chromosomique avec crossing-over
            new_chromosome = Chromosome.combine(genome1.chromosomes[i], genome2.chromosomes[i])

            # Possibilité de duplication de ce chromosome
            if chromosome_duplication and i == random.randint(0, min_chromosomes - 1):
                # Ajouter deux copies (duplication)
                new_genome.add_chromosome(new_chromosome)
                new_genome.add_chromosome(new_chromosome.mutate())  # Légère variation
            else:
                # Ajout normal
                new_genome.add_chromosome(new_chromosome)

        # Ajoute les chromosomes supplémentaires du plus grand génome
        if len(genome1.chromosomes) > min_chromosomes:
            for i in range(min_chromosomes, len(genome1.chromosomes)):
                # Possibilité de mutation accrue aux extrémités du génome
                if random.random() < 0.2:  # 20% de chance de mutation accrue
                    # Créer une copie avec taux de mutation temporairement augmenté
                    temp_chromosome = Chromosome()
                    for gene_id, gene in genome1.chromosomes[i].genes.items():
                        mutated_gene = Gene(gene_id, gene.value, gene.mutation_rate * 2)
                        mutated_gene.dominance = gene.dominance
                        temp_chromosome.add_gene(mutated_gene)
                    new_genome.add_chromosome(temp_chromosome.mutate())
                else:
                    new_genome.add_chromosome(genome1.chromosomes[i].mutate())
        elif len(genome2.chromosomes) > min_chromosomes:
            for i in range(min_chromosomes, len(genome2.chromosomes)):
                # Même logique pour le second parent
                if random.random() < 0.2:
                    temp_chromosome = Chromosome()
                    for gene_id, gene in genome2.chromosomes[i].genes.items():
                        mutated_gene = Gene(gene_id, gene.value, gene.mutation_rate * 2)
                        mutated_gene.dominance = gene.dominance
                        temp_chromosome.add_gene(mutated_gene)
                    new_genome.add_chromosome(temp_chromosome.mutate())
                else:
                    new_genome.add_chromosome(genome2.chromosomes[i].mutate())

        # Anomalies chromosomiques rares (translocations, inversions)
        if chromosomal_anomaly and len(new_genome.chromosomes) >= 2:
            # Sélectionner deux chromosomes aléatoires pour l'anomalie
            idx1, idx2 = random.sample(range(len(new_genome.chromosomes)), 2)

            # Types d'anomalies possibles
            anomaly_type = random.choice(["translocation", "inversion", "fusion"])

            if anomaly_type == "translocation":
                # Échange de segments entre chromosomes
                chrom1, chrom2 = new_genome.chromosomes[idx1], new_genome.chromosomes[idx2]

                # Sélectionner des gènes aléatoires à échanger
                if chrom1.genes and chrom2.genes:
                    genes1 = list(chrom1.genes.keys())
                    genes2 = list(chrom2.genes.keys())

                    if genes1 and genes2:
                        # Échanger un segment aléatoire
                        swap_count = min(len(genes1), len(genes2), random.randint(1, 3))
                        swap_genes1 = random.sample(genes1, swap_count)
                        swap_genes2 = random.sample(genes2, swap_count)

                        # Effectuer l'échange
                        for g1, g2 in zip(swap_genes1, swap_genes2):
                            chrom1.genes[g1], chrom2.genes[g2] = chrom2.genes[g2], chrom1.genes[g1]

            elif anomaly_type == "inversion":
                # Inversion d'un segment dans un chromosome
                chrom = new_genome.chromosomes[idx1]
                if len(chrom.genes) >= 3:
                    genes = list(chrom.genes.keys())
                    # Sélectionner un segment à inverser
                    segment_size = random.randint(2, min(len(genes), 5))
                    start_idx = random.randint(0, len(genes) - segment_size)
                    segment = genes[start_idx:start_idx + segment_size]

                    # Inverser le segment
                    inverted_segment = segment[::-1]
                    for i, gene_id in enumerate(segment):
                        chrom.genes[gene_id], chrom.genes[inverted_segment[i]] = chrom.genes[inverted_segment[i]], chrom.genes[gene_id]

            elif anomaly_type == "fusion":
                # Fusion de deux chromosomes
                if len(new_genome.chromosomes) > 2:  # Garder au moins 2 chromosomes
                    chrom1, chrom2 = new_genome.chromosomes[idx1], new_genome.chromosomes[idx2]

                    # Créer un nouveau chromosome fusionné
                    fused_chrom = Chromosome()
                    for gene_id, gene in chrom1.genes.items():
                        fused_chrom.add_gene(gene)
                    for gene_id, gene in chrom2.genes.items():
                        if gene_id not in fused_chrom.genes:
                            fused_chrom.add_gene(gene)

                    # Remplacer les deux chromosomes par le chromosome fusionné
                    new_genome.chromosomes[idx1] = fused_chrom
                    new_genome.chromosomes.pop(idx2)

        return new_genome

class Phenotype:
    """Représente l'expression physique du génome d'un organisme."""
    def __init__(self, genome: Genome):
        self.genome = genome
        
        # Traits métaboliques
        self.metabolism_rate = self._calculate_trait("metabolism_efficiency", 0.3, 2.0)
        self.energy_capacity = self._calculate_trait("energy_storage", 50, 500)
        self.waste_tolerance = self._calculate_trait("waste_processing", 0.2, 0.8)
        
        # Traits de mobilité
        self.max_speed = self._calculate_trait("speed", 0, 10)
        self.agility = self._calculate_trait("agility", 0, 1)
        self.strength = self._calculate_trait("strength", 0.1, 2.0)
        
        # Traits sensoriels
        self.vision_range = self._calculate_trait("vision", 0, 50)
        self.hearing_range = self._calculate_trait("hearing", 0, 40)
        self.smell_sensitivity = self._calculate_trait("smell", 0, 1)
        
        # Traits de reproduction
        self.fertility = self._calculate_trait("fertility", 0, 1)
        self.maturation_time = self._calculate_trait("maturation_rate", 10, 100, inverse=True)
        self.max_offspring = math.ceil(self._calculate_trait("offspring_count", 1, 20))
        
        # Traits de défense/attaque
        self.immune_strength = self._calculate_trait("immune_system", 0, 1)
        self.toxin_resistance = self._calculate_trait("toxin_resistance", 0, 1)
        self.attack_power = self._calculate_trait("offense", 0, 10)
        self.defense_power = self._calculate_trait("defense", 0, 10)
        
        # Traits d'intelligence
        self.learning_rate = self._calculate_trait("learning_capacity", 0, 1)
        self.memory_capacity = self._calculate_trait("memory", 0, 1)
        self.problem_solving = self._calculate_trait("problem_solving", 0, 1)
        
        # Traits d'adaptation
        self.temperature_range = self._calculate_trait("temperature_tolerance", 10, 50)
        self.pressure_tolerance = self._calculate_trait("pressure_tolerance", 1, 10)
        self.radiation_resistance = self._calculate_trait("radiation_tolerance", 0, 1)
        
        # Traits physiques dérivés
        self.size = self._calculate_size()
        self.color = self._calculate_color()
        self.lifespan = self._calculate_lifespan()
        
        # Traits de comportement
        self.aggression = self._calculate_trait_from_combination(["offense", "strength"], [0.7, 0.3], 0, 1)
        self.sociability = self._calculate_trait_from_combination(["problem_solving", "learning_capacity"], [0.5, 0.5], 0, 1)
    
    def _calculate_trait(self, gene_id: str, min_value: float, max_value: float, inverse: bool = False) -> float:
        """Calcule la valeur d'un trait phénotypique à partir d'un gène."""
        gene_value = self.genome.get_gene_value(gene_id)
        if inverse:
            gene_value = 1 - gene_value
        return min_value + gene_value * (max_value - min_value)
    
    def _calculate_trait_from_combination(self, gene_ids: List[str], weights: List[float], min_value: float, max_value: float) -> float:
        """Calcule un trait à partir d'une combinaison pondérée de plusieurs gènes avec interactions complexes."""
        combined_value = 0
        total_weight = sum(weights)

        # Protection contre la division par zéro
        if total_weight <= 0:
            # Si les poids sont tous nuls, utiliser des poids égaux
            weights = [1.0] * len(gene_ids)
            total_weight = float(len(gene_ids))

        # Collecter les valeurs et propriétés des gènes impliqués
        gene_data = []
        for i, gene_id in enumerate(gene_ids):
            # Récupérer la valeur de base du gène
            gene_value = self.genome.get_gene_value(gene_id)

            # Chercher le gène dans tous les chromosomes pour obtenir ses propriétés
            gene_obj = None
            for chromosome in self.genome.chromosomes:
                if gene_id in chromosome.genes:
                    gene_obj = chromosome.genes[gene_id]
                    break

            # Si le gène est trouvé, collecter ses propriétés
            if gene_obj:
                gene_data.append({
                    'id': gene_id,
                    'value': gene_value,
                    'weight': weights[i] / total_weight,
                    'expression': getattr(gene_obj, 'expression_level', 1.0),
                    'epistasis': getattr(gene_obj, 'epistasis', {}),
                    'pleiotropy': getattr(gene_obj, 'pleiotropy', [])
                })
            else:
                # Si le gène n'est pas trouvé, utiliser des valeurs par défaut
                gene_data.append({
                    'id': gene_id,
                    'value': gene_value,
                    'weight': weights[i] / total_weight,
                    'expression': 1.0,
                    'epistasis': {},
                    'pleiotropy': []
                })

        # Calculer la valeur de base (pondérée par les poids et l'expression)
        for gene in gene_data:
            # La valeur est modulée par le niveau d'expression du gène
            effective_value = gene['value'] * gene['expression']
            combined_value += effective_value * gene['weight']

        # Appliquer les effets d'épistasie (interactions entre gènes)
        epistatic_modifier = 0
        for gene in gene_data:
            for target_id, effect in gene['epistasis'].items():
                # Chercher si le gène cible est dans notre ensemble
                for target_gene in gene_data:
                    if target_gene['id'] == target_id:
                        # L'effet peut être positif (synergique) ou négatif (inhibiteur)
                        interaction = gene['value'] * target_gene['value'] * effect
                        epistatic_modifier += interaction
                        break

        # Limiter l'effet d'épistasie pour éviter des valeurs extrêmes
        epistatic_modifier = max(-0.3, min(0.3, epistatic_modifier))

        # Appliquer les effets de pléiotropie pour ce trait spécifique
        pleiotropic_modifier = 0
        for gene in gene_data:
            for trait, effect in gene['pleiotropy']:
                # Vérifier si l'un des gènes a un effet pléiotropique sur ce trait
                if any(gene_id.startswith(trait) for gene_id in gene_ids):
                    pleiotropic_modifier += gene['value'] * effect

        # Limiter l'effet de pléiotropie
        pleiotropic_modifier = max(-0.2, min(0.2, pleiotropic_modifier))

        # Combiner tous les effets
        final_value = combined_value + epistatic_modifier + pleiotropic_modifier

        # Normaliser entre 0 et 1
        final_value = max(0, min(1, final_value))

        # Convertir à l'échelle demandée
        return min_value + final_value * (max_value - min_value)
    
    def _calculate_size(self) -> float:
        """Calcule la taille de l'organisme en fonction des gènes."""
        base_size = self._calculate_trait_from_combination(
            ["energy_storage", "strength"], 
            [0.6, 0.4], 
            0.1, 3.0
        )
        
        # La taille influence l'énergie nécessaire et la vitesse
        return base_size
    
    def _calculate_color(self) -> Tuple[int, int, int]:
        """Calcule la couleur de l'organisme en fonction des gènes."""
        # Utilise des valeurs par défaut si les gènes n'existent pas
        r = max(0, min(255, int(255 * self.genome.get_gene_value("gene_0_0"))))
        g = max(0, min(255, int(255 * self.genome.get_gene_value("gene_0_1"))))
        b = max(0, min(255, int(255 * self.genome.get_gene_value("gene_0_2"))))
        return (r, g, b)
    
    def _calculate_lifespan(self) -> int:
        """Calcule la durée de vie en fonction des gènes."""
        base_lifespan = self._calculate_trait_from_combination(
            ["metabolism_efficiency", "immune_system", "waste_processing"],
            [0.4, 0.4, 0.2],
            50, 1000
        )
        
        # La taille et le métabolisme affectent la durée de vie
        size_factor = 1.0 - (self.size - 0.1) / 2.9 * 0.3  # Pénalité de taille (max 30%)
        metabolism_factor = 1.0 - (self.metabolism_rate - 0.3) / 1.7 * 0.2  # Pénalité de métabolisme (max 20%)
        
        return base_lifespan * size_factor * metabolism_factor

class Organism:
    """
    Représente un organisme vivant dans l'écosystème.

    Implémente les mécanismes fondamentaux de l'évolution biologique :
    - Variation génétique (mutations, recombinaison)
    - Adaptation à l'environnement
    - Reproduction (sexuée et asexuée)
    - Développement et croissance
    - Interactions écologiques
    """
    def __init__(self,
                 position: Tuple[float, float],
                 genome: Optional[Genome] = None,
                 organism_type: OrganismType = OrganismType.UNICELLULAR,
                 generation: int = 1,
                 parent_ids: List[str] = None,
                 species_id: str = None,
                 taxonomy_id: str = None,
                 parent_taxonomy_id: str = None,
                 is_hybrid: bool = False,
                 developmental_stage: str = "adult"):

        self.id = str(uuid.uuid4())
        self.position = position
        self.velocity = (0, 0)
        self.age = 0
        self.organism_type = organism_type
        self.developmental_stage = developmental_stage  # zygote, embryo, juvenile, adult, senescent

        # Informations évolutives
        self.generation = generation  # Génération de l'organisme
        self.parent_ids = parent_ids or []  # IDs des parents
        self.species_id = species_id or self.id  # ID de l'espèce (par défaut, chaque organisme initial est sa propre espèce)
        self.mutation_count = 0  # Nombre de mutations significatives
        self.adaptation_score = 0.0  # Score d'adaptation à l'environnement
        self.is_hybrid = is_hybrid  # Issu d'hybridation entre espèces différentes
        self.evolutionary_pressures = {}  # Pressions évolutives actuelles {pressure_name: intensity}
        self.evolutionary_history = []  # Historique des événements évolutifs significatifs
        self.species_population = 1  # Nombre d'individus de la même espèce (mis à jour par le monde)
        self.geographic_isolation = 0.0  # Degré d'isolement géographique (0.0 à 1.0)

        # Taxonomie
        self.parent_taxonomy_id = parent_taxonomy_id

        # Systèmes évolutifs avancés (activés si les modules sont disponibles)
        self.gene_regulatory_network = None
        self.coevolutionary_relationships = []

        if ADVANCED_EVOLUTION_ENABLED:
            # Initialiser le réseau de régulation génétique si le module est disponible
            try:
                self.gene_regulatory_network = create_gene_regulatory_network()
            except Exception as e:
                print(f"Erreur lors de l'initialisation du réseau de régulation génétique: {e}")
                self.gene_regulatory_network = None

        # Génome et phénotype
        self.genome = genome if genome else Genome.random_genome()
        self.phenotype = Phenotype(self.genome)

        # Génération de la taxonomie
        if taxonomy_id:
            self.taxonomy_id = taxonomy_id
        else:
            # Générer une nouvelle taxonomie
            mutation_traits = {'count': self.mutation_count, 'significance': 0.5}
            self.taxonomy_id = Taxonomy.generate_taxonomy(
                self.organism_type,
                parent_taxonomy_id=parent_taxonomy_id,
                mutation_traits=mutation_traits,
                species_id=self.species_id
            )

        # Noms scientifiques et communs
        self.scientific_name = Taxonomy.get_scientific_name(self.taxonomy_id)
        self.common_name = Taxonomy.get_common_name(self.taxonomy_id, self.organism_type)

        # État physiologique
        self.energy = self.phenotype.energy_capacity * 0.5
        self.health = 100.0
        self.hydration = 100.0
        self.waste = 0.0
        self.is_alive = True
        self.maturity = 0.0  # 0 à 1, où 1 est mature

        # Mémoire et apprentissage
        self.memory = {}
        self.learning_progress = {}

        # Reproduction
        self.reproduction_cooldown = 0
        self.offspring_count = 0
        self.successful_offspring = 0  # Descendants qui ont atteint la maturité

        # Relations sociales (pour espèces sociales)
        self.social_bonds = {}

        # Statut de reproduction
        self.ready_to_mate = False

        # Statut de ressources
        self.collected_resources = {res_type: 0 for res_type in ResourceType}

        # Calcul du score d'adaptation initial
        self._calculate_adaptation_score()
    
    def update(self, world, delta_time: float):
        """Met à jour l'état de l'organisme."""
        if not self.is_alive:
            return
        
        # Vieillissement
        self.age += delta_time
        
        # Maturation
        if self.maturity < 1.0:
            maturation_increment = delta_time / self.phenotype.maturation_time
            self.maturity = min(1.0, self.maturity + maturation_increment)
        
        # Métabolisme (consommation d'énergie)
        energy_consumption = self.phenotype.metabolism_rate * delta_time
        self.energy = max(0, self.energy - energy_consumption)
        
        # Production de déchets métaboliques
        waste_production = energy_consumption * (1 - self.phenotype.waste_tolerance)
        self.waste = min(100, self.waste + waste_production)
        
        # Impact des déchets sur la santé
        if self.waste > 50:
            health_impact = (self.waste - 50) / 50 * delta_time * 2
            self.health = max(0, self.health - health_impact)
        
        # Déshydratation
        hydration_loss = 2 * delta_time
        self.hydration = max(0, self.hydration - hydration_loss)
        if self.hydration < 20:
            health_impact = (20 - self.hydration) / 20 * delta_time * 5
            self.health = max(0, self.health - health_impact)
        
        # Perte de santé due à la faim
        if self.energy < self.phenotype.energy_capacity * 0.1:
            hunger_damage = delta_time * 5
            self.health = max(0, self.health - hunger_damage)
        
        # Récupération naturelle de la santé si les conditions sont bonnes
        if (self.energy > self.phenotype.energy_capacity * 0.5 and 
            self.hydration > 50 and 
            self.waste < 30 and 
            self.health < 100):
            health_recovery = delta_time * self.phenotype.immune_strength
            self.health = min(100, self.health + health_recovery)
        
        # Décrémentation du temps de recharge de reproduction
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown = max(0, self.reproduction_cooldown - delta_time)
        
        # Statut de reproduction
        self.ready_to_mate = (self.maturity == 1.0 and 
                             self.reproduction_cooldown == 0 and 
                             self.energy > self.phenotype.energy_capacity * 0.7 and
                             self.health > 70 and
                             self.offspring_count < self.phenotype.max_offspring)
        
        # Vérifie si l'organisme est encore en vie
        if self.health <= 0 or self.age > self.phenotype.lifespan:
            self.die()
        
        # Mise à jour de la position basée sur la vélocité
        self.position = (
            self.position[0] + self.velocity[0] * delta_time,
            self.position[1] + self.velocity[1] * delta_time
        )
        
        # Maintient la position dans les limites du monde
        self.position = (
            max(0, min(world.width, self.position[0])),
            max(0, min(world.height, self.position[1]))
        )
        
        # Interaction avec l'environnement
        self.interact_with_environment(world, delta_time)
    
    def interact_with_environment(self, world, delta_time: float):
        """Interagit avec l'environnement pour collecter des ressources."""
        current_cell = world.get_cell_at_position(self.position)
        if not current_cell:
            return
        
        # Collection de ressources selon le type d'organisme
        if self.organism_type == OrganismType.UNICELLULAR or self.organism_type == OrganismType.PLANT:
            # Photosynthèse pour les plantes et certains unicellulaires
            if current_cell.resources[ResourceType.SUNLIGHT] > 0 and current_cell.resources[ResourceType.WATER] > 0:
                sunlight_absorbed = min(delta_time * 2, current_cell.resources[ResourceType.SUNLIGHT])
                water_absorbed = min(delta_time, current_cell.resources[ResourceType.WATER])
                
                energy_gained = sunlight_absorbed * 5 * self.phenotype.metabolism_rate
                self.energy = min(self.phenotype.energy_capacity, self.energy + energy_gained)
                self.hydration = min(100, self.hydration + water_absorbed * 10)
                
                # Consommation des ressources de la cellule
                current_cell.resources[ResourceType.SUNLIGHT] -= sunlight_absorbed
                current_cell.resources[ResourceType.WATER] -= water_absorbed
                
                # Production d'oxygène (pour l'écosystème)
                current_cell.resources[ResourceType.OXYGEN] += energy_gained * 0.2
        
        elif self.organism_type == OrganismType.HERBIVORE:
            # Recherche de végétation
            plant_energy = current_cell.resources[ResourceType.ORGANIC_MATTER] * 0.5
            if plant_energy > 0:
                consumed = min(delta_time * 3 * self.phenotype.strength, plant_energy)
                energy_gained = consumed * self.phenotype.metabolism_rate
                self.energy = min(self.phenotype.energy_capacity, self.energy + energy_gained)
                
                # Consommation des ressources
                current_cell.resources[ResourceType.ORGANIC_MATTER] -= consumed / 0.5
                
                # Hydratation par l'eau contenue dans les plantes
                self.hydration = min(100, self.hydration + consumed * 2)
        
        # L'eau est disponible pour tous les organismes
        if current_cell.resources[ResourceType.WATER] > 0 and self.hydration < 100:
            water_consumed = min(delta_time * 2, current_cell.resources[ResourceType.WATER])
            self.hydration = min(100, self.hydration + water_consumed * 20)
            current_cell.resources[ResourceType.WATER] -= water_consumed
    
    def try_reproduce(self, mate: Optional['Organism'] = None) -> Optional['Organism']:
        """Tente de se reproduire avec un autre organisme compatible ou par reproduction asexuée.

        Modèle évolutif amélioré avec des mécanismes de spéciation réalistes basés sur:
        - Isolement géographique (spéciation allopatrique)
        - Isolement reproductif (spéciation sympatrique)
        - Adaptation à différentes niches écologiques (spéciation écologique)
        - Dérive génétique et sélection naturelle
        - Coévolution et interactions écologiques
        - Régulation génétique et gènes architectes

        Différentes stratégies de reproduction sont utilisées selon le type d'organisme:
        - Unicellulaires: Reproduction asexuée (clonage) avec mutations fréquentes et transfert horizontal de gènes
        - Plantes: Reproduction mixte (auto-pollinisation ou croisement) avec mutations modérées
        - Animaux (Herbivores, Carnivores, Omnivores): Reproduction sexuée avec mutations variables
        """
        # Vérification de base pour tous les types d'organismes
        if not self.ready_to_mate:
            return None

        # Coût énergétique de la reproduction (varie selon le type et la complexité)
        reproduction_cost_factors = {
            OrganismType.UNICELLULAR: 0.2,  # Moins coûteux pour les unicellulaires
            OrganismType.PLANT: 0.25,
            OrganismType.HERBIVORE: 0.3,
            OrganismType.CARNIVORE: 0.35,
            OrganismType.OMNIVORE: 0.3
        }

        # Ajustement du coût en fonction de la taille et de la complexité
        size_factor = 1.0 + (self.phenotype.size - 0.5) * 0.5  # Plus grand = plus coûteux
        complexity_factor = 1.0 + (len(self.genome.chromosomes) / 30.0) * 0.5  # Plus complexe = plus coûteux

        base_cost = self.phenotype.energy_capacity * reproduction_cost_factors.get(self.organism_type, 0.3)
        reproduction_cost = base_cost * size_factor * complexity_factor

        if self.energy < reproduction_cost:
            return None

        # Taux de mutation de base selon le type d'organisme et la stratégie évolutive
        # Les organismes à reproduction rapide ont généralement plus de mutations
        mutation_rates = {
            OrganismType.UNICELLULAR: 0.35,  # Mutations très fréquentes - évolution rapide
            OrganismType.PLANT: 0.18,        # Mutations modérées - équilibre entre stabilité et adaptation
            OrganismType.HERBIVORE: 0.12,    # Mutations modérées - pression de sélection moyenne
            OrganismType.CARNIVORE: 0.10,    # Mutations plus rares - sélection plus stricte
            OrganismType.OMNIVORE: 0.15      # Mutations intermédiaires - plus grande plasticité adaptative
        }
        base_mutation_rate = mutation_rates.get(self.organism_type, 0.1)

        # Facteurs environnementaux influençant le taux de mutation
        # Modèle plus réaliste de stress environnemental et d'adaptation
        environmental_stress = 0.0

        # Vérifier si l'organisme est dans un biome défavorable
        if hasattr(self, 'current_biome') and hasattr(self, 'adaptation_score'):
            if self.adaptation_score < 0.5:  # Mauvaise adaptation
                # Stress plus important si l'adaptation est très faible
                environmental_stress += (0.5 - self.adaptation_score) * 0.8
            elif self.adaptation_score > 0.8:  # Très bonne adaptation
                # Réduction du taux de mutation si parfaitement adapté (stabilité)
                environmental_stress -= 0.1

        # Pressions évolutives (sélection directionnelle)
        evolutionary_pressure = 0.0
        for pressure_name, intensity in self.evolutionary_pressures.items():
            if intensity > 0.5:  # Pression significative
                evolutionary_pressure += (intensity - 0.5) * 0.2

        # Isolement géographique (augmente la dérive génétique)
        isolation_factor = 0.0
        if hasattr(self, 'geographic_isolation') and self.geographic_isolation > 0.3:
            isolation_factor = (self.geographic_isolation - 0.3) * 0.3

        # Pression de population (la surpopulation augmente les mutations)
        population_stress = 0.0
        if hasattr(self, 'species_population') and self.species_population > 0:
            # Calculer la densité de population relative
            carrying_capacity = 100  # Capacité de charge par défaut
            if hasattr(self, 'current_cell') and hasattr(self.current_cell, 'carrying_capacity'):
                carrying_capacity = self.current_cell.carrying_capacity

            population_density = self.species_population / carrying_capacity
            if population_density > 0.7:  # Surpopulation
                population_stress = (population_density - 0.7) * 0.5

        # Facteurs de stress environnementaux spécifiques
        if hasattr(self, 'current_cell') and self.current_cell:
            # Température extrême
            temp_optimal = 20  # Température optimale générale
            if hasattr(self.phenotype, 'optimal_temperature'):
                temp_optimal = self.phenotype.optimal_temperature

            temp_stress = abs(self.current_cell.temperature - temp_optimal) / 30
            environmental_stress += temp_stress * 0.3

            # Ressources limitées
            if self.organism_type == OrganismType.PLANT:
                # Stress hydrique et lumineux pour les plantes
                water_level = self.current_cell.resources[ResourceType.WATER] / self.current_cell.resource_capacity[ResourceType.WATER]
                light_level = self.current_cell.resources[ResourceType.SUNLIGHT] / self.current_cell.resource_capacity[ResourceType.SUNLIGHT]

                if water_level < 0.3 or light_level < 0.3:
                    environmental_stress += 0.2
            else:
                # Stress alimentaire pour les animaux
                food_type = ResourceType.ORGANIC_MATTER
                food_level = self.current_cell.resources[food_type] / self.current_cell.resource_capacity[food_type]

                if food_level < 0.3:
                    environmental_stress += 0.2

        # Facteurs de population - la densité de population influence l'évolution
        population_stress = 0.0
        if hasattr(self, 'nearby_organisms_count'):
            # Forte densité = plus de compétition = plus de pression sélective
            if self.nearby_organisms_count > 20:
                population_stress = 0.15
            # Très faible densité = risque de dérive génétique
            elif self.nearby_organisms_count < 3:
                population_stress = 0.1

        # Âge de l'organisme (plus âgé = plus de mutations dans les gamètes)
        # Modèle réaliste d'accumulation de mutations dans les cellules germinales
        age_factor = 0.0
        if hasattr(self, 'age') and hasattr(self.phenotype, 'lifespan'):
            relative_age = self.age / self.phenotype.lifespan

            # Courbe non linéaire - augmentation rapide des mutations avec l'âge
            if relative_age < 0.3:
                age_factor = relative_age * 0.1  # Faible au début
            elif relative_age < 0.7:
                age_factor = 0.03 + (relative_age - 0.3) * 0.2  # Augmentation modérée
            else:
                age_factor = 0.11 + (relative_age - 0.7) * 0.4  # Augmentation rapide en fin de vie

        # Facteur d'exposition aux mutagènes (radiations, toxines, etc.)
        mutagen_exposure = 0.0
        if hasattr(self, 'current_cell') and self.current_cell:
            if hasattr(self.current_cell, 'radiation'):
                mutagen_exposure += self.current_cell.radiation * 2.0
            if hasattr(self.current_cell, 'toxicity'):
                mutagen_exposure += self.current_cell.toxicity * 0.5

        # Ajuster le taux de mutation en fonction de tous les facteurs
        adjusted_mutation_rate = base_mutation_rate * (
            1.0 + environmental_stress + age_factor + population_stress +
            mutagen_exposure + evolutionary_pressure + isolation_factor
        )

        # Limiter le taux de mutation à des valeurs réalistes
        adjusted_mutation_rate = max(0.05, min(0.5, adjusted_mutation_rate))

        # Si les modules avancés sont disponibles, utiliser le réseau de régulation génétique
        if ADVANCED_EVOLUTION_ENABLED and hasattr(self, 'gene_regulatory_network') and self.gene_regulatory_network:
            try:
                # Obtenir les facteurs environnementaux pour le réseau de régulation
                env_factors = {}
                if hasattr(self, 'current_cell') and self.current_cell:
                    if hasattr(self.current_cell, 'temperature'):
                        env_factors['temperature'] = self.current_cell.temperature / 40.0  # Normaliser
                    if hasattr(self.current_cell, 'humidity'):
                        env_factors['humidity'] = self.current_cell.humidity
                    if ResourceType.SUNLIGHT in self.current_cell.resources:
                        env_factors['sunlight'] = self.current_cell.resources[ResourceType.SUNLIGHT]

                # Ajouter les facteurs de stress
                env_factors['stress_level'] = environmental_stress
                env_factors['population_density'] = population_stress

                # Calculer l'expression des gènes en fonction de l'environnement
                gene_expression = self.gene_regulatory_network.get_gene_expression_profile(
                    self.developmental_stage, env_factors
                )

                # Ajuster le taux de mutation en fonction de l'expression des gènes
                if 'mutation_regulation' in gene_expression:
                    mutation_modifier = gene_expression['mutation_regulation']
                    adjusted_mutation_rate *= (0.5 + mutation_modifier)
            except Exception as e:
                print(f"Erreur lors de l'utilisation du réseau de régulation génétique: {e}")
                # En cas d'erreur, continuer avec le taux de mutation déjà calculé

        # Stratégies de reproduction spécifiques par type d'organisme
        # Modèle évolutif amélioré avec des mécanismes de spéciation plus réalistes
        if self.organism_type == OrganismType.UNICELLULAR:
            # Reproduction asexuée (clonage avec mutations)
            # Les unicellulaires peuvent parfois échanger du matériel génétique (transfert horizontal)
            if mate and random.random() < 0.2:  # 20% de chance d'échange génétique
                # Transfert horizontal de gènes - mécanisme important d'évolution microbienne
                # Permet l'acquisition rapide de nouvelles fonctions (ex: résistance aux antibiotiques)
                return self._bacterial_conjugation(mate, reproduction_cost, adjusted_mutation_rate * 1.2)
            else:
                # Division cellulaire avec mutations - mécanisme principal d'évolution des unicellulaires
                # Permet l'accumulation graduelle de mutations et l'adaptation
                return self._asexual_reproduction(reproduction_cost, adjusted_mutation_rate)

        elif self.organism_type == OrganismType.PLANT:
            # Les plantes ont des stratégies de reproduction variées et complexes
            # Modèle plus réaliste de reproduction végétale

            # Facteurs saisonniers et environnementaux
            season_factor = 0.5  # Valeur par défaut
            if hasattr(self, 'world') and hasattr(self.world, 'season'):
                # Saisons réelles du monde
                season = self.world.season
                # Printemps et début d'été sont optimaux pour la reproduction
                if season == 0:  # Printemps
                    season_factor = 0.9
                elif season == 1:  # Été
                    season_factor = 0.7
                elif season == 2:  # Automne
                    season_factor = 0.4
                else:  # Hiver
                    season_factor = 0.2
            else:
                # Simulation simplifiée des saisons basée sur l'âge
                season_factor = math.sin(self.age / 100.0 * math.pi) * 0.5 + 0.5

            # Pollinisation croisée (reproduction sexuée)
            if mate and mate.ready_to_mate and mate.organism_type == self.organism_type:
                # Distance entre les plantes
                distance = math.sqrt((self.position[0] - mate.position[0])**2 +
                                    (self.position[1] - mate.position[1])**2)

                # Facteurs influençant la pollinisation
                # 1. Distance (plus proche = plus probable)
                distance_factor = 1.0 - min(1.0, distance / 25.0)

                # 2. Saison (printemps/été = plus probable)

                # 3. Compatibilité génétique
                genetic_compatibility = 0.7  # Valeur par défaut
                if hasattr(self, '_calculate_genetic_similarity'):
                    genetic_compatibility = self._calculate_genetic_similarity(mate)

                # Probabilité finale de pollinisation croisée
                pollination_chance = (
                    0.3 +                      # Chance de base
                    distance_factor * 0.3 +    # Influence de la distance
                    season_factor * 0.3        # Influence de la saison
                )

                # Limiter entre 0 et 1
                pollination_chance = max(0.0, min(1.0, pollination_chance))

                if random.random() < pollination_chance:
                    return self._sexual_reproduction(mate, reproduction_cost, adjusted_mutation_rate)

            # Auto-pollinisation (reproduction asexuée)
            # Plus probable en fin de saison ou en l'absence de partenaires
            autogamy_chance = (
                0.2 +                          # Chance de base
                (1.0 - season_factor) * 0.4    # Plus probable en fin de saison
            )

            # Stratégie de reproduction de secours
            if random.random() < autogamy_chance:
                return self._self_pollination(reproduction_cost, adjusted_mutation_rate * 1.2)

            return None  # Échec de reproduction

        else:  # Animaux (reproduction sexuée obligatoire)
            if not mate or not mate.ready_to_mate or mate.organism_type != self.organism_type:
                return None

            # Modèle amélioré de sélection sexuelle et d'isolement reproductif
            # Facteurs clés dans la spéciation des animaux

            # 1. Compatibilité génétique - isolement reproductif
            genetic_similarity = 0.7  # Valeur par défaut
            if hasattr(self, '_calculate_genetic_similarity'):
                genetic_similarity = self._calculate_genetic_similarity(mate)

            # Seuil d'incompatibilité génétique - varie selon le type d'organisme
            incompatibility_threshold = 0.4
            if self.organism_type == OrganismType.CARNIVORE:
                incompatibility_threshold = 0.45  # Plus strict
            elif self.organism_type == OrganismType.OMNIVORE:
                incompatibility_threshold = 0.35  # Plus flexible

            # Vérifier l'incompatibilité génétique (isolement reproductif)
            if genetic_similarity < incompatibility_threshold:
                # Trop différent génétiquement - isolement reproductif
                if random.random() > genetic_similarity * 1.5:
                    return None

            # 2. Sélection sexuelle - préférence pour certains traits
            # Mécanisme important de spéciation par sélection sexuelle

            # Traits évalués pour la sélection sexuelle
            health_factor = mate.health / 100.0
            size_factor = mate.phenotype.size / 3.0  # Normalisé
            strength_factor = mate.phenotype.strength / 2.0  # Normalisé

            # Préférences différentes selon le type d'organisme
            mate_quality = 0.0

            if self.organism_type == OrganismType.HERBIVORE:
                # Les herbivores valorisent la santé et la vitesse (fuite des prédateurs)
                mate_quality = (
                    health_factor * 0.4 +
                    size_factor * 0.2 +
                    strength_factor * 0.2 +
                    mate.phenotype.max_speed / 10.0 * 0.2
                )
            elif self.organism_type == OrganismType.CARNIVORE:
                # Les carnivores valorisent la force et les capacités de chasse
                mate_quality = (
                    health_factor * 0.3 +
                    size_factor * 0.2 +
                    strength_factor * 0.3 +
                    mate.phenotype.vision_range / 20.0 * 0.2
                )
            elif self.organism_type == OrganismType.OMNIVORE:
                # Les omnivores valorisent l'intelligence et l'adaptabilité
                mate_quality = (
                    health_factor * 0.3 +
                    size_factor * 0.2 +
                    strength_factor * 0.2 +
                    mate.phenotype.metabolism_efficiency * 0.3
                )

            # Probabilité finale de reproduction
            reproduction_probability = (
                0.3 +                          # Chance de base
                mate_quality * 0.4 +           # Qualité du partenaire
                (genetic_similarity - 0.4) * 0.2  # Compatibilité génétique optimale
            )

            # Limiter entre 0.2 et 0.95
            reproduction_probability = max(0.2, min(0.95, reproduction_probability))

            # Tentative de reproduction
            if random.random() < reproduction_probability:
                return self._sexual_reproduction(mate, reproduction_cost, adjusted_mutation_rate)

            return None  # Échec de reproduction

    def _calculate_genetic_similarity(self, mate: 'Organism') -> float:
        """
        Calcule la similarité génétique entre deux organismes.
        Retourne une valeur entre 0 (complètement différent) et 1 (identique).

        Cette méthode est cruciale pour modéliser l'isolement reproductif et la spéciation.
        """
        # Si les organismes sont de types différents, similarité minimale
        if self.organism_type != mate.organism_type:
            return 0.1

        # Si les organismes sont de la même espèce, similarité de base élevée
        if self.species_id == mate.species_id:
            base_similarity = 0.8
        else:
            # Similarité de base plus faible pour des espèces différentes
            base_similarity = 0.5

        # Comparer les génomes chromosome par chromosome
        genome_similarity = 0.0
        chromosome_count = 0

        # Vérifier que les deux organismes ont des chromosomes
        if not self.genome.chromosomes or not mate.genome.chromosomes:
            return base_similarity

        # Comparer les chromosomes qui existent dans les deux génomes
        for i in range(min(len(self.genome.chromosomes), len(mate.genome.chromosomes))):
            self_chromosome = self.genome.chromosomes[i]
            mate_chromosome = mate.genome.chromosomes[i]

            # Compter les gènes communs
            common_genes = 0
            total_genes = 0

            # Ensemble des IDs de gènes dans les deux chromosomes
            self_gene_ids = set(self_chromosome.genes.keys())
            mate_gene_ids = set(mate_chromosome.genes.keys())

            # Gènes présents dans les deux chromosomes
            shared_gene_ids = self_gene_ids.intersection(mate_gene_ids)

            # Similarité des gènes communs
            gene_value_similarity = 0.0

            for gene_id in shared_gene_ids:
                self_gene = self_chromosome.genes[gene_id]
                mate_gene = mate_chromosome.genes[gene_id]

                # Similarité basée sur la différence de valeur du gène
                value_diff = abs(self_gene.value - mate_gene.value)
                gene_similarity = 1.0 - value_diff

                gene_value_similarity += gene_similarity

            # Calculer la similarité pour ce chromosome
            if shared_gene_ids:
                # Similarité des valeurs des gènes
                avg_gene_similarity = gene_value_similarity / len(shared_gene_ids)

                # Similarité structurelle (présence/absence de gènes)
                structural_similarity = len(shared_gene_ids) / max(len(self_gene_ids), len(mate_gene_ids))

                # Combiner les deux types de similarité
                chromosome_similarity = avg_gene_similarity * 0.6 + structural_similarity * 0.4
            else:
                chromosome_similarity = 0.0

            genome_similarity += chromosome_similarity
            chromosome_count += 1

        # Similarité moyenne des chromosomes
        if chromosome_count > 0:
            avg_genome_similarity = genome_similarity / chromosome_count
        else:
            avg_genome_similarity = 0.0

        # Facteur de génération - les organismes de générations très différentes sont moins compatibles
        generation_diff = abs(self.generation - mate.generation)
        generation_factor = max(0.0, 1.0 - generation_diff / 50.0)  # Effet significatif après 50 générations

        # Combiner tous les facteurs
        final_similarity = (
            base_similarity * 0.3 +
            avg_genome_similarity * 0.6 +
            generation_factor * 0.1
        )

        # Limiter entre 0 et 1
        return max(0.0, min(1.0, final_similarity))

    def update_evolutionary_pressures(self, world=None):
        """
        Met à jour les pressions évolutives agissant sur cet organisme.

        Cette méthode intègre les concepts de la théorie synthétique de l'évolution
        en modélisant les pressions sélectives qui façonnent l'évolution des espèces.

        Args:
            world: Le monde de simulation (optionnel)
        """
        # Réinitialiser les pressions
        self.evolutionary_pressures = {}

        # Si les modules avancés ne sont pas disponibles, utiliser un modèle simplifié
        if not ADVANCED_EVOLUTION_ENABLED:
            # Pressions de base
            if hasattr(self, 'current_cell') and self.current_cell:
                # Pression climatique
                if hasattr(self.current_cell, 'temperature'):
                    optimal_temp = 20
                    if hasattr(self.phenotype, 'optimal_temperature'):
                        optimal_temp = self.phenotype.optimal_temperature

                    temp_stress = abs(self.current_cell.temperature - optimal_temp) / 30.0
                    if temp_stress > 0.3:
                        self.evolutionary_pressures['climate'] = temp_stress

                # Pression de prédation
                if hasattr(self, 'predator_count') and self.predator_count > 0:
                    self.evolutionary_pressures['predation'] = min(1.0, self.predator_count / 5.0)

                # Pression de compétition
                if hasattr(self, 'competition_level'):
                    self.evolutionary_pressures['competition'] = self.competition_level

            return

        # Si les modules avancés sont disponibles, utiliser le système de pressions évolutives
        try:
            if world and hasattr(world, 'evolutionary_pressure_system'):
                pressure_system = world.evolutionary_pressure_system

                # Obtenir la région actuelle
                region_id = None
                if hasattr(self, 'current_cell') and self.current_cell:
                    region_id = self.current_cell.region_id if hasattr(self.current_cell, 'region_id') else None

                # Obtenir l'année et la saison actuelles
                year = world.year if hasattr(world, 'year') else None
                season = world.current_season if hasattr(world, 'current_season') else None

                # Récupérer les pressions actives
                active_pressures = pressure_system.get_active_pressures(region_id, year, season)

                # Calculer l'effet de chaque pression sur cet organisme
                for name, pressure in active_pressures.items():
                    # Vérifier si l'organisme possède les traits ciblés par cette pression
                    has_targeted_traits = False
                    for trait in pressure.target_traits:
                        if hasattr(self.phenotype, trait):
                            has_targeted_traits = True
                            break

                    if has_targeted_traits:
                        # Calculer le coefficient de sélection
                        selection_coefficient = pressure_system.calculate_selection_coefficient(
                            self, region_id, year, season
                        )

                        # Enregistrer la pression si elle est significative
                        if abs(selection_coefficient) > 0.1:
                            self.evolutionary_pressures[name] = selection_coefficient

        except Exception as e:
            print(f"Erreur lors de la mise à jour des pressions évolutives: {e}")

    def _count_significant_mutations(self, offspring_genome: 'Genome') -> Tuple[int, float]:
        """
        Analyse un génome pour déterminer le nombre et l'importance des mutations significatives.

        Retourne un tuple contenant:
        - Le nombre de mutations significatives
        - Un score d'importance des mutations (0-1)

        Cette méthode est cruciale pour modéliser la spéciation basée sur les changements génétiques.
        """
        # Si nous n'avons pas de génome parent pour comparer, retourner des valeurs par défaut
        if not hasattr(self, 'genome') or not self.genome:
            return (0, 0.0)

        # Gènes fondamentaux qui ont un impact majeur sur le phénotype
        fundamental_genes = [
            "metabolism_efficiency", "energy_storage", "waste_processing",
            "speed", "agility", "strength",
            "vision", "hearing", "smell",
            "fertility", "maturation_rate", "offspring_count",
            "immune_system", "toxin_resistance", "offense", "defense",
            "learning_capacity", "memory", "problem_solving",
            "temperature_tolerance", "pressure_tolerance", "radiation_tolerance"
        ]

        # Compteurs pour l'analyse des mutations
        mutation_count = 0
        total_significance = 0.0
        total_genes_compared = 0

        # Comparer les chromosomes
        for i in range(min(len(self.genome.chromosomes), len(offspring_genome.chromosomes))):
            parent_chrom = self.genome.chromosomes[i]
            offspring_chrom = offspring_genome.chromosomes[i]

            # Ensemble des gènes présents dans les deux chromosomes
            parent_genes = set(parent_chrom.genes.keys())
            offspring_genes = set(offspring_chrom.genes.keys())

            # 1. Mutations structurelles - ajout ou suppression de gènes
            new_genes = offspring_genes - parent_genes
            deleted_genes = parent_genes - offspring_genes

            # Chaque ajout ou suppression de gène est une mutation significative
            for gene_id in new_genes:
                mutation_count += 1
                # Les nouveaux gènes fondamentaux sont plus significatifs
                if any(gene_id.startswith(prefix) for prefix in fundamental_genes):
                    total_significance += 0.8
                else:
                    total_significance += 0.4

            for gene_id in deleted_genes:
                mutation_count += 1
                # La perte de gènes fondamentaux est très significative
                if any(gene_id.startswith(prefix) for prefix in fundamental_genes):
                    total_significance += 0.9
                else:
                    total_significance += 0.3

            # 2. Mutations de valeur - changements dans les gènes existants
            common_genes = parent_genes.intersection(offspring_genes)

            for gene_id in common_genes:
                parent_gene = parent_chrom.genes[gene_id]
                offspring_gene = offspring_chrom.genes[gene_id]

                # Calculer la différence de valeur
                value_diff = abs(parent_gene.value - offspring_gene.value)

                # Seuil de mutation significative - plus strict pour les gènes fondamentaux
                significance_threshold = 0.1 if any(gene_id.startswith(prefix) for prefix in fundamental_genes) else 0.2

                if value_diff > significance_threshold:
                    mutation_count += 1

                    # L'importance de la mutation dépend de l'ampleur du changement et du type de gène
                    if any(gene_id.startswith(prefix) for prefix in fundamental_genes):
                        # Les mutations dans les gènes fondamentaux sont plus significatives
                        significance = value_diff * 1.5
                    else:
                        significance = value_diff

                    total_significance += min(1.0, significance)

                total_genes_compared += 1

        # 3. Mutations chromosomiques - différence dans le nombre de chromosomes
        if len(self.genome.chromosomes) != len(offspring_genome.chromosomes):
            chrom_diff = abs(len(self.genome.chromosomes) - len(offspring_genome.chromosomes))
            mutation_count += chrom_diff
            total_significance += chrom_diff * 0.7  # Très significatif

        # Calculer le score d'importance moyen des mutations
        if mutation_count > 0:
            avg_significance = total_significance / mutation_count
        else:
            avg_significance = 0.0

        # Normaliser le score d'importance entre 0 et 1
        normalized_significance = min(1.0, avg_significance)

        return (mutation_count, normalized_significance)

    def _bacterial_conjugation(self, mate: 'Organism', reproduction_cost: float, mutation_rate: float) -> 'Organism':
        """Simule la conjugaison bactérienne - transfert horizontal de gènes entre unicellulaires."""
        # Copie du génome avec mutations
        offspring_genome = self.genome.mutate()

        # Sélectionner aléatoirement des gènes du partenaire à transférer
        if mate.genome.chromosomes and offspring_genome.chromosomes:
            # Nombre de gènes à transférer
            transfer_count = random.randint(1, 5)

            # Sélectionner un chromosome aléatoire du donneur et du receveur
            donor_chromosome = random.choice(mate.genome.chromosomes)
            recipient_chromosome = random.choice(offspring_genome.chromosomes)

            # Transférer des gènes aléatoires
            if donor_chromosome.genes:
                donor_genes = list(donor_chromosome.genes.items())
                for _ in range(min(transfer_count, len(donor_genes))):
                    if donor_genes:
                        gene_id, gene = random.choice(donor_genes)
                        donor_genes.remove((gene_id, gene))

                        # Copier le gène avec possibilité de mutation
                        new_gene = gene.mutate() if random.random() < mutation_rate else Gene(gene_id, gene.value, gene.mutation_rate)
                        recipient_chromosome.add_gene(new_gene)

        # Position légèrement décalée
        offspring_position = (
            self.position[0] + random.uniform(-3, 3),
            self.position[1] + random.uniform(-3, 3)
        )

        # Nouvelle génération
        new_generation = self.generation + 1

        # Détermination de l'espèce (chance de spéciation plus élevée due au transfert horizontal)
        species_id = self.species_id
        if random.random() < mutation_rate * 2.5:  # Chance accrue de nouvelle espèce
            species_id = str(uuid.uuid4())

        # Création du nouvel organisme
        offspring = Organism(
            position=offspring_position,
            genome=offspring_genome,
            organism_type=self.organism_type,
            generation=new_generation,
            parent_ids=[self.id, mate.id],  # Les deux parents contribuent
            species_id=species_id
        )

        # Comptage des mutations significatives
        mutation_count = self._count_significant_mutations(offspring_genome)
        offspring.mutation_count = mutation_count

        # Coûts pour les parents
        self.energy -= reproduction_cost * 0.7  # Coût réduit car partagé
        mate.energy -= reproduction_cost * 0.3  # Le donneur dépense moins d'énergie

        self.reproduction_cooldown = 25  # Temps de récupération réduit
        mate.reproduction_cooldown = 15  # Temps de récupération très court pour le donneur

        self.offspring_count += 1
        # Le donneur ne compte pas cela comme sa progéniture

        return offspring

    def _asexual_reproduction(self, reproduction_cost: float, mutation_rate: float) -> 'Organism':
        """
        Reproduction asexuée (clonage avec mutations) avec un modèle évolutif réaliste.

        Modélise les différents types de mutations et leurs effets sur la spéciation:
        - Mutations ponctuelles: changements de nucléotides individuels
        - Duplications de gènes: source importante d'innovation évolutive
        - Délétions: perte de matériel génétique
        - Insertions: ajout de nouveau matériel génétique
        - Réarrangements chromosomiques: changements structurels majeurs
        """
        # Copie du génome avec mutations de base
        offspring_genome = self.genome.mutate()

        # Facteurs environnementaux qui influencent les mutations
        environmental_mutagen_factor = 1.0
        if hasattr(self, 'current_cell') and self.current_cell:
            # Exposition aux radiations
            if hasattr(self.current_cell, 'radiation'):
                environmental_mutagen_factor += self.current_cell.radiation * 3.0

            # Exposition aux toxines
            if hasattr(self.current_cell, 'toxicity'):
                environmental_mutagen_factor += self.current_cell.toxicity * 1.5

            # Stress thermique
            if hasattr(self.current_cell, 'temperature'):
                temp_optimal = 20
                if hasattr(self.phenotype, 'optimal_temperature'):
                    temp_optimal = self.phenotype.optimal_temperature

                temp_stress = abs(self.current_cell.temperature - temp_optimal) / 30
                if temp_stress > 0.5:  # Stress thermique significatif
                    environmental_mutagen_factor += temp_stress * 0.5

        # Modèle avancé de mutations pour la division cellulaire
        # Les mutations se produisent principalement pendant la réplication de l'ADN
        for chromosome in offspring_genome.chromosomes:
            # Probabilité de mutation par chromosome proportionnelle à sa taille et aux facteurs environnementaux
            chromosome_mutation_chance = min(0.9, mutation_rate * len(chromosome.genes) / 10 * environmental_mutagen_factor)

            # Plusieurs mutations peuvent se produire sur un même chromosome
            mutation_count_for_chromosome = 0
            if random.random() < chromosome_mutation_chance:
                # Nombre de mutations basé sur la taille du chromosome et le taux de mutation
                potential_mutations = max(1, int(len(chromosome.genes) * mutation_rate * 2))
                mutation_count_for_chromosome = min(
                    random.randint(1, potential_mutations),
                    5  # Limite pour éviter trop de mutations simultanées
                )

            # Appliquer les mutations
            for _ in range(mutation_count_for_chromosome):
                # Sélectionner un type de mutation avec des probabilités réalistes
                # Les mutations ponctuelles sont les plus courantes, suivies des insertions/délétions
                mutation_type = random.choices(
                    ["point", "duplication", "deletion", "insertion", "rearrangement"],
                    weights=[0.65, 0.12, 0.10, 0.08, 0.05]  # Probabilités basées sur des données biologiques
                )[0]

                # Appliquer la mutation selon son type
                if mutation_type == "point" and chromosome.genes:
                    # Mutation ponctuelle - modifier un gène existant
                    gene_id = random.choice(list(chromosome.genes.keys()))
                    gene = chromosome.genes[gene_id]

                    # Différents types de mutations ponctuelles
                    point_mutation_type = random.choices(
                        ["silent", "missense", "nonsense"],
                        weights=[0.6, 0.35, 0.05]  # La plupart des mutations sont silencieuses ou faux-sens
                    )[0]

                    if point_mutation_type == "silent":
                        # Mutation silencieuse - petit changement sans effet majeur
                        mutation_size = random.gauss(0, 0.02)
                    elif point_mutation_type == "missense":
                        # Mutation faux-sens - changement modéré avec effet potentiel
                        mutation_size = random.gauss(0, 0.1)
                    else:  # nonsense
                        # Mutation non-sens - changement important avec effet probable
                        mutation_size = random.gauss(0, 0.25)

                    # Appliquer la mutation
                    gene.value = max(0, min(1, gene.value + mutation_size))

                    # Ajuster le taux de mutation du gène lui-même (certains gènes sont plus mutables)
                    if random.random() < 0.1:  # 10% de chance
                        gene.mutation_rate = max(0.01, min(0.5, gene.mutation_rate + random.gauss(0, 0.05)))

                elif mutation_type == "duplication" and chromosome.genes:
                    # Duplication de gène - mécanisme important d'innovation évolutive
                    # Permet l'apparition de nouvelles fonctions tout en conservant l'ancienne

                    # Sélectionner un gène à dupliquer
                    gene_id = random.choice(list(chromosome.genes.keys()))
                    gene = chromosome.genes[gene_id]

                    # Créer une copie avec un nouvel ID
                    new_gene_id = f"{gene_id}_dup_{random.randint(0, 1000)}"

                    # La copie peut subir des modifications
                    new_value = gene.value
                    if random.random() < 0.3:  # 30% de chance de modification immédiate
                        new_value = max(0, min(1, new_value + random.gauss(0, 0.1)))

                    # Taux de mutation potentiellement plus élevé pour le gène dupliqué
                    new_mutation_rate = gene.mutation_rate
                    if random.random() < 0.4:  # 40% de chance
                        new_mutation_rate = min(0.5, new_mutation_rate * random.uniform(1.0, 2.0))

                    # Créer et ajouter le nouveau gène
                    new_gene = Gene(new_gene_id, new_value, new_mutation_rate)
                    chromosome.add_gene(new_gene)

                elif mutation_type == "deletion" and len(chromosome.genes) > 1:
                    # Suppression de gène - peut être bénéfique en éliminant des fonctions inutiles
                    # ou nuisible en supprimant des fonctions essentielles

                    # Éviter de supprimer des gènes essentiels
                    essential_gene_prefixes = ["metabolism", "energy", "reproduction", "survival"]
                    non_essential_genes = [g for g in chromosome.genes.keys()
                                          if not any(g.startswith(prefix) for prefix in essential_gene_prefixes)]

                    if non_essential_genes:
                        gene_to_delete = random.choice(non_essential_genes)
                        del chromosome.genes[gene_to_delete]

                elif mutation_type == "insertion":
                    # Insertion de nouveau gène - peut provenir de transfert horizontal ou de novo

                    # Type d'insertion
                    insertion_source = random.choices(
                        ["de_novo", "modified_copy"],
                        weights=[0.3, 0.7]  # Plus souvent dérivé d'un gène existant
                    )[0]

                    if insertion_source == "de_novo" or not chromosome.genes:
                        # Gène entièrement nouveau
                        new_gene_id = f"gene_new_{random.randint(0, 1000)}"
                        new_gene = Gene(
                            new_gene_id,
                            random.random(),  # Valeur aléatoire
                            random.uniform(0.05, 0.2)  # Taux de mutation variable
                        )
                    else:
                        # Gène dérivé d'un existant mais fortement modifié
                        template_gene_id = random.choice(list(chromosome.genes.keys()))
                        template_gene = chromosome.genes[template_gene_id]

                        new_gene_id = f"{template_gene_id}_var_{random.randint(0, 1000)}"
                        new_value = max(0, min(1, template_gene.value + random.gauss(0, 0.3)))
                        new_gene = Gene(new_gene_id, new_value, template_gene.mutation_rate * random.uniform(0.8, 1.5))

                    chromosome.add_gene(new_gene)

                elif mutation_type == "rearrangement" and len(offspring_genome.chromosomes) > 1:
                    # Réarrangement chromosomique - changement structurel majeur
                    # Peut conduire à un isolement reproductif et à la spéciation

                    # Sélectionner un autre chromosome pour l'échange
                    other_chromosomes = [c for c in offspring_genome.chromosomes if c != chromosome]
                    if other_chromosomes:
                        other_chromosome = random.choice(other_chromosomes)

                        # Échanger une partie des gènes entre les chromosomes
                        if chromosome.genes and other_chromosome.genes:
                            # Nombre de gènes à échanger
                            exchange_count = min(
                                random.randint(1, 3),
                                min(len(chromosome.genes), len(other_chromosome.genes))
                            )

                            # Sélectionner et échanger des gènes aléatoires
                            for _ in range(exchange_count):
                                if chromosome.genes and other_chromosome.genes:
                                    gene1_id = random.choice(list(chromosome.genes.keys()))
                                    gene2_id = random.choice(list(other_chromosome.genes.keys()))

                                    # Échanger les gènes
                                    chromosome.genes[gene1_id], other_chromosome.genes[gene2_id] = \
                                        other_chromosome.genes[gene2_id], chromosome.genes[gene1_id]

        # Position de l'organisme enfant selon le type d'organisme
        if self.organism_type == OrganismType.UNICELLULAR:
            # Division cellulaire - position proche
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(1, 4)  # Distance de séparation typique pour les bactéries

            offspring_position = (
                self.position[0] + math.cos(angle) * distance,
                self.position[1] + math.sin(angle) * distance
            )
        else:
            # Autres types d'organismes - position variable
            offspring_position = (
                self.position[0] + random.uniform(-5, 5),
                self.position[1] + random.uniform(-5, 5)
            )

        # Nouvelle génération
        new_generation = self.generation + 1

        # Analyse des mutations pour déterminer la spéciation
        mutation_result = self._count_significant_mutations(offspring_genome)
        mutation_count = mutation_result[0]
        mutation_significance = mutation_result[1]

        # Modèle de spéciation plus réaliste basé sur plusieurs facteurs

        # 1. Accumulation de mutations significatives
        mutation_factor = min(1.0, (mutation_count / 5) * (mutation_significance / 0.5))

        # 2. Isolement géographique (si applicable)
        geographic_isolation = 0.0
        if hasattr(self, 'species_population') and self.species_population < 5:
            geographic_isolation = 0.2  # Petite population isolée

        # 3. Pression de sélection environnementale
        environmental_pressure = 0.0
        if hasattr(self, 'adaptation_score'):
            if self.adaptation_score < 0.4:  # Mauvaise adaptation
                environmental_pressure = 0.3
            elif self.adaptation_score < 0.6:  # Adaptation moyenne
                environmental_pressure = 0.15

        # 4. Facteur temporel - accumulation de différences au fil des générations
        generation_factor = min(0.3, self.generation / 100)

        # Probabilité finale de spéciation
        speciation_probability = (
            0.05 +                      # Probabilité de base
            mutation_factor * 0.4 +     # Influence des mutations
            geographic_isolation +      # Isolement géographique
            environmental_pressure +    # Pression environnementale
            generation_factor           # Facteur générationnel
        )

        # Limiter la probabilité
        speciation_probability = min(0.8, max(0.0, speciation_probability))

        # Déterminer si une nouvelle espèce est créée
        species_id = self.species_id
        new_species = random.random() < speciation_probability

        if new_species:
            species_id = str(uuid.uuid4())

            # Enregistrer l'événement de spéciation si possible
            if hasattr(self, 'world') and hasattr(self.world, 'evolutionary_milestones'):
                self.world.evolutionary_milestones.append({
                    'year': getattr(self.world, 'year', 0),
                    'day': getattr(self.world, 'day', 0),
                    'event_type': 'speciation',
                    'parent_species': self.species_id,
                    'new_species': species_id,
                    'organism_type': self.organism_type.name,
                    'mutation_count': mutation_count,
                    'mutation_significance': mutation_significance,
                    'mechanism': 'asexual_reproduction',
                    'description': f"Nouvelle espèce formée par reproduction asexuée avec {mutation_count} mutations significatives"
                })

        # Création du nouvel organisme avec taxonomie
        # Déterminer la taxonomie en fonction des mutations et de la spéciation
        mutation_traits = {
            'count': mutation_count,
            'significance': mutation_significance if new_species else mutation_significance * 0.5,
            'new_species': new_species,
            'mechanism': 'asexual_reproduction'
        }

        offspring = Organism(
            position=offspring_position,
            genome=offspring_genome,
            organism_type=self.organism_type,
            generation=new_generation,
            parent_ids=[self.id],
            species_id=species_id,
            parent_taxonomy_id=self.taxonomy_id,
            taxonomy_id=None  # Sera généré automatiquement dans le constructeur
        )

        offspring.maturity = 0.0
        offspring.mutation_count = mutation_count

        # Coûts pour le parent - division cellulaire
        self.energy -= reproduction_cost

        # Temps de récupération variable selon les conditions environnementales
        base_cooldown = 30

        # Ajustement selon les ressources disponibles
        if hasattr(self, 'current_cell') and self.current_cell:
            resources = self.current_cell.resources
            if resources[ResourceType.ORGANIC_MATTER] > 0.7:
                base_cooldown *= 0.8  # Récupération plus rapide si beaucoup de ressources
            elif resources[ResourceType.ORGANIC_MATTER] < 0.3:
                base_cooldown *= 1.2  # Récupération plus lente si peu de ressources

        self.reproduction_cooldown = base_cooldown
        self.offspring_count += 1

        return offspring

    def _self_pollination(self, reproduction_cost: float, mutation_rate: float) -> 'Organism':
        """Auto-pollinisation pour les plantes avec un modèle plus réaliste."""
        # Copie du génome avec plus de mutations (compensation pour le manque de diversité)
        offspring_genome = self.genome.mutate()

        # Simulation de l'autofécondation - croisement entre différentes parties du même génome
        # Dans la nature, même l'autopollinisation implique une recombinaison génétique
        if len(offspring_genome.chromosomes) >= 2:
            # Sélectionner deux chromosomes différents pour simuler la recombinaison
            indices = random.sample(range(len(offspring_genome.chromosomes)), 2)
            chrom1, chrom2 = offspring_genome.chromosomes[indices[0]], offspring_genome.chromosomes[indices[1]]

            # Échanger quelques gènes entre ces chromosomes
            if chrom1.genes and chrom2.genes:
                genes_to_swap = min(random.randint(1, 3), min(len(chrom1.genes), len(chrom2.genes)))

                for _ in range(genes_to_swap):
                    # Sélectionner des gènes aléatoires à échanger
                    if chrom1.genes and chrom2.genes:
                        gene1_id = random.choice(list(chrom1.genes.keys()))
                        gene2_id = random.choice(list(chrom2.genes.keys()))

                        # Échanger les gènes
                        chrom1.genes[gene1_id], chrom2.genes[gene2_id] = chrom2.genes[gene2_id], chrom1.genes[gene1_id]

        # Mutations supplémentaires - plus fréquentes dans l'autopollinisation
        # Cela simule l'accumulation de mutations récessives délétères
        inbreeding_depression = 0.0  # Risque de dépression de consanguinité

        for chromosome in offspring_genome.chromosomes:
            for gene_id, gene in list(chromosome.genes.items()):
                if random.random() < mutation_rate:
                    # Mutation plus forte
                    mutation = random.gauss(0, 0.2)  # Plus grande variance
                    new_value = max(0, min(1, gene.value + mutation))
                    gene.value = new_value

                    # Chance de mutation délétère
                    if random.random() < 0.2:  # 20% de chance
                        inbreeding_depression += 0.05

        # Dispersion des graines - modèle plus réaliste
        # Les plantes dispersent leurs graines selon différentes stratégies
        dispersion_strategies = [
            "gravity",      # Chute simple près du parent
            "wind",         # Dispersion par le vent
            "explosion"     # Dispersion explosive (comme certaines légumineuses)
        ]

        strategy = random.choices(
            dispersion_strategies,
            weights=[0.6, 0.3, 0.1]  # Probabilités relatives
        )[0]

        # Position basée sur la stratégie de dispersion
        if strategy == "gravity":
            # Chute près du parent
            offspring_position = (
                self.position[0] + random.uniform(-3, 3),
                self.position[1] + random.uniform(-3, 3)
            )
        elif strategy == "wind":
            # Dispersion par le vent - plus loin et directionnelle
            wind_direction = random.uniform(0, 2 * math.pi)
            wind_strength = random.uniform(5, 15)

            offspring_position = (
                self.position[0] + math.cos(wind_direction) * wind_strength,
                self.position[1] + math.sin(wind_direction) * wind_strength
            )
        else:  # explosion
            # Dispersion explosive - distance moyenne mais dans toutes les directions
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(8, 12)

            offspring_position = (
                self.position[0] + math.cos(angle) * distance,
                self.position[1] + math.sin(angle) * distance
            )

        # Nouvelle génération
        new_generation = self.generation + 1

        # Détermination de l'espèce avec un modèle plus réaliste
        species_id = self.species_id
        mutation_result = self._count_significant_mutations(offspring_genome)
        mutation_count = mutation_result[0]
        mutation_significance = mutation_result[1]

        # Spéciation influencée par l'isolement et les mutations
        speciation_chance = 0.05 + (mutation_count * 0.03) + (mutation_significance * 0.1)

        # L'autopollinisation répétée augmente les chances de spéciation
        if hasattr(self, 'self_pollination_count'):
            self.self_pollination_count += 1
            speciation_chance += min(0.2, self.self_pollination_count * 0.02)
        else:
            self.self_pollination_count = 1

        new_species = False
        if random.random() < speciation_chance:
            species_id = str(uuid.uuid4())
            new_species = True

        # Création du nouvel organisme avec taxonomie
        # Déterminer la taxonomie en fonction des mutations et de la spéciation
        mutation_traits = {
            'count': mutation_count,
            'significance': mutation_significance if new_species else mutation_significance * 0.5
        }

        offspring = Organism(
            position=offspring_position,
            genome=offspring_genome,
            organism_type=self.organism_type,
            generation=new_generation,
            parent_ids=[self.id],
            species_id=species_id,
            parent_taxonomy_id=self.taxonomy_id,
            taxonomy_id=None  # Sera généré automatiquement dans le constructeur
        )

        offspring.maturity = 0.0
        offspring.mutation_count = mutation_count

        # Effet de la dépression de consanguinité
        if inbreeding_depression > 0:
            # Réduction de la santé initiale
            offspring.health = max(50, 100 - inbreeding_depression * 100)

            # Réduction de certains traits phénotypiques
            if hasattr(offspring, 'phenotype'):
                offspring.phenotype.strength *= max(0.7, 1.0 - inbreeding_depression)
                offspring.phenotype.metabolism_rate *= max(0.7, 1.0 - inbreeding_depression)
                offspring.phenotype.fertility *= max(0.6, 1.0 - inbreeding_depression * 1.5)

        # Coûts pour le parent
        self.energy -= reproduction_cost

        # Temps de récupération variable selon la saison (simulée)
        season_factor = math.sin(self.age / 100.0 * math.pi) * 0.5 + 0.5  # 0-1
        base_cooldown = 40
        seasonal_cooldown = base_cooldown * (1.0 - season_factor * 0.3)  # Récupération plus rapide en saison favorable

        self.reproduction_cooldown = seasonal_cooldown
        self.offspring_count += 1

        return offspring

    def _sexual_reproduction(self, mate: 'Organism', reproduction_cost: float, mutation_rate: float) -> Optional['Organism']:
        """Reproduction sexuée pour les plantes (croisement) et les animaux avec un modèle évolutif réaliste."""
        if mate.energy < reproduction_cost:
            return None

        # Calcul de la compatibilité génétique
        genetic_similarity = self._calculate_genetic_similarity(mate)

        # Probabilité de reproduction réussie basée sur la diversité génétique
        # Modèle plus réaliste de sélection sexuelle et d'incompatibilité
        reproduction_chance = 1.0

        # Effet de la consanguinité et de l'incompatibilité
        if genetic_similarity > 0.9:  # Trop similaire (consanguinité)
            reproduction_chance = 0.6
            # Risque accru de problèmes génétiques
            inbreeding_risk = (genetic_similarity - 0.9) * 5  # 0-0.5
        elif genetic_similarity < 0.4:  # Trop différent (incompatibilité)
            reproduction_chance = 0.4
            inbreeding_risk = 0.0
        else:
            # Zone optimale de diversité génétique
            optimal_similarity = 0.7
            distance_from_optimal = abs(genetic_similarity - optimal_similarity)
            reproduction_chance = 1.0 - distance_from_optimal * 0.5
            inbreeding_risk = 0.0

        # Facteurs de fertilité avec influence environnementale
        self_fertility = self.phenotype.fertility
        mate_fertility = mate.phenotype.fertility

        # Ajustement environnemental de la fertilité
        if hasattr(self, 'current_cell') and self.current_cell:
            # Facteurs environnementaux qui affectent la fertilité
            if self.organism_type == OrganismType.PLANT:
                # Les plantes sont sensibles à la lumière et à l'eau
                sunlight = self.current_cell.resources[ResourceType.SUNLIGHT]
                water = self.current_cell.resources[ResourceType.WATER]

                env_factor = (sunlight * 0.6 + water * 0.4) / 1.0  # Normalisé
                self_fertility *= 0.7 + env_factor * 0.6  # 0.7-1.3 range
            else:
                # Les animaux sont sensibles aux ressources et à la température
                resources = self.current_cell.resources[ResourceType.ORGANIC_MATTER]
                temp_optimal = 0.5  # Température optimale normalisée
                temp_actual = (self.current_cell.temperature + 5) / 35  # -5 à 30°C normalisé à 0-1
                temp_stress = abs(temp_actual - temp_optimal)

                env_factor = resources * 0.7 - temp_stress * 0.5
                self_fertility *= 0.8 + max(0, min(0.4, env_factor))  # 0.8-1.2 range

        # Même chose pour le partenaire
        if hasattr(mate, 'current_cell') and mate.current_cell:
            if mate.organism_type == OrganismType.PLANT:
                sunlight = mate.current_cell.resources[ResourceType.SUNLIGHT]
                water = mate.current_cell.resources[ResourceType.WATER]

                env_factor = (sunlight * 0.6 + water * 0.4) / 1.0
                mate_fertility *= 0.7 + env_factor * 0.6
            else:
                resources = mate.current_cell.resources[ResourceType.ORGANIC_MATTER]
                temp_optimal = 0.5
                temp_actual = (mate.current_cell.temperature + 5) / 35
                temp_stress = abs(temp_actual - temp_optimal)

                env_factor = resources * 0.7 - temp_stress * 0.5
                mate_fertility *= 0.8 + max(0, min(0.4, env_factor))

        # Fertilité combinée
        fertility_factor = (self_fertility + mate_fertility) / 2
        reproduction_chance *= fertility_factor

        # Facteurs saisonniers (simulés)
        if hasattr(self, 'age'):
            season_factor = math.sin(self.age / 100.0 * math.pi) * 0.5 + 0.5  # 0-1

            # Certaines espèces se reproduisent mieux à certaines saisons
            if self.organism_type == OrganismType.PLANT:
                # Les plantes préfèrent le printemps/été
                reproduction_chance *= 0.7 + season_factor * 0.6  # 0.7-1.3
            elif self.organism_type == OrganismType.HERBIVORE:
                # Les herbivores suivent les cycles des plantes avec un léger décalage
                delayed_season = math.sin((self.age - 10) / 100.0 * math.pi) * 0.5 + 0.5
                reproduction_chance *= 0.8 + delayed_season * 0.4  # 0.8-1.2

        # Vérification finale de la reproduction
        if random.random() > reproduction_chance:
            # Échec de la reproduction
            self.reproduction_cooldown = 20
            mate.reproduction_cooldown = 20
            return None

        # Combinaison des génomes avec possibilité de mutations
        offspring_genome = Genome.reproduce(self.genome, mate.genome)

        # Mutations supplémentaires basées sur le taux de mutation
        # Les mutations sont influencées par des facteurs environnementaux
        environmental_mutation_factor = 1.0

        # Stress environnemental augmente les mutations
        if hasattr(self, 'current_cell') and self.current_cell:
            # Facteurs de stress: température extrême, pollution, radiation
            temp = self.current_cell.temperature
            temp_stress = abs(temp - 20) / 25  # Écart par rapport à 20°C, normalisé

            # Radiation (si présente)
            radiation = getattr(self.current_cell, 'radiation', 0)

            environmental_mutation_factor += temp_stress * 0.3 + radiation * 2.0

        adjusted_mutation_rate = mutation_rate * environmental_mutation_factor

        # Application des mutations
        if random.random() < adjusted_mutation_rate:
            offspring_genome = offspring_genome.mutate()

            # Mutations supplémentaires dans des conditions extrêmes
            if environmental_mutation_factor > 1.5 and random.random() < 0.3:
                offspring_genome = offspring_genome.mutate()  # Mutation additionnelle

        # Détermination de l'espèce avec un système plus réaliste
        mutation_result = self._count_significant_mutations(offspring_genome)
        mutation_count = mutation_result[0]
        mutation_significance = mutation_result[1]

        # Calcul de la divergence génétique entre l'enfant et chaque parent
        parent1_divergence = self._calculate_genetic_diversity_with_genome(offspring_genome)
        parent2_divergence = mate._calculate_genetic_diversity_with_genome(offspring_genome)

        # Divergence moyenne par rapport aux parents
        avg_divergence = (parent1_divergence + parent2_divergence) / 2

        # Facteurs environnementaux qui influencent la spéciation
        environmental_pressure = 0.0

        # Vérifier si les parents vivent dans des biomes différents
        if hasattr(self, 'current_biome') and hasattr(mate, 'current_biome'):
            if self.current_biome != mate.current_biome:
                environmental_pressure += 0.15  # Augmente la chance de spéciation

                # Adaptation à différents biomes
                if hasattr(self, 'adaptation_score') and hasattr(mate, 'adaptation_score'):
                    # Si les deux parents sont bien adaptés à des biomes différents
                    if self.adaptation_score > 0.7 and mate.adaptation_score > 0.7:
                        environmental_pressure += 0.1  # Pression de sélection disruptive

        # Facteur d'isolement géographique - crucial pour la spéciation allopatrique
        distance = math.sqrt((self.position[0] - mate.position[0])**2 +
                            (self.position[1] - mate.position[1])**2)
        geographic_isolation = min(1.0, distance / 500)  # Normaliser entre 0 et 1

        # Populations isolées ont plus de chances de spéciation
        if geographic_isolation > 0.7:
            environmental_pressure += 0.1

        # Facteur de temps (générations) - spéciation graduelle
        generation_factor = min(1.0, max(self.generation, mate.generation) / 50)

        # Facteur de population - les petites populations évoluent plus vite (dérive génétique)
        population_factor = 0.0
        if hasattr(self, 'species_population') and self.species_population < 10:
            population_factor = 0.1

        # Probabilité de spéciation basée sur tous ces facteurs
        speciation_probability = (
            0.05 +                          # Probabilité de base
            avg_divergence * 0.3 +          # Influence de la divergence génétique
            (mutation_count / 10) * 0.2 +   # Influence des mutations significatives
            environmental_pressure +        # Influence de l'environnement
            geographic_isolation * 0.1 +    # Influence de l'isolement géographique
            generation_factor * 0.1 +       # Influence du temps évolutif
            population_factor               # Influence de la taille de population
        )

        # Limiter la probabilité entre 0 et 1
        speciation_probability = min(0.8, max(0.0, speciation_probability))

        # Déterminer si une nouvelle espèce est créée
        new_species = random.random() < speciation_probability

        # Hybridation entre espèces différentes - mécanisme important d'évolution
        if self.species_id != mate.species_id:
            # Compatibilité génétique entre espèces
            genetic_compatibility = self._calculate_genetic_similarity(mate)

            # Si la compatibilité est faible, l'hybridation peut échouer
            if genetic_compatibility < 0.4:
                # Chance d'échec de l'hybridation
                if random.random() > genetic_compatibility * 1.5:
                    # L'hybridation échoue, pas de descendance viable
                    return None

            # Si l'hybridation réussit, plus grande chance de nouvelle espèce
            speciation_probability += 0.2
            new_species = random.random() < speciation_probability

            # Déterminer l'espèce de l'hybride si ce n'est pas une nouvelle espèce
            if not new_species:
                # L'espèce dominante a plus de chance d'être transmise
                parent1_dominance = self._calculate_species_dominance()
                parent2_dominance = mate._calculate_species_dominance()

                if parent1_dominance > parent2_dominance:
                    species_id = self.species_id
                else:
                    species_id = mate.species_id
        else:
            # Même espèce pour les parents
            species_id = self.species_id

        # Si c'est une nouvelle espèce, générer un nouvel ID
        if new_species:
            species_id = str(uuid.uuid4())

        # Position de naissance selon le type d'organisme
        if self.organism_type == OrganismType.PLANT:
            # Les graines tombent près des parents
            parent_choice = random.choice([self, mate])
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(3, 8)

            offspring_position = (
                parent_choice.position[0] + math.cos(angle) * distance,
                parent_choice.position[1] + math.sin(angle) * distance
            )
        else:
            # Les animaux naissent entre les parents ou près de la mère
            if random.random() < 0.7:  # 70% près de la mère (plus réaliste)
                mother = self if random.random() < 0.5 else mate  # Choix aléatoire de la mère
                offspring_position = (
                    mother.position[0] + random.uniform(-3, 3),
                    mother.position[1] + random.uniform(-3, 3)
                )
            else:
                # Entre les parents
                offspring_position = (
                    (self.position[0] + mate.position[0]) / 2 + random.uniform(-5, 5),
                    (self.position[1] + mate.position[1]) / 2 + random.uniform(-5, 5)
                )

        # Nouvelle génération
        new_generation = max(self.generation, mate.generation) + 1

        # Création du nouvel organisme avec taxonomie
        # Déterminer la taxonomie en fonction des mutations et de la spéciation
        mutation_traits = {
            'count': mutation_count,
            'significance': avg_divergence
        }

        # Si c'est une nouvelle espèce, créer une nouvelle taxonomie
        # Sinon, hériter de la taxonomie d'un des parents
        parent_taxonomy_id = self.taxonomy_id if random.random() < 0.5 else mate.taxonomy_id

        offspring = Organism(
            position=offspring_position,
            genome=offspring_genome,
            organism_type=self.organism_type,
            generation=new_generation,
            parent_ids=[self.id, mate.id],
            species_id=species_id,
            parent_taxonomy_id=parent_taxonomy_id,
            taxonomy_id=None  # Sera généré automatiquement dans le constructeur
        )

        offspring.maturity = 0.0
        offspring.mutation_count = mutation_count

        # Effets de la consanguinité si présents
        if inbreeding_risk > 0:
            # Réduction de la santé et de certains traits
            offspring.health = max(60, 100 - inbreeding_risk * 80)

            # Affaiblissement de certains traits
            if hasattr(offspring, 'phenotype'):
                weakness_factor = 1.0 - inbreeding_risk * 0.6
                offspring.phenotype.strength *= weakness_factor
                offspring.phenotype.metabolism_rate *= weakness_factor
                offspring.phenotype.immune_strength *= weakness_factor
                offspring.phenotype.fertility *= max(0.5, weakness_factor - 0.1)  # Fertilité plus affectée

        # Coûts pour les parents - varie selon le type d'organisme
        # Les femelles investissent généralement plus dans la reproduction
        if self.organism_type == OrganismType.PLANT:
            # Coût partagé pour les plantes
            self.energy -= reproduction_cost * 0.6
            mate.energy -= reproduction_cost * 0.4
        else:
            # Pour les animaux, un parent (la "mère") investit plus
            mother = self if random.random() < 0.5 else mate
            father = mate if mother == self else self

            mother.energy -= reproduction_cost * 0.7
            father.energy -= reproduction_cost * 0.3

        # Temps de récupération variable selon le type et les conditions
        base_cooldown_factors = {
            OrganismType.PLANT: 40,
            OrganismType.HERBIVORE: 50,
            OrganismType.CARNIVORE: 60,
            OrganismType.OMNIVORE: 55
        }
        base_cooldown = base_cooldown_factors.get(self.organism_type, 50)

        # Ajustements environnementaux et individuels
        # Ressources abondantes = récupération plus rapide
        resource_factor = 1.0
        if hasattr(self, 'current_cell') and self.current_cell:
            if self.organism_type == OrganismType.PLANT:
                resources = (self.current_cell.resources[ResourceType.SUNLIGHT] +
                            self.current_cell.resources[ResourceType.WATER]) / 2
            else:
                resources = self.current_cell.resources[ResourceType.ORGANIC_MATTER]

            resource_factor = 1.2 - resources * 0.4  # 0.8-1.2 range

        # Âge influence la récupération
        age_factor = 1.0
        if hasattr(self, 'age') and hasattr(self, 'phenotype') and hasattr(self.phenotype, 'lifespan'):
            relative_age = self.age / self.phenotype.lifespan
            if relative_age > 0.7:  # Organismes âgés récupèrent plus lentement
                age_factor = 1.0 + (relative_age - 0.7) * 1.0  # Jusqu'à +30%

        # Appliquer les facteurs
        self_cooldown = base_cooldown * resource_factor * age_factor
        mate_cooldown = base_cooldown * resource_factor * age_factor

        # Si l'un des parents est la "mère", son temps de récupération est plus long
        if self.organism_type != OrganismType.PLANT:
            mother = self if random.random() < 0.5 else mate
            if mother == self:
                self_cooldown *= 1.3
            else:
                mate_cooldown *= 1.3

        self.reproduction_cooldown = self_cooldown
        mate.reproduction_cooldown = mate_cooldown

        self.offspring_count += 1
        mate.offspring_count += 1

        # Bonus d'expérience pour les organismes qui se reproduisent (apprentissage)
        if hasattr(self, 'experience') and hasattr(self.phenotype, 'learning_rate'):
            self.experience += 5 * self.phenotype.learning_rate

        if hasattr(mate, 'experience') and hasattr(mate.phenotype, 'learning_rate'):
            mate.experience += 5 * mate.phenotype.learning_rate

        return offspring

    def _calculate_genetic_similarity(self, other: 'Organism') -> float:
        """Calcule la similarité génétique entre deux organismes."""
        if not other or self.organism_type != other.organism_type:
            return 0.0

        # Comparer les gènes des deux organismes
        total_genes = 0
        matching_genes = 0

        # Poids des gènes fondamentaux (plus importants pour la compatibilité)
        fundamental_genes = [
            "metabolism_efficiency", "energy_storage", "waste_processing",
            "speed", "agility", "strength",
            "vision", "hearing", "smell",
            "fertility", "maturation_rate", "offspring_count",
            "immune_system", "toxin_resistance", "offense", "defense",
            "learning_capacity", "memory", "problem_solving",
            "temperature_tolerance", "pressure_tolerance", "radiation_tolerance"
        ]

        # Pour chaque chromosome
        for i in range(min(len(self.genome.chromosomes), len(other.genome.chromosomes))):
            my_chrom = self.genome.chromosomes[i]
            other_chrom = other.genome.chromosomes[i]

            # Pour chaque gène présent dans les deux chromosomes
            all_gene_ids = set(my_chrom.genes.keys()) | set(other_chrom.genes.keys())

            for gene_id in all_gene_ids:
                # Les gènes fondamentaux ont plus de poids
                gene_weight = 2.0 if gene_id in fundamental_genes else 1.0
                total_genes += gene_weight

                if gene_id in my_chrom.genes and gene_id in other_chrom.genes:
                    my_gene = my_chrom.genes[gene_id]
                    other_gene = other_chrom.genes[gene_id]

                    # Similarité basée sur la valeur du gène et la dominance
                    value_diff = abs(my_gene.value - other_gene.value)
                    dominance_diff = abs(my_gene.dominance - other_gene.dominance)

                    # Seuil de similarité plus strict pour les gènes fondamentaux
                    similarity_threshold = 0.15 if gene_id in fundamental_genes else 0.25

                    if value_diff < similarity_threshold and dominance_diff < 0.3:
                        matching_genes += gene_weight

        if total_genes == 0:
            return 0.0

        return matching_genes / total_genes

    def _calculate_genetic_diversity(self, other: 'Organism') -> float:
        """Calcule la diversité génétique entre deux organismes (inverse de la similarité)."""
        similarity = self._calculate_genetic_similarity(other)
        return 1.0 - similarity

    def _calculate_genetic_diversity_with_genome(self, other_genome: Genome) -> float:
        """Calcule la diversité génétique entre cet organisme et un génome donné."""
        # Comparer les gènes des deux génomes
        total_genes = 0
        matching_genes = 0

        # Poids des gènes fondamentaux (plus importants pour la compatibilité)
        fundamental_genes = [
            "metabolism_efficiency", "energy_storage", "waste_processing",
            "speed", "agility", "strength",
            "vision", "hearing", "smell",
            "fertility", "maturation_rate", "offspring_count",
            "immune_system", "toxin_resistance", "offense", "defense",
            "learning_capacity", "memory", "problem_solving",
            "temperature_tolerance", "pressure_tolerance", "radiation_tolerance"
        ]

        # Pour chaque chromosome
        for i in range(min(len(self.genome.chromosomes), len(other_genome.chromosomes))):
            my_chrom = self.genome.chromosomes[i]
            other_chrom = other_genome.chromosomes[i]

            # Pour chaque gène présent dans les deux chromosomes
            all_gene_ids = set(my_chrom.genes.keys()) | set(other_chrom.genes.keys())

            for gene_id in all_gene_ids:
                # Les gènes fondamentaux ont plus de poids
                gene_weight = 2.0 if gene_id in fundamental_genes else 1.0
                total_genes += gene_weight

                if gene_id in my_chrom.genes and gene_id in other_chrom.genes:
                    my_gene = my_chrom.genes[gene_id]
                    other_gene = other_chrom.genes[gene_id]

                    # Similarité basée sur la valeur du gène et la dominance
                    value_diff = abs(my_gene.value - other_gene.value)
                    dominance_diff = abs(my_gene.dominance - other_gene.dominance)

                    # Seuil de similarité plus strict pour les gènes fondamentaux
                    similarity_threshold = 0.15 if gene_id in fundamental_genes else 0.25

                    if value_diff < similarity_threshold and dominance_diff < 0.3:
                        matching_genes += gene_weight

        if total_genes == 0:
            return 0.5  # Valeur moyenne par défaut

        similarity = matching_genes / total_genes
        return 1.0 - similarity

    def _calculate_species_dominance(self) -> float:
        """Calcule la dominance de l'espèce basée sur divers facteurs génétiques et phénotypiques."""
        # Facteurs qui contribuent à la dominance d'une espèce
        dominance_factors = {
            # Facteurs génétiques
            "genetic_stability": self.genome.get_gene_value("immune_system") * 0.5 +
                                self.genome.get_gene_value("metabolism_efficiency") * 0.5,

            # Facteurs phénotypiques
            "physical_dominance": self.phenotype.strength * 0.3 +
                                 self.phenotype.size * 0.3 +
                                 self.phenotype.max_speed * 0.4,

            # Facteurs d'adaptation
            "adaptation": self.adaptation_score,

            # Facteurs de reproduction
            "reproductive_success": min(1.0, self.offspring_count / 10) * 0.7 +
                                   self.genome.get_gene_value("fertility") * 0.3,

            # Facteur de génération (espèces plus anciennes = plus stables)
            "evolutionary_stability": min(1.0, self.generation / 50)
        }

        # Poids relatifs des différents facteurs
        weights = {
            "genetic_stability": 0.25,
            "physical_dominance": 0.2,
            "adaptation": 0.3,
            "reproductive_success": 0.15,
            "evolutionary_stability": 0.1
        }

        # Calcul de la dominance pondérée
        dominance = sum(dominance_factors[factor] * weights[factor] for factor in weights)

        # Normaliser entre 0 et 1
        return max(0.0, min(1.0, dominance))

    def _count_significant_mutations(self, offspring_genome: Genome) -> tuple:
        """
        Compte le nombre de mutations significatives dans le génome de la progéniture.
        Retourne un tuple (nombre de mutations, importance des mutations)

        Modèle amélioré pour un réalisme évolutif accru, basé sur la théorie de l'évolution moderne
        et la génétique des populations.
        """
        mutation_count = 0
        mutation_significance = 0.0
        total_genes_checked = 0

        # Catégorisation des gènes par leur importance évolutive
        gene_categories = {
            # Gènes fondamentaux (mutations très importantes, souvent létales si trop fortes)
            "core": [
                "metabolism_efficiency", "energy_storage", "waste_processing",
                "immune_system", "toxin_resistance", "temperature_tolerance"
            ],

            # Gènes morphologiques (mutations visibles, importantes pour la spéciation)
            "morphological": [
                "size", "body_structure", "limb_length", "skin_type", "coloration",
                "sensory_organs", "reproductive_organs"
            ],

            # Gènes comportementaux (mutations importantes pour l'adaptation)
            "behavioral": [
                "aggression", "sociability", "territoriality", "parental_care",
                "learning_capacity", "memory", "problem_solving"
            ],

            # Gènes adaptatifs (mutations importantes pour l'adaptation environnementale)
            "adaptive": [
                "speed", "agility", "strength", "vision", "hearing", "smell",
                "pressure_tolerance", "radiation_tolerance", "toxin_production"
            ],

            # Gènes reproductifs (mutations cruciales pour l'isolement reproductif)
            "reproductive": [
                "fertility", "maturation_rate", "offspring_count", "mating_display",
                "reproductive_timing", "gamete_compatibility"
            ]
        }

        # Aplatir la liste pour vérification rapide
        all_categorized_genes = []
        for category, genes in gene_categories.items():
            all_categorized_genes.extend(genes)

        # Poids des mutations par catégorie (impact sur la spéciation)
        category_weights = {
            "core": 1.0,         # Mutations fondamentales - impact modéré sur la spéciation mais crucial pour la viabilité
            "morphological": 2.0, # Mutations morphologiques - fort impact sur la spéciation (isolement mécanique)
            "behavioral": 1.5,    # Mutations comportementales - impact significatif (isolement comportemental)
            "adaptive": 1.2,      # Mutations adaptatives - impact modéré à fort selon l'environnement
            "reproductive": 2.5   # Mutations reproductives - impact maximal (isolement reproductif)
        }

        # Pour chaque chromosome
        for i in range(min(len(self.genome.chromosomes), len(offspring_genome.chromosomes))):
            my_chrom = self.genome.chromosomes[i]
            offspring_chrom = offspring_genome.chromosomes[i]

            # Pour chaque gène présent dans les deux chromosomes
            common_genes = set(my_chrom.genes.keys()) & set(offspring_chrom.genes.keys())
            total_genes_checked += len(common_genes)

            # Gènes ajoutés ou supprimés (événements rares mais importants)
            added_genes = set(offspring_chrom.genes.keys()) - set(my_chrom.genes.keys())
            removed_genes = set(my_chrom.genes.keys()) - set(offspring_chrom.genes.keys())
            total_genes_checked += len(added_genes) + len(removed_genes)

            # Vérification des mutations dans les gènes communs
            for gene_id in common_genes:
                # Déterminer la catégorie du gène
                gene_category = None
                for category, genes in gene_categories.items():
                    if any(gene_name in gene_id for gene_name in genes):
                        gene_category = category
                        break

                # Si le gène n'est pas catégorisé, lui donner un poids standard
                category_weight = category_weights.get(gene_category, 1.0) if gene_category else 1.0

                my_gene = my_chrom.genes[gene_id]
                offspring_gene = offspring_chrom.genes[gene_id]

                # Seuils de mutation différents selon la catégorie du gène
                # Les gènes fondamentaux ont des seuils plus bas (mutations plus rares)
                if gene_category == "core":
                    value_threshold = 0.15
                elif gene_category == "reproductive":
                    value_threshold = 0.18
                elif gene_category == "morphological":
                    value_threshold = 0.20
                else:
                    value_threshold = 0.25

                # Vérification des mutations significatives
                value_diff = abs(my_gene.value - offspring_gene.value)
                dominance_diff = abs(my_gene.dominance - offspring_gene.dominance)

                # Analyse de l'impact évolutif de la mutation
                if value_diff > value_threshold:
                    # Calcul de l'impact basé sur l'ampleur du changement et l'importance du gène
                    impact = value_diff * category_weight

                    # Mutations dans les gènes fondamentaux peuvent être létales
                    if gene_category == "core" and value_diff > 0.5:
                        impact *= 1.5  # Mutation potentiellement délétère

                    # Mutations morphologiques importantes pour la spéciation
                    if gene_category == "morphological" and value_diff > 0.3:
                        impact *= 1.8  # Changement morphologique significatif

                    # Mutations reproductives cruciales pour l'isolement reproductif
                    if gene_category == "reproductive" and value_diff > 0.25:
                        impact *= 2.0  # Potentiel d'isolement reproductif

                    mutation_count += max(1, int(impact))
                    mutation_significance += impact

                # Changements dans la dominance des gènes (important pour l'expression phénotypique)
                if dominance_diff > 0.3:
                    dominance_impact = dominance_diff * category_weight * 0.8
                    mutation_count += max(1, int(dominance_impact))
                    mutation_significance += dominance_impact

                # Changements dans le taux de mutation (évolution du potentiel évolutif)
                mutation_rate_diff = abs(my_gene.mutation_rate - offspring_gene.mutation_rate)
                if mutation_rate_diff > 0.01:
                    # Les changements dans le taux de mutation peuvent accélérer l'évolution future
                    mutation_count += 1
                    mutation_significance += 0.5 * category_weight

            # Analyse des gènes ajoutés (innovations génétiques)
            for gene_id in added_genes:
                # Déterminer la catégorie du gène ajouté
                gene_category = None
                for category, genes in gene_categories.items():
                    if any(gene_name in gene_id for gene_name in genes):
                        gene_category = category
                        break

                category_weight = category_weights.get(gene_category, 1.0) if gene_category else 1.0

                # L'ajout d'un gène est un événement évolutif majeur
                impact = 1.0 * category_weight

                # L'ajout de gènes morphologiques ou reproductifs est particulièrement important
                if gene_category in ["morphological", "reproductive"]:
                    impact *= 1.5

                mutation_count += max(1, int(impact))
                mutation_significance += impact

            # Analyse des gènes supprimés (perte de fonction)
            for gene_id in removed_genes:
                # Déterminer la catégorie du gène supprimé
                gene_category = None
                for category, genes in gene_categories.items():
                    if any(gene_name in gene_id for gene_name in genes):
                        gene_category = category
                        break

                category_weight = category_weights.get(gene_category, 1.0) if gene_category else 1.0

                # La suppression d'un gène fondamental est souvent délétère
                if gene_category == "core":
                    impact = 1.5 * category_weight  # Potentiellement létal
                else:
                    impact = 0.8 * category_weight  # Moins critique

                mutation_count += max(1, int(impact))
                mutation_significance += impact

        # Vérification des chromosomes supplémentaires ou manquants (polyploïdie, aneuploïdie)
        if len(offspring_genome.chromosomes) != len(self.genome.chromosomes):
            # Changement dans le nombre de chromosomes = événement évolutif majeur
            # Peut causer un isolement reproductif immédiat (spéciation sympatrique)
            chrom_diff = abs(len(offspring_genome.chromosomes) - len(self.genome.chromosomes))

            # Impact massif sur la spéciation
            mutation_count += chrom_diff * 5
            mutation_significance += chrom_diff * 3.0

        # Ajustement pour le type d'organisme et sa complexité
        if self.organism_type == OrganismType.UNICELLULAR:
            # Les unicellulaires ont plus de mutations mais un génome plus simple
            mutation_count = int(mutation_count * 1.2)  # Plus de mutations
            mutation_significance *= 0.8  # Mais impact individuel moindre
        elif self.organism_type == OrganismType.PLANT:
            # Les plantes ont souvent une plus grande tolérance à la polyploïdie
            if len(offspring_genome.chromosomes) > len(self.genome.chromosomes):
                mutation_significance *= 0.9  # Impact réduit des changements chromosomiques
            else:
                mutation_significance *= 1.0  # Impact normal des autres mutations
        elif self.organism_type == OrganismType.CARNIVORE:
            # Les carnivores ont souvent une sélection plus forte
            mutation_count = int(mutation_count * 0.9)  # Moins de mutations viables
            mutation_significance *= 1.3  # Mais impact plus fort (sélection plus stricte)
        elif self.organism_type == OrganismType.HERBIVORE:
            # Les herbivores ont une pression de sélection intermédiaire
            mutation_significance *= 1.1
        elif self.organism_type == OrganismType.OMNIVORE:
            # Les omnivores ont une plus grande plasticité adaptative
            mutation_significance *= 1.2

        # Normaliser l'importance des mutations entre 0 et 1
        if total_genes_checked > 0:
            mutation_significance = min(1.0, mutation_significance / (total_genes_checked * 0.8))
        else:
            mutation_significance = 0.0

        return mutation_count, mutation_significance
    
    def _calculate_adaptation_score(self):
        """Calcule un score d'adaptation basé sur les traits phénotypiques."""
        # Facteurs d'adaptation de base
        energy_factor = self.phenotype.energy_capacity / 500  # Max 1.0
        speed_factor = self.phenotype.max_speed / 10  # Max 1.0
        lifespan_factor = self.phenotype.lifespan / 1000  # Max 1.0

        # Facteurs spécifiques au type d'organisme
        type_specific_score = 0.0

        if self.organism_type == OrganismType.UNICELLULAR:
            # Les unicellulaires valorisent l'efficacité métabolique et la résistance
            type_specific_score = (self.phenotype.metabolism_rate * 0.5 +
                                  self.phenotype.toxin_resistance * 0.5)

        elif self.organism_type == OrganismType.PLANT:
            # Les plantes valorisent l'efficacité photosynthétique et la résistance aux conditions
            type_specific_score = (self.phenotype.metabolism_rate * 0.3 +
                                  self.phenotype.temperature_range * 0.4 +
                                  self.phenotype.waste_tolerance * 0.3)

        elif self.organism_type == OrganismType.HERBIVORE:
            # Les herbivores valorisent la vitesse et les sens
            type_specific_score = (speed_factor * 0.4 +
                                  self.phenotype.vision_range / 50 * 0.3 +
                                  self.phenotype.smell_sensitivity * 0.3)

        elif self.organism_type == OrganismType.CARNIVORE:
            # Les carnivores valorisent la force et l'attaque
            type_specific_score = (self.phenotype.strength * 0.4 +
                                  self.phenotype.attack_power / 10 * 0.4 +
                                  speed_factor * 0.2)

        elif self.organism_type == OrganismType.OMNIVORE:
            # Les omnivores valorisent l'équilibre et l'adaptabilité
            type_specific_score = (self.phenotype.problem_solving * 0.3 +
                                  self.phenotype.temperature_range / 50 * 0.3 +
                                  self.phenotype.metabolism_rate * 0.2 +
                                  speed_factor * 0.2)

        # Score final combiné
        self.adaptation_score = (energy_factor * 0.2 +
                               lifespan_factor * 0.2 +
                               type_specific_score * 0.6)

        return self.adaptation_score

    def die(self):
        """Gère la mort de l'organisme."""
        self.is_alive = False
        # La décomposition et retour à l'écosystème sera géré par le World

    def get_details(self) -> dict:
        """Renvoie un dictionnaire avec les détails de l'organisme pour l'affichage."""
        return {
            "ID": self.id[:8],  # Version courte de l'UUID
            "Type": self.organism_type.name,
            "Génération": self.generation,
            "Âge": f"{self.age:.1f}",
            "Santé": f"{self.health:.1f}%",
            "Énergie": f"{self.energy:.1f}/{self.phenotype.energy_capacity:.1f}",
            "Hydratation": f"{self.hydration:.1f}%",
            "Taille": f"{self.phenotype.size:.2f}",
            "Vitesse max": f"{self.phenotype.max_speed:.2f}",
            "Force": f"{self.phenotype.strength:.2f}",
            "Métabolisme": f"{self.phenotype.metabolism_rate:.2f}",
            "Vision": f"{self.phenotype.vision_range:.1f}",
            "Adaptation": f"{self.adaptation_score:.2f}",
            "Descendants": self.offspring_count,
            "Espèce": self.species_id[:8]  # Version courte de l'UUID
        }
    
    def decide_action(self, world, nearby_organisms):
        """Décide de l'action à effectuer en fonction de l'environnement."""
        if not self.is_alive or self.maturity < 0.5:  # Les jeunes ont une mobilité limitée
            self.velocity = (0, 0)
            return
        
        # Priorités en fonction des besoins
        priorities = []
        
        # 1. Survie immédiate (eau si déshydraté)
        if self.hydration < 30:
            priorities.append(("find_water", 10))
        
        # 2. Nourriture si faim
        if self.energy < self.phenotype.energy_capacity * 0.4:
            if self.organism_type == OrganismType.PLANT or self.organism_type == OrganismType.UNICELLULAR:
                priorities.append(("find_sunlight", 8))
            elif self.organism_type == OrganismType.HERBIVORE:
                priorities.append(("find_plants", 8))
            elif self.organism_type == OrganismType.CARNIVORE:
                priorities.append(("hunt", 8))
            elif self.organism_type == OrganismType.OMNIVORE:
                priorities.append(("find_food", 8))
        
        # 3. Reproduction si prêt
        if self.ready_to_mate:
            priorities.append(("find_mate", 6))
        
        # 4. Fuite si menacé
        if self.organism_type != OrganismType.CARNIVORE:
            predators = [org for org in nearby_organisms if org.organism_type == OrganismType.CARNIVORE]
            if predators:
                priorities.append(("flee_predator", 9))
        
        # 5. Exploration (comportement par défaut)
        priorities.append(("explore", 1))
        
        # Trier par priorité et choisir l'action la plus importante
        priorities.sort(key=lambda x: x[1], reverse=True)
        action = priorities[0][0]
        
        # Exécuter l'action choisie
        if action == "find_water":
            self._move_towards_resource(world, ResourceType.WATER)
        elif action == "find_sunlight":
            self._move_towards_resource(world, ResourceType.SUNLIGHT)
        elif action == "find_plants":
            self._move_towards_resource(world, ResourceType.ORGANIC_MATTER)
        elif action == "hunt":
            self._hunt_prey(nearby_organisms)
        elif action == "find_food":
            if random.random() < 0.7:  # Préfère les plantes
                self._move_towards_resource(world, ResourceType.ORGANIC_MATTER)
            else:
                self._hunt_prey(nearby_organisms)
        elif action == "find_mate":
            self._seek_mate(nearby_organisms)
        elif action == "flee_predator":
            self._flee_from_predators(nearby_organisms)
        elif action == "explore":
            self._explore()
    
    def _move_towards_resource(self, world, resource_type):
        """Se déplace vers une ressource spécifique."""
        # Détection de ressources dans un rayon visuel
        best_cell = None
        best_value = 0
        vision_range = self.phenotype.vision_range
        
        for dx in range(-int(vision_range), int(vision_range) + 1):
            for dy in range(-int(vision_range), int(vision_range) + 1):
                check_pos = (
                    self.position[0] + dx,
                    self.position[1] + dy
                )
                
                # Vérifie si la position est dans les limites du monde
                if (0 <= check_pos[0] < world.width and 
                    0 <= check_pos[1] < world.height):
                    
                    # Distance à la position
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > vision_range:
                        continue
                    
                    cell = world.get_cell_at_position(check_pos)
                    if cell and cell.resources[resource_type] > best_value:
                        best_cell = cell
                        best_value = cell.resources[resource_type]
        
        if best_cell:
            # Calcul du vecteur de direction
            dx = best_cell.position[0] - self.position[0]
            dy = best_cell.position[1] - self.position[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 0:
                # Normalisation et application de la vitesse
                self.velocity = (
                    dx / dist * self.phenotype.max_speed,
                    dy / dist * self.phenotype.max_speed
                )
        else:
            # Pas de ressource trouvée, exploration aléatoire
            self._explore()
    
    def _hunt_prey(self, nearby_organisms):
        """Chasse les proies potentielles."""
        prey_types = [OrganismType.HERBIVORE, OrganismType.UNICELLULAR]
        if self.organism_type == OrganismType.OMNIVORE:
            prey_types.append(OrganismType.PLANT)
        
        potential_prey = [
            org for org in nearby_organisms 
            if org.organism_type in prey_types and org.is_alive
        ]
        
        if not potential_prey:
            self._explore()
            return
        
        # Sélectionne la proie la plus faible/proche
        best_prey = None
        best_score = float('-inf')
        
        for prey in potential_prey:
            dist = math.sqrt((prey.position[0] - self.position[0])**2 + 
                             (prey.position[1] - self.position[1])**2)
            
            if dist > self.phenotype.vision_range:
                continue
                
            # Score basé sur la faiblesse de la proie et la proximité
            health_factor = (100 - prey.health) / 100
            distance_factor = 1 - (dist / self.phenotype.vision_range)
            size_factor = 1 - (prey.phenotype.size / 3)  # Préfère les plus petites proies
            
            prey_score = health_factor * 0.4 + distance_factor * 0.4 + size_factor * 0.2
            
            if prey_score > best_score:
                best_prey = prey
                best_score = prey_score
        
        if best_prey:
            # Se dirige vers la proie
            dx = best_prey.position[0] - self.position[0]
            dy = best_prey.position[1] - self.position[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 0:
                self.velocity = (
                    dx / dist * self.phenotype.max_speed,
                    dy / dist * self.phenotype.max_speed
                )
                
                # Attaque si suffisamment proche
                if dist < 2:
                    self._attack(best_prey)
        else:
            self._explore()
    
    def _attack(self, target):
        """Attaque une cible."""
        # Calcul des dégâts basés sur la force et l'attaque
        damage = self.phenotype.attack_power * (0.5 + 0.5 * self.phenotype.strength)
        
        # La défense de la cible réduit les dégâts
        effective_damage = damage * (1 - target.phenotype.defense_power / 15)
        
        # Application des dégâts
        target.health -= max(0, effective_damage)
        
        # Si la cible meurt, gain d'énergie pour le prédateur
        if target.health <= 0:
            energy_gained = target.phenotype.size * 50 * self.phenotype.metabolism_rate
            self.energy = min(self.phenotype.energy_capacity, self.energy + energy_gained)
    
    def _seek_mate(self, nearby_organisms):
        """Cherche un partenaire pour la reproduction."""
        potential_mates = [
            org for org in nearby_organisms
            if org.organism_type == self.organism_type and 
            org.ready_to_mate and
            org.id != self.id
        ]
        
        if not potential_mates:
            self._explore()
            return
        
        # Trouver le partenaire le plus compatible/proche
        best_mate = None
        best_score = float('-inf')
        
        for mate in potential_mates:
            dist = math.sqrt((mate.position[0] - self.position[0])**2 + 
                            (mate.position[1] - self.position[1])**2)
            
            if dist > self.phenotype.vision_range:
                continue
            
            # Score basé sur la proximité et la compatibilité génétique
            distance_factor = 1 - (dist / self.phenotype.vision_range)
            health_factor = mate.health / 100
            
            # Préférence pour la diversité génétique (évite la consanguinité)
            genetic_diversity = random.random()  # Simplification, devrait comparer les génomes
            
            mate_score = distance_factor * 0.4 + health_factor * 0.3 + genetic_diversity * 0.3
            
            if mate_score > best_score:
                best_mate = mate
                best_score = mate_score
        
        if best_mate:
            # Se dirige vers le partenaire
            dx = best_mate.position[0] - self.position[0]
            dy = best_mate.position[1] - self.position[1]
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 0:
                self.velocity = (
                    dx / dist * self.phenotype.max_speed,
                    dy / dist * self.phenotype.max_speed
                )
        else:
            self._explore()
    
    def _flee_from_predators(self, nearby_organisms):
        """Fuit les prédateurs à proximité."""
        predator_types = [OrganismType.CARNIVORE, OrganismType.OMNIVORE]
        
        predators = [
            org for org in nearby_organisms 
            if org.organism_type in predator_types and org.is_alive
        ]
        
        if not predators:
            self._explore()
            return
        
        # Calcul du vecteur de fuite (s'éloigne des prédateurs)
        flee_x, flee_y = 0, 0
        
        for predator in predators:
            dist = math.sqrt((predator.position[0] - self.position[0])**2 + 
                            (predator.position[1] - self.position[1])**2)
            
            if dist < self.phenotype.vision_range:
                # Vecteur d'éloignement pondéré par l'inverse de la distance
                weight = 1 / max(1, dist)
                flee_x -= (predator.position[0] - self.position[0]) * weight
                flee_y -= (predator.position[1] - self.position[1]) * weight
        
        # Normalisation et application de la vitesse de fuite
        magnitude = math.sqrt(flee_x**2 + flee_y**2)
        if magnitude > 0:
            flee_speed = self.phenotype.max_speed * (1 + 0.2 * self.phenotype.agility)  # Boost d'adrénaline
            self.velocity = (
                flee_x / magnitude * flee_speed,
                flee_y / magnitude * flee_speed
            )
        else:
            self._explore()
    
    def _explore(self, speed_factor=0.8):
        """Comportement d'exploration aléatoire amélioré avec facteur de vitesse variable."""
        # Chance de changer de direction adaptée au type d'organisme
        change_dir_prob = 0.05  # Probabilité de base

        # Ajuster selon le type d'organisme
        if self.organism_type == OrganismType.CARNIVORE:
            change_dir_prob = 0.03  # Plus persistant dans sa direction
        elif self.organism_type == OrganismType.HERBIVORE:
            change_dir_prob = 0.07  # Change plus souvent de direction (nerveux)
        elif self.organism_type == OrganismType.PLANT:
            change_dir_prob = 0.01  # Très peu de mouvement
            speed_factor *= 0.3     # Mouvement très lent

        # Changer de direction avec une probabilité qui dépend du type d'organisme
        if random.random() < change_dir_prob:
            # Angle aléatoire avec une préférence pour continuer dans la même direction générale
            if hasattr(self, 'velocity') and (self.velocity[0] != 0 or self.velocity[1] != 0):
                current_angle = math.atan2(self.velocity[1], self.velocity[0])
                # Variation limitée autour de la direction actuelle
                angle = current_angle + random.uniform(-math.pi/2, math.pi/2)
            else:
                angle = random.uniform(0, 2 * math.pi)

            # Vitesse variable selon le type et l'énergie
            base_speed = self.phenotype.max_speed * speed_factor
            energy_factor = max(0.5, self.energy / self.phenotype.energy_capacity)
            actual_speed = base_speed * energy_factor

            self.velocity = (
                math.cos(angle) * actual_speed,
                math.sin(angle) * actual_speed
            )
    
    def draw(self, surface, camera_offset=(0, 0), zoom=1.0, selected=False):
        """Dessine l'organisme sur la surface donnée."""
        if not self.is_alive:
            return

        # Calcul de la position à l'écran
        screen_x = (self.position[0] - camera_offset[0]) * zoom
        screen_y = (self.position[1] - camera_offset[1]) * zoom

        # Taille à l'écran basée sur la taille réelle et le zoom
        screen_size = max(2, int(self.phenotype.size * 5 * zoom))

        # Couleur basée sur le type d'organisme et le génome
        # Assure que la couleur est valide même si le phénotype n'a pas de couleur définie
        try:
            base_color = self.phenotype.color
            # Vérifier que base_color est un tuple valide de 3 entiers
            if not (isinstance(base_color, tuple) and len(base_color) == 3 and
                    all(isinstance(c, int) and 0 <= c <= 255 for c in base_color)):
                base_color = (128, 128, 128)  # Gris par défaut
        except (AttributeError, TypeError):
            base_color = (128, 128, 128)  # Gris par défaut

        # Ajustement de la couleur selon le type d'organisme
        if self.organism_type == OrganismType.PLANT:
            color = (
                min(255, int(base_color[0] * 0.5)),
                min(255, int(base_color[1] * 1.5)),
                min(255, int(base_color[2] * 0.5))
            )
        elif self.organism_type == OrganismType.HERBIVORE:
            color = (
                min(255, int(base_color[0] * 0.7)),
                min(255, int(base_color[1] * 1.3)),
                min(255, int(base_color[2] * 1.0))
            )
        elif self.organism_type == OrganismType.CARNIVORE:
            color = (
                min(255, int(base_color[0] * 1.5)),
                min(255, int(base_color[1] * 0.5)),
                min(255, int(base_color[2] * 0.5))
            )
        elif self.organism_type == OrganismType.OMNIVORE:
            color = (
                min(255, int(base_color[0] * 1.2)),
                min(255, int(base_color[1] * 0.8)),
                min(255, int(base_color[2] * 1.2))
            )
        else:  # UNICELLULAR
            color = base_color

        # Modifie la luminosité de la couleur en fonction de la santé
        health_factor = max(0.1, self.health / 100)  # Évite les valeurs trop faibles
        color = (
            max(0, min(255, int(color[0] * health_factor))),
            max(0, min(255, int(color[1] * health_factor))),
            max(0, min(255, int(color[2] * health_factor)))
        )

        # Dessine l'organisme selon son type
        if self.organism_type == OrganismType.UNICELLULAR:
            pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), screen_size)
        elif self.organism_type == OrganismType.PLANT:
            pygame.draw.polygon(surface, color, [
                (screen_x, screen_y - screen_size),
                (screen_x - screen_size, screen_y + screen_size),
                (screen_x + screen_size, screen_y + screen_size)
            ])
        else:
            # Forme plus complexe pour les animaux
            pygame.draw.polygon(surface, color, [
                (screen_x + screen_size, screen_y),
                (screen_x - screen_size/2, screen_y - screen_size/2),
                (screen_x - screen_size/2, screen_y + screen_size/2)
            ])

        # Indicateur de statut de reproduction
        if self.ready_to_mate:
            try:
                pygame.draw.circle(surface, (255, 255, 0), (int(screen_x), int(screen_y)),
                                  max(1, int(screen_size/4)))
            except (ValueError, TypeError):
                # En cas d'erreur, ignorer cet indicateur
                pass

        # Indicateur de sélection
        if selected:
            try:
                pygame.draw.circle(surface, (255, 255, 0), (int(screen_x), int(screen_y)),
                                  max(1, int(screen_size + 5)), 2)
            except (ValueError, TypeError):
                # En cas d'erreur, ignorer cet indicateur
                pass


class WorldCell:
    """Représente une cellule (ou case) dans le monde de simulation."""
    def __init__(self, position: Tuple[int, int], biome_type: BiomeType):
        self.position = position
        self.biome_type = biome_type
        
        # Ressources disponibles dans la cellule
        self.resources = {res_type: 0.0 for res_type in ResourceType}
        
        # Caractéristiques environnementales
        self.temperature = 20.0  # en degrés Celsius
        self.pressure = 1.0      # en atmosphères
        self.radiation = 0.0     # niveau de radiation (0-1)
        self.altitude = 0.0      # altitude relative (-1 à 1)
        
        # Paramètres pour les règles de croissance/diminution de ressources
        self.resource_capacity = {res_type: 100.0 for res_type in ResourceType}
        self.resource_regen_rate = {res_type: 0.1 for res_type in ResourceType}
        
        # Initialisation des ressources basée sur le biome
        self._initialize_biome_properties()
    
    def _initialize_biome_properties(self):
        """Initialise les propriétés de la cellule en fonction de son biome."""
        if self.biome_type == BiomeType.OCEAN:
            self.altitude = -0.8
            self.temperature = 15.0
            self.resources[ResourceType.WATER] = 100.0
            self.resources[ResourceType.SUNLIGHT] = 60.0
            self.resources[ResourceType.MINERALS] = 40.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 30.0
            
        elif self.biome_type == BiomeType.SHALLOW_WATER:
            self.altitude = -0.3
            self.temperature = 18.0
            self.resources[ResourceType.WATER] = 100.0
            self.resources[ResourceType.SUNLIGHT] = 80.0
            self.resources[ResourceType.MINERALS] = 60.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 70.0
            
        elif self.biome_type == BiomeType.BEACH:
            self.altitude = 0.0
            self.temperature = 22.0
            self.resources[ResourceType.WATER] = 60.0
            self.resources[ResourceType.SUNLIGHT] = 90.0
            self.resources[ResourceType.MINERALS] = 50.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 40.0
            
        elif self.biome_type == BiomeType.GRASSLAND:
            self.altitude = 0.2
            self.temperature = 20.0
            self.resources[ResourceType.WATER] = 50.0
            self.resources[ResourceType.SUNLIGHT] = 100.0
            self.resources[ResourceType.MINERALS] = 60.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 100.0
            
        elif self.biome_type == BiomeType.FOREST:
            self.altitude = 0.3
            self.temperature = 18.0
            self.resources[ResourceType.WATER] = 70.0
            self.resources[ResourceType.SUNLIGHT] = 60.0
            self.resources[ResourceType.MINERALS] = 70.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 150.0
            
        elif self.biome_type == BiomeType.MOUNTAIN:
            self.altitude = 0.8
            self.temperature = 10.0
            self.resources[ResourceType.WATER] = 30.0
            self.resources[ResourceType.SUNLIGHT] = 80.0
            self.resources[ResourceType.MINERALS] = 90.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 20.0
            
        elif self.biome_type == BiomeType.DESERT:
            self.altitude = 0.1
            self.temperature = 30.0
            self.resources[ResourceType.WATER] = 10.0
            self.resources[ResourceType.SUNLIGHT] = 100.0
            self.resources[ResourceType.MINERALS] = 40.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 10.0
            
        elif self.biome_type == BiomeType.TUNDRA:
            self.altitude = 0.4
            self.temperature = -5.0
            self.resources[ResourceType.WATER] = 20.0
            self.resources[ResourceType.SUNLIGHT] = 60.0
            self.resources[ResourceType.MINERALS] = 50.0
            self.resource_capacity[ResourceType.ORGANIC_MATTER] = 30.0
        
        # Initialisation de l'oxygène et du CO2
        self.resources[ResourceType.OXYGEN] = 20.0
        self.resources[ResourceType.CO2] = 0.4
        
        # Initialisation de la matière organique avec une valeur de départ
        self.resources[ResourceType.ORGANIC_MATTER] = self.resource_capacity[ResourceType.ORGANIC_MATTER] * 0.1
    
    def update(self, delta_time: float, neighboring_cells: List['WorldCell']):
        """Met à jour l'état de la cellule et ses ressources."""
        # Régénération naturelle des ressources
        for res_type in ResourceType:
            if res_type == ResourceType.SUNLIGHT:
                # La lumière du soleil ne se régénère pas, elle est constante
                continue
                
            if res_type == ResourceType.WATER:
                # L'eau se diffuse depuis les voisins
                self._diffuse_resource(ResourceType.WATER, neighboring_cells, delta_time)
                
                # Précipitations (plus fréquentes près de l'eau et en altitude)
                precipitation_factor = 0.01
                if self.altitude > 0.5:
                    precipitation_factor *= 1.5
                
                water_neighbors = sum(1 for cell in neighboring_cells 
                                     if cell.biome_type in [BiomeType.OCEAN, BiomeType.SHALLOW_WATER])
                precipitation_factor *= (1 + 0.1 * water_neighbors)
                
                if random.random() < precipitation_factor * delta_time:
                    self.resources[ResourceType.WATER] = min(
                        self.resource_capacity[ResourceType.WATER],
                        self.resources[ResourceType.WATER] + random.uniform(10, 20)
                    )
            
            elif res_type == ResourceType.MINERALS:
                # Lente régénération des minéraux
                if self.resources[res_type] < self.resource_capacity[res_type]:
                    regen_amount = self.resource_regen_rate[res_type] * delta_time * 0.1
                    self.resources[res_type] = min(
                        self.resource_capacity[res_type],
                        self.resources[res_type] + regen_amount
                    )
            
            elif res_type == ResourceType.ORGANIC_MATTER:
                # Croissance de la matière organique basée sur l'eau, la lumière et le CO2
                # Conditions assouplies pour favoriser la croissance
                if (self.resources[ResourceType.WATER] > 5 and  # Seuil réduit de 10 à 5
                    self.resources[ResourceType.SUNLIGHT] > 10 and  # Seuil réduit de 20 à 10
                    self.resources[ResourceType.CO2] > 0.05):  # Seuil réduit de 0.1 à 0.05

                    growth_factor = (
                        self.resources[ResourceType.WATER] / 100 *
                        self.resources[ResourceType.SUNLIGHT] / 100 *
                        self.resources[ResourceType.CO2] * 8  # Facteur augmenté de 5 à 8
                    ) * delta_time

                    # Ajustement basé sur la température - plage élargie
                    temp_factor = 1.0
                    if self.temperature < -5 or self.temperature > 45:  # Plage élargie
                        temp_factor = 0.3  # Légèrement augmenté de 0.2 à 0.3
                    elif self.temperature < 5 or self.temperature > 35:  # Plage élargie
                        temp_factor = 0.7  # Augmenté de 0.6 à 0.7

                    # Bonus pour les biomes favorables à la végétation
                    biome_factor = 1.0
                    if self.biome_type in [BiomeType.FOREST, BiomeType.RAINFOREST, BiomeType.GRASSLAND, BiomeType.SWAMP]:
                        biome_factor = 1.5

                    growth_amount = growth_factor * temp_factor * biome_factor * 3.0  # Multiplié par 3 au lieu de 2

                    # Régénération de base minimale pour éviter les déserts biologiques
                    min_growth = 0.05 * delta_time
                    growth_amount = max(min_growth, growth_amount)

                    self.resources[res_type] = min(
                        self.resource_capacity[res_type],
                        self.resources[res_type] + growth_amount
                    )

                    # Consommation de CO2 et production d'oxygène
                    self.resources[ResourceType.CO2] = max(
                        0.1,
                        self.resources[ResourceType.CO2] - growth_amount * 0.1
                    )
                    self.resources[ResourceType.OXYGEN] = min(
                        100,
                        self.resources[ResourceType.OXYGEN] + growth_amount * 0.2
                    )
                else:
                    # Régénération minimale même dans des conditions défavorables
                    min_growth = 0.02 * delta_time
                    self.resources[res_type] = min(
                        self.resource_capacity[res_type],
                        self.resources[res_type] + min_growth
                    )
            
            elif res_type == ResourceType.OXYGEN:
                # Diffusion d'oxygène
                self._diffuse_resource(ResourceType.OXYGEN, neighboring_cells, delta_time)
                
                # Conversion naturelle en CO2 (respiration bactérienne, etc.)
                conversion_amount = self.resources[ResourceType.OXYGEN] * 0.001 * delta_time
                self.resources[ResourceType.OXYGEN] = max(
                    0,
                    self.resources[ResourceType.OXYGEN] - conversion_amount
                )
                self.resources[ResourceType.CO2] = min(
                    1.0,
                    self.resources[ResourceType.CO2] + conversion_amount * 0.5
                )
            
            elif res_type == ResourceType.CO2:
                # Diffusion de CO2
                self._diffuse_resource(ResourceType.CO2, neighboring_cells, delta_time)
        
        # Évaporation de l'eau basée sur la température
        if self.temperature > 25 and self.resources[ResourceType.WATER] > 0:
            evaporation_rate = (self.temperature - 25) * 0.002 * delta_time
            water_loss = min(self.resources[ResourceType.WATER], evaporation_rate)
            self.resources[ResourceType.WATER] -= water_loss
            
            # Diffusion de l'eau évaporée vers les cellules voisines
            if neighboring_cells:
                water_per_neighbor = water_loss * 0.7 / len(neighboring_cells)
                for neighbor in neighboring_cells:
                    neighbor.resources[ResourceType.WATER] = min(
                        neighbor.resource_capacity[ResourceType.WATER],
                        neighbor.resources[ResourceType.WATER] + water_per_neighbor
                    )
    
    def _diffuse_resource(self, resource_type: ResourceType, neighboring_cells: List['WorldCell'], delta_time: float):
        """Diffuse une ressource vers et depuis les cellules voisines."""
        if not neighboring_cells:
            return
            
        # Taux de diffusion dépend du type de ressource
        diffusion_rates = {
            ResourceType.WATER: 0.005,
            ResourceType.OXYGEN: 0.01,
            ResourceType.CO2: 0.01
        }
        
        diffusion_rate = diffusion_rates.get(resource_type, 0) * delta_time
        
        # Calcul des différences de concentration
        total_flow = 0
        flows = []
        
        for neighbor in neighboring_cells:
            # Calculer le flux basé sur la différence de concentration
            diff = self.resources[resource_type] - neighbor.resources[resource_type]
            
            # Ajustement de la diffusion selon la topographie pour l'eau
            if resource_type == ResourceType.WATER:
                # L'eau coule vers le bas
                altitude_factor = (self.altitude - neighbor.altitude) * 2
                if altitude_factor > 0:  # Si nous sommes plus haut
                    diff += altitude_factor * 20
            
            flow = diff * diffusion_rate
            total_flow += flow
            flows.append((neighbor, flow))
        
        # Appliquer les flux calculés
        for neighbor, flow in flows:
            if flow > 0:  # Ressource quittant cette cellule
                actual_flow = min(flow, self.resources[resource_type])
                self.resources[resource_type] -= actual_flow
                neighbor.resources[resource_type] = min(
                    neighbor.resource_capacity[resource_type],
                    neighbor.resources[resource_type] + actual_flow
                )
    
    def add_decomposition(self, biomass: float):
        """Ajoute de la matière organique à la cellule suite à la décomposition."""
        self.resources[ResourceType.ORGANIC_MATTER] = min(
            self.resource_capacity[ResourceType.ORGANIC_MATTER],
            self.resources[ResourceType.ORGANIC_MATTER] + biomass * 0.5
        )
        
        # Une partie se transforme en minéraux
        self.resources[ResourceType.MINERALS] = min(
            self.resource_capacity[ResourceType.MINERALS],
            self.resources[ResourceType.MINERALS] + biomass * 0.2
        )
        
        # Production de CO2 par décomposition
        self.resources[ResourceType.CO2] = min(
            1.0,
            self.resources[ResourceType.CO2] + biomass * 0.1
        )
    
    def get_color(self) -> Tuple[int, int, int]:
        """Retourne la couleur représentative du biome et de son état."""
        base_colors = {
            # Biomes aquatiques
            BiomeType.DEEP_OCEAN: (0, 30, 100),
            BiomeType.OCEAN: (0, 70, 150),
            BiomeType.SHALLOW_WATER: (50, 120, 200),
            BiomeType.CORAL_REEF: (100, 180, 220),
            BiomeType.RIVER: (30, 100, 200),
            BiomeType.LAKE: (40, 110, 190),

            # Biomes côtiers
            BiomeType.BEACH: (194, 178, 128),

            # Biomes de plaine
            BiomeType.GRASSLAND: (76, 153, 0),
            BiomeType.SAVANNA: (180, 170, 50),

            # Biomes forestiers
            BiomeType.FOREST: (0, 102, 0),
            BiomeType.RAINFOREST: (0, 80, 0),
            BiomeType.MOUNTAIN_FOREST: (40, 100, 40),

            # Biomes humides
            BiomeType.SWAMP: (70, 90, 40),

            # Biomes montagneux
            BiomeType.MOUNTAIN: (120, 120, 120),
            BiomeType.VOLCANIC: (80, 30, 30),

            # Biomes arides
            BiomeType.DESERT: (194, 178, 78),
            BiomeType.DESERT_HILLS: (170, 150, 70),

            # Biomes froids
            BiomeType.TUNDRA: (180, 180, 200),
            BiomeType.ICE: (230, 230, 250)
        }

        base_color = base_colors.get(self.biome_type, (128, 128, 128))

        # Modifier la couleur en fonction de l'état des ressources
        water_influence = min(1.0, self.resources[ResourceType.WATER] / max(0.1, self.resource_capacity[ResourceType.WATER]))
        organic_influence = min(1.0, self.resources[ResourceType.ORGANIC_MATTER] / max(0.1, self.resource_capacity[ResourceType.ORGANIC_MATTER]))
        mineral_influence = min(1.0, self.resources[ResourceType.MINERALS] / max(0.1, self.resource_capacity[ResourceType.MINERALS]))

        # Facteur d'altitude pour les terres
        altitude_factor = 0
        if hasattr(self, 'altitude'):
            altitude_factor = max(0, min(1, (self.altitude + 1) / 2))  # Normaliser entre 0 et 1

        # Facteur de température
        temp_factor = 0
        if hasattr(self, 'temperature'):
            temp_factor = max(0, min(1, (self.temperature + 5) / 35))  # Normaliser entre 0 et 1

        # Ajustements de couleur

        # Bleuté si plus d'eau
        r = max(0, min(255, base_color[0] * (1 - water_influence * 0.3)))
        g = max(0, min(255, base_color[1] * (1 - water_influence * 0.1)))
        b = max(0, min(255, base_color[2] + (255 - base_color[2]) * water_influence * 0.3))

        # Plus vert si plus de matière organique
        r = max(0, min(255, r * (1 - organic_influence * 0.2)))
        g = max(0, min(255, g + (255 - g) * organic_influence * 0.3))
        b = max(0, min(255, b * (1 - organic_influence * 0.2)))

        # Plus clair si plus d'altitude (pour les terres)
        if self.biome_type not in [BiomeType.DEEP_OCEAN, BiomeType.OCEAN, BiomeType.SHALLOW_WATER,
                                  BiomeType.CORAL_REEF, BiomeType.RIVER, BiomeType.LAKE]:
            brightness = 1.0 + altitude_factor * 0.3
            r = max(0, min(255, r * brightness))
            g = max(0, min(255, g * brightness))
            b = max(0, min(255, b * brightness))

        # Plus rouge/jaune si plus chaud
        if temp_factor > 0.6:
            heat_influence = (temp_factor - 0.6) / 0.4  # 0 à 1 pour les températures élevées
            r = max(0, min(255, r + (255 - r) * heat_influence * 0.3))
            g = max(0, min(255, g + (255 - g) * heat_influence * 0.1))

        # Plus bleu/blanc si très froid
        if temp_factor < 0.3:
            cold_influence = (0.3 - temp_factor) / 0.3  # 0 à 1 pour les températures basses
            r = max(0, min(255, r + (255 - r) * cold_influence * 0.2))
            g = max(0, min(255, g + (255 - g) * cold_influence * 0.2))
            b = max(0, min(255, b + (255 - b) * cold_influence * 0.3))

        return (int(r), int(g), int(b))


class SpatialGrid:
    """Système de partitionnement spatial pour optimiser les recherches de proximité."""
    def __init__(self, width: int, height: int, cell_size: int = 50):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size + 1
        self.grid_height = height // cell_size + 1

        # Grille de cellules contenant des listes d'organismes
        self.grid = [[[] for _ in range(self.grid_height)] for _ in range(self.grid_width)]

        # Dictionnaire pour retrouver rapidement la position d'un organisme dans la grille
        self.organism_positions = {}  # organism_id -> (grid_x, grid_y)

    def add_organism(self, organism: 'Organism'):
        """Ajoute un organisme à la grille spatiale."""
        grid_x, grid_y = self._get_grid_position(organism.position)

        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.grid[grid_x][grid_y].append(organism)
            self.organism_positions[organism.id] = (grid_x, grid_y)

    def remove_organism(self, organism: 'Organism'):
        """Retire un organisme de la grille spatiale."""
        if organism.id in self.organism_positions:
            grid_x, grid_y = self.organism_positions[organism.id]

            if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                if organism in self.grid[grid_x][grid_y]:
                    self.grid[grid_x][grid_y].remove(organism)

            del self.organism_positions[organism.id]

    def update_organism_position(self, organism: 'Organism'):
        """Met à jour la position d'un organisme dans la grille spatiale."""
        if organism.id in self.organism_positions:
            old_grid_x, old_grid_y = self.organism_positions[organism.id]
            new_grid_x, new_grid_y = self._get_grid_position(organism.position)

            # Si la position de grille a changé
            if old_grid_x != new_grid_x or old_grid_y != new_grid_y:
                # Retirer de l'ancienne cellule
                if 0 <= old_grid_x < self.grid_width and 0 <= old_grid_y < self.grid_height:
                    if organism in self.grid[old_grid_x][old_grid_y]:
                        self.grid[old_grid_x][old_grid_y].remove(organism)

                # Ajouter à la nouvelle cellule
                if 0 <= new_grid_x < self.grid_width and 0 <= new_grid_y < self.grid_height:
                    self.grid[new_grid_x][new_grid_y].append(organism)
                    self.organism_positions[organism.id] = (new_grid_x, new_grid_y)
                else:
                    # Si l'organisme est hors limites, le supprimer de la grille
                    if organism.id in self.organism_positions:
                        del self.organism_positions[organism.id]

    def get_nearby_organisms(self, position: Tuple[float, float], radius: float) -> List['Organism']:
        """Récupère tous les organismes dans un rayon donné autour d'une position."""
        center_x, center_y = self._get_grid_position(position)
        cell_radius = int(radius / self.cell_size) + 1

        nearby = []

        # Parcourir les cellules dans le rayon
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                grid_x, grid_y = center_x + dx, center_y + dy

                if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                    # Ajouter tous les organismes de cette cellule
                    for organism in self.grid[grid_x][grid_y]:
                        if organism.is_alive:
                            # Vérification précise de la distance
                            dist = math.sqrt((position[0] - organism.position[0])**2 +
                                           (position[1] - organism.position[1])**2)

                            if dist <= radius:
                                nearby.append(organism)

        return nearby

    def get_all_organisms(self) -> List['Organism']:
        """Récupère tous les organismes de la grille."""
        all_organisms = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                all_organisms.extend(self.grid[x][y])
        return all_organisms

    def _get_grid_position(self, position: Tuple[float, float]) -> Tuple[int, int]:
        """Convertit une position du monde en indices de grille."""
        grid_x = int(position[0] / self.cell_size)
        grid_y = int(position[1] / self.cell_size)
        return grid_x, grid_y

    def clear(self):
        """Vide la grille spatiale."""
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                self.grid[x][y].clear()
        self.organism_positions.clear()

class World:
    """Représente le monde de simulation avec toutes les cellules et organismes."""
    def __init__(self, width: int, height: int, cell_size: int = 10):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size

        # Création de la grille de cellules
        self.grid = [[None for _ in range(self.grid_height)] for _ in range(self.grid_width)]

        # Liste des organismes vivant dans le monde
        self.organisms = []

        # Grille spatiale pour optimiser les recherches de proximité
        self.spatial_grid = SpatialGrid(width, height, cell_size=50)  # Cellules plus grandes pour la grille spatiale

        # État global de l'environnement
        self.global_temperature = 20.0
        self.climate_cycle = 0.0  # Pour les cycles climatiques
        self.day_night_cycle = 0.0  # Pour le cycle jour/nuit (0-1)
        self.year_cycle = 0.0  # Position dans l'année (0-1)
        self.season = 0  # Saison actuelle (0-3: printemps, été, automne, hiver)
        self.year = 0  # Compteur d'années simulées
        self.day = 0  # Compteur de jours simulés
        self.time_of_day = 0.0  # Heure de la journée en heures (0-24)
        self.weather_conditions = {
            "precipitation": 0.0,  # 0-1 (aucune à forte)
            "cloud_cover": 0.0,    # 0-1 (clair à couvert)
            "wind_speed": 0.0,     # 0-1 (calme à tempête)
            "wind_direction": 0.0  # 0-2π (radians)
        }
        self.natural_disasters = []  # Liste des catastrophes naturelles actives

        # Statistiques de l'écosystème
        self.species_stats = {org_type: 0 for org_type in OrganismType}  # Statistiques par type d'organisme
        self.species_registry = {}  # Registre des espèces {species_id: {name, count, first_appearance, etc.}}
        self.historical_data = []  # Données historiques
        self.max_generation = 1  # Génération maximale atteinte
        self.extinction_count = 0  # Nombre d'espèces éteintes
        self.speciation_events = 0  # Nombre d'événements de spéciation

        # Suivi de l'évolution
        self.evolutionary_milestones = []  # Événements évolutifs importants
        self.adaptation_by_biome = {}  # Adaptation moyenne par biome
        self.dominant_species = {}  # Espèces dominantes par type d'organisme

        # Événements naturels
        self.active_events = []  # Liste des événements en cours
        self.selection_pressure = 1.0  # Pression de sélection naturelle (1.0 = normale)

        # Paramètres de performance
        self.max_organisms = 20000  # Limite pour éviter les problèmes de performance
        self.lod_thresholds = {  # Seuils pour le niveau de détail
            5000: 1.0,   # Jusqu'à 5000 organismes: détail complet
            10000: 0.5,  # Jusqu'à 10000: mise à jour d'un organisme sur deux
            15000: 0.25, # Jusqu'à 15000: mise à jour d'un organisme sur quatre
            20000: 0.1   # Au-delà: mise à jour minimale
        }
        self.update_counter = 0  # Compteur pour les mises à jour partielles

        # Génération du monde
        self._generate_world()
    
    def _generate_world(self):
        """Génère le monde avec des biomes réalistes en utilisant le bruit de Perlin."""
        # Seed pour la génération procédurale
        seed = random.randint(0, 10000)
        random.seed(seed)
        print(f"Génération du monde avec seed: {seed}")

        # Ratios de biomes par défaut si non spécifiés - plus réalistes
        if not hasattr(self, 'biome_ratios'):
            self.biome_ratios = {
                "ocean": 0.65,       # Les océans couvrent environ 70% de la Terre
                "mountain": 0.10,    # Zones montagneuses
                "forest": 0.12,      # Forêts diverses
                "desert": 0.05,      # Déserts
                "tundra": 0.03,      # Régions polaires
                "swamp": 0.03,       # Marécages et zones humides
                "volcanic": 0.01,    # Zones volcaniques rares
                "grassland": 0.06    # Prairies et savanes
            }

        # Implémentation du bruit de Perlin pour une génération plus réaliste
        def perlin_noise(x, y, octaves=6, persistence=0.5, lacunarity=2.0, scale=100.0):
            """Génère une valeur de bruit de Perlin à la position (x, y)."""
            total = 0
            amplitude = 1.0
            frequency = 1.0
            max_value = 0  # Utilisé pour normaliser le résultat

            # Ajouter plusieurs octaves de bruit
            for _ in range(octaves):
                # Utiliser une fonction de bruit simplifiée basée sur le sinus
                # Dans une implémentation réelle, on utiliserait une vraie bibliothèque de bruit de Perlin
                nx = x / scale * frequency
                ny = y / scale * frequency

                # Simuler le bruit de Perlin avec des fonctions trigonométriques
                noise_val = (math.sin(nx * 12.9898 + ny * 78.233) * 43758.5453) % 1
                noise_val += (math.cos(nx * 39.346 + ny * 11.135) * 53758.5453) % 1
                noise_val = (noise_val - 0.5) * 2  # Normaliser entre -1 et 1

                total += noise_val * amplitude

                max_value += amplitude
                amplitude *= persistence
                frequency *= lacunarity

            # Normaliser le résultat entre 0 et 1
            return (total / max_value + 1) / 2

        # Génération des cartes de base
        altitude_map = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        humidity_map = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        temperature_map = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]
        river_map = [[0 for _ in range(self.grid_height)] for _ in range(self.grid_width)]

        # Paramètres pour les différentes cartes
        altitude_scale = 150.0
        humidity_scale = 200.0
        temperature_scale = 250.0

        # Ajustement des seuils en fonction des ratios personnalisés
        ocean_threshold = self.biome_ratios.get("ocean", 0.35)
        mountain_threshold = 1.0 - self.biome_ratios.get("mountain", 0.15)
        forest_threshold = 0.5  # Humidité minimale pour les forêts
        desert_threshold = self.biome_ratios.get("desert", 0.1) * 2  # Humidité maximale pour les déserts

        print("Génération des cartes de terrain...")

        # Génération des cartes de base
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                # Coordonnées réelles
                real_x = x * self.cell_size
                real_y = y * self.cell_size

                # Génération de l'altitude avec plusieurs octaves
                altitude_map[x][y] = perlin_noise(real_x, real_y,
                                                octaves=8,
                                                persistence=0.5,
                                                scale=altitude_scale)

                # Génération de continents plus réalistes
                # Au lieu d'un simple biais vers le centre, créons plusieurs "plaques tectoniques"

                # Définir des centres de continents (si ce n'est pas déjà fait)
                if not hasattr(self, 'continent_centers'):
                    num_continents = random.randint(3, 6)  # Entre 3 et 6 continents
                    self.continent_centers = []
                    self.continent_sizes = []
                    self.continent_shapes = []

                    for _ in range(num_continents):
                        # Position aléatoire pour chaque continent
                        cx = random.uniform(0.1, 0.9) * self.grid_width
                        cy = random.uniform(0.1, 0.9) * self.grid_height
                        self.continent_centers.append((cx, cy))

                        # Taille aléatoire pour chaque continent
                        size = random.uniform(0.15, 0.35) * max(self.grid_width, self.grid_height)
                        self.continent_sizes.append(size)

                        # Forme aléatoire pour chaque continent (déformation)
                        shape = (random.uniform(0.7, 1.3), random.uniform(0.7, 1.3))
                        self.continent_shapes.append(shape)

                # Calculer l'influence de chaque continent sur ce point
                continental_influence = 0
                for i, (cx, cy) in enumerate(self.continent_centers):
                    # Distance au centre du continent, ajustée par la forme
                    dx = (x - cx) * self.continent_shapes[i][0]
                    dy = (y - cy) * self.continent_shapes[i][1]
                    distance = math.sqrt(dx*dx + dy*dy)

                    # Influence basée sur la distance et la taille du continent
                    size = self.continent_sizes[i]
                    # Fonction sigmoïde pour une transition douce entre continent et océan
                    influence = 1.0 / (1.0 + math.exp((distance - size*0.7) / (size*0.15)))

                    # Ajouter du bruit aux bords des continents
                    edge_noise = perlin_noise(x * 0.05 + i*100, y * 0.05 + i*100, octaves=3) * 0.2
                    influence *= (1.0 + edge_noise)

                    continental_influence = max(continental_influence, influence)

                # Ajuster l'altitude en fonction de l'influence continentale
                # Plus d'influence = plus haute altitude
                altitude_map[x][y] = altitude_map[x][y] * 0.4 + continental_influence * 0.6

                # Ajouter des chaînes de montagnes aux frontières des plaques (simulation tectonique)
                mountain_influence = 0
                for i, (cx, cy) in enumerate(self.continent_centers):
                    for j, (cx2, cy2) in enumerate(self.continent_centers):
                        if i >= j:
                            continue

                        # Calculer un point sur la ligne entre deux centres de continents
                        t = random.uniform(0.3, 0.7)  # Position aléatoire entre les continents
                        plate_border_x = cx * (1-t) + cx2 * t
                        plate_border_y = cy * (1-t) + cy2 * t

                        # Distance à cette frontière de plaque
                        border_dx = x - plate_border_x
                        border_dy = y - plate_border_y
                        border_dist = math.sqrt(border_dx*border_dx + border_dy*border_dy)

                        # Largeur de la chaîne de montagnes
                        mountain_width = random.uniform(0.05, 0.1) * max(self.grid_width, self.grid_height)

                        # Influence de la chaîne de montagnes
                        if border_dist < mountain_width:
                            # Plus proche du centre de la chaîne = plus haute montagne
                            mountain_factor = 1.0 - (border_dist / mountain_width)
                            mountain_influence = max(mountain_influence, mountain_factor * 0.5)

                # Ajouter l'influence des montagnes à l'altitude
                if mountain_influence > 0 and altitude_map[x][y] > self.biome_ratios["ocean"]:
                    altitude_map[x][y] += mountain_influence

                # Génération de l'humidité (décalée pour différencier)
                humidity_map[x][y] = perlin_noise(real_x + 1000, real_y + 1000,
                                                octaves=6,
                                                persistence=0.6,
                                                scale=humidity_scale)

                # La température dépend de la latitude (distance au centre vertical)
                # Normaliser y entre 0 et 1, puis ajuster pour que l'équateur soit au milieu
                normalized_y = y / (self.grid_height - 1)
                latitude_factor = abs(normalized_y * 2 - 1)  # 0 à l'équateur, 1 aux pôles

                # Base de température influencée par la latitude
                base_temp = 1.0 - latitude_factor * 0.8

                # Ajout de variations locales avec du bruit
                temp_noise = perlin_noise(real_x + 2000, real_y + 2000,
                                        octaves=4,
                                        persistence=0.4,
                                        scale=temperature_scale)

                # Combinaison des facteurs
                temperature_map[x][y] = base_temp * 0.8 + temp_noise * 0.2

                # Ajustement de la température en fonction de l'altitude (plus froid en altitude)
                if altitude_map[x][y] > ocean_threshold:  # Seulement pour les terres
                    altitude_temp_factor = (altitude_map[x][y] - ocean_threshold) / (1.0 - ocean_threshold)
                    temperature_map[x][y] -= altitude_temp_factor * 0.3

                # Ajustement de la température en fonction de la température globale
                temperature_map[x][y] *= (self.global_temperature / 20.0)

        print("Génération des rivières...")

        # Génération des rivières
        river_sources = []

        # Trouver des sources potentielles de rivières (points élevés)
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if altitude_map[x][y] > ocean_threshold + 0.2 and altitude_map[x][y] < mountain_threshold:
                    # Vérifier si c'est un maximum local
                    is_local_max = True
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
                                altitude_map[nx][ny] > altitude_map[x][y]):
                                is_local_max = False
                                break

                    if is_local_max and random.random() < 0.1:  # Limiter le nombre de sources
                        river_sources.append((x, y))

        # Tracer les rivières depuis les sources
        for source_x, source_y in river_sources:
            current_x, current_y = source_x, source_y
            river_strength = random.uniform(0.5, 1.0)  # Force initiale de la rivière

            # Suivre la pente descendante
            for _ in range(1000):  # Limite pour éviter les boucles infinies
                river_map[current_x][current_y] = max(river_map[current_x][current_y], river_strength)

                # Trouver la cellule voisine avec l'altitude la plus basse
                lowest_alt = altitude_map[current_x][current_y]
                next_x, next_y = current_x, current_y

                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = current_x + dx, current_y + dy
                        if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
                            altitude_map[nx][ny] < lowest_alt):
                            lowest_alt = altitude_map[nx][ny]
                            next_x, next_y = nx, ny

                # Si on ne peut pas descendre plus bas, arrêter
                if next_x == current_x and next_y == current_y:
                    break

                # Passer à la cellule suivante
                current_x, next_x = next_x, current_x
                current_y, next_y = next_y, current_y

                # Réduire légèrement la force de la rivière
                river_strength *= 0.99

                # Si on atteint l'océan, arrêter
                if altitude_map[current_x][current_y] < ocean_threshold:
                    break

        print("Création des biomes...")

        # Création des biomes basée sur l'altitude, l'humidité et la température
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                altitude = altitude_map[x][y]
                humidity = humidity_map[x][y]
                temperature = temperature_map[x][y]
                river_value = river_map[x][y]

                # Détermination du biome
                biome = self._determine_advanced_biome(altitude, humidity, temperature, river_value,
                                                    ocean_threshold, mountain_threshold,
                                                    forest_threshold, desert_threshold)

                # Création de la cellule
                cell = WorldCell((x * self.cell_size, y * self.cell_size), biome)
                cell.altitude = altitude * 2 - 1  # -1 à 1
                cell.temperature = temperature * 35 - 5  # -5°C à 30°C
                cell.humidity = humidity * 100  # 0 à 100%

                # Définir les ressources en fonction du biome
                self._initialize_cell_resources(cell)

                self.grid[x][y] = cell

        print("Monde généré avec succès!")

    def _determine_advanced_biome(self, altitude: float, humidity: float, temperature: float, river_value: float,
                                ocean_threshold: float, mountain_threshold: float,
                                forest_threshold: float, desert_threshold: float) -> BiomeType:
        """Détermine le biome en fonction de l'altitude, de l'humidité, de la température et des rivières avec un modèle plus réaliste."""

        # Facteurs environnementaux normalisés pour faciliter les calculs
        # Utiliser directement les variables normalisées dans les calculs suivants
        # puisqu'elles sont déjà entre 0 et 1

        # Facteur d'écotone - transition entre biomes (aléatoire pour créer des frontières naturelles)
        ecotone_factor = random.uniform(-0.05, 0.05)

        # Ajustement des seuils avec le facteur d'écotone pour des transitions plus naturelles
        ocean_threshold_adj = ocean_threshold + ecotone_factor
        mountain_threshold_adj = mountain_threshold + ecotone_factor
        forest_threshold_adj = forest_threshold + ecotone_factor
        desert_threshold_adj = desert_threshold + ecotone_factor

        # Rivières et lacs - priorité la plus élevée
        if river_value > 0.5:
            # Embouchures de rivières et deltas
            if altitude < ocean_threshold_adj + 0.05:
                return BiomeType.SHALLOW_WATER
            # Rivières principales
            elif river_value > 0.8:
                return BiomeType.RIVER
            # Zones humides autour des rivières
            elif humidity > 0.6:
                if temperature > 0.7:
                    return BiomeType.SWAMP
                else:
                    return BiomeType.LAKE
            # Rivières standard
            else:
                return BiomeType.RIVER

        # Zones océaniques et aquatiques
        if altitude < ocean_threshold_adj:
            # Océan profond
            if altitude < ocean_threshold_adj * 0.4:
                return BiomeType.DEEP_OCEAN
            # Océan standard
            elif altitude < ocean_threshold_adj * 0.7:
                return BiomeType.OCEAN
            # Récifs coralliens dans les eaux chaudes et peu profondes
            elif temperature > 0.7 and humidity > 0.6:
                # Variation pour créer des motifs de récifs
                coral_pattern = (math.sin(altitude * 100) + math.cos(humidity * 100)) * 0.5
                if coral_pattern > 0:
                    return BiomeType.CORAL_REEF
                else:
                    return BiomeType.SHALLOW_WATER
            # Eaux peu profondes standard
            else:
                return BiomeType.SHALLOW_WATER

        # Zones côtières - transition terre/mer
        elif altitude < ocean_threshold_adj + 0.08:
            # Plages tropicales
            if temperature > 0.7:
                return BiomeType.BEACH
            # Plages tempérées
            elif temperature > 0.4:
                # Alternance de plages et zones rocheuses
                if random.random() < 0.7:
                    return BiomeType.BEACH
                else:
                    return BiomeType.GRASSLAND
            # Côtes froides
            else:
                if random.random() < 0.5:
                    return BiomeType.BEACH
                else:
                    return BiomeType.TUNDRA

        # Zones montagneuses
        elif altitude > mountain_threshold_adj:
            # Sommets glacés
            if temperature < 0.15 or altitude > mountain_threshold_adj + 0.15:
                return BiomeType.ICE
            # Zones volcaniques - plus fréquentes à certaines "latitudes"
            elif random.random() < 0.08 and temperature > 0.5:
                return BiomeType.VOLCANIC
            # Toundra alpine
            elif temperature < 0.3:
                return BiomeType.TUNDRA
            # Forêts de montagne
            elif humidity > 0.55:
                # Variation de densité forestière
                if random.random() < humidity * 0.8:
                    return BiomeType.MOUNTAIN_FOREST
                else:
                    return BiomeType.MOUNTAIN
            # Montagnes standard
            else:
                return BiomeType.MOUNTAIN

        # Zones de plaine et intermédiaires - le plus complexe
        else:
            # Calcul de l'élévation relative dans la zone non-montagneuse/non-océanique
            relative_elevation = (altitude - ocean_threshold_adj) / (mountain_threshold_adj - ocean_threshold_adj)

            # Zones chaudes (tropicales et subtropicales)
            if temperature > 0.7:
                # Déserts chauds
                if humidity < desert_threshold_adj:
                    # Déserts de haute altitude
                    if relative_elevation > 0.6:
                        return BiomeType.DESERT_HILLS
                    # Déserts standards
                    else:
                        return BiomeType.DESERT
                # Savanes
                elif humidity < 0.45:
                    # Variation pour créer des motifs naturels
                    if random.random() < 0.2:
                        return BiomeType.GRASSLAND
                    else:
                        return BiomeType.SAVANNA
                # Forêts tropicales
                elif humidity < 0.7:
                    # Transition forêt/savane
                    if random.random() < 0.3:
                        return BiomeType.SAVANNA
                    else:
                        return BiomeType.FOREST
                # Forêts tropicales humides
                else:
                    # Marécages dans les zones basses
                    if relative_elevation < 0.3 and random.random() < 0.4:
                        return BiomeType.SWAMP
                    else:
                        return BiomeType.RAINFOREST

            # Zones tempérées
            elif temperature > 0.35:
                # Déserts tempérés
                if humidity < desert_threshold_adj:
                    if relative_elevation > 0.7:
                        return BiomeType.DESERT_HILLS
                    else:
                        return BiomeType.DESERT
                # Prairies et steppes
                elif humidity < 0.45:
                    # Variation pour créer des motifs naturels
                    if random.random() < humidity * 0.5:
                        return BiomeType.GRASSLAND
                    else:
                        if temperature > 0.5:
                            return BiomeType.SAVANNA
                        else:
                            return BiomeType.GRASSLAND
                # Forêts tempérées
                elif humidity < 0.7:
                    # Densité forestière variable
                    if random.random() < humidity * 0.7:
                        return BiomeType.FOREST
                    else:
                        return BiomeType.GRASSLAND
                # Forêts humides et marécages
                else:
                    # Marécages dans les zones basses
                    if relative_elevation < 0.25:
                        return BiomeType.SWAMP
                    # Forêts denses dans les zones plus élevées
                    else:
                        if temperature > 0.6:
                            return BiomeType.RAINFOREST
                        else:
                            return BiomeType.FOREST

            # Zones froides (subpolaires)
            else:
                # Toundra sèche
                if humidity < 0.35:
                    return BiomeType.TUNDRA
                # Toundra humide et taïga
                elif humidity < 0.6:
                    if random.random() < 0.6:
                        return BiomeType.TUNDRA
                    else:
                        return BiomeType.GRASSLAND
                # Forêts boréales
                else:
                    if temperature < 0.25:
                        # Alternance de forêt et toundra
                        if random.random() < 0.7:
                            return BiomeType.FOREST
                        else:
                            return BiomeType.TUNDRA
                    else:
                        return BiomeType.FOREST

    def _initialize_cell_resources(self, cell: 'WorldCell'):
        """Initialise les ressources d'une cellule en fonction de son biome avec un modèle plus réaliste."""
        # Valeurs de base pour tous les biomes
        base_resources = {
            ResourceType.SUNLIGHT: 1.0,
            ResourceType.WATER: 0.5,
            ResourceType.MINERALS: 0.5,
            ResourceType.OXYGEN: 0.8,
            ResourceType.CO2: 0.2,
            ResourceType.ORGANIC_MATTER: 0.1
        }

        # Ajustements spécifiques par biome - valeurs plus réalistes
        biome_modifiers = {
            BiomeType.DEEP_OCEAN: {
                ResourceType.SUNLIGHT: 0.05,  # Très peu de lumière en profondeur
                ResourceType.WATER: 2.5,      # Beaucoup d'eau
                ResourceType.MINERALS: 1.2,   # Riches en minéraux
                ResourceType.OXYGEN: 0.4,     # Peu d'oxygène en profondeur
                ResourceType.CO2: 0.6,        # Plus de CO2 dissous
                ResourceType.ORGANIC_MATTER: 0.3  # Matière organique des sédiments
            },
            BiomeType.OCEAN: {
                ResourceType.SUNLIGHT: 0.2,   # Peu de lumière
                ResourceType.WATER: 2.5,      # Beaucoup d'eau
                ResourceType.MINERALS: 0.9,   # Minéraux dissous
                ResourceType.OXYGEN: 0.6,     # Oxygène dissous
                ResourceType.CO2: 0.4,        # CO2 dissous
                ResourceType.ORGANIC_MATTER: 0.4  # Plancton et autres organismes
            },
            BiomeType.SHALLOW_WATER: {
                ResourceType.SUNLIGHT: 0.7,   # Bonne pénétration de la lumière
                ResourceType.WATER: 2.2,      # Beaucoup d'eau
                ResourceType.MINERALS: 0.8,   # Minéraux du fond
                ResourceType.OXYGEN: 0.9,     # Bonne oxygénation
                ResourceType.CO2: 0.3,        # CO2 modéré
                ResourceType.ORGANIC_MATTER: 0.6  # Vie abondante
            },
            BiomeType.CORAL_REEF: {
                ResourceType.SUNLIGHT: 0.9,   # Excellente luminosité
                ResourceType.WATER: 2.2,      # Beaucoup d'eau
                ResourceType.MINERALS: 1.3,   # Très riches en calcium et autres minéraux
                ResourceType.OXYGEN: 1.1,     # Très bonne oxygénation
                ResourceType.CO2: 0.2,        # Peu de CO2 (consommé par les coraux)
                ResourceType.ORGANIC_MATTER: 1.2  # Très riche en vie
            },
            BiomeType.BEACH: {
                ResourceType.SUNLIGHT: 1.2,   # Exposition maximale
                ResourceType.WATER: 1.2,      # Humidité modérée
                ResourceType.MINERALS: 0.9,   # Sable riche en minéraux
                ResourceType.OXYGEN: 1.0,     # Bonne oxygénation
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.4  # Algues, débris marins
            },
            BiomeType.GRASSLAND: {
                ResourceType.SUNLIGHT: 1.3,   # Exposition maximale
                ResourceType.WATER: 0.7,      # Eau modérée
                ResourceType.MINERALS: 0.8,   # Sols fertiles
                ResourceType.OXYGEN: 1.1,     # Bonne production d'oxygène
                ResourceType.CO2: 0.2,        # Consommé par les plantes
                ResourceType.ORGANIC_MATTER: 0.7  # Herbes et racines
            },
            BiomeType.SAVANNA: {
                ResourceType.SUNLIGHT: 1.4,   # Très forte exposition
                ResourceType.WATER: 0.5,      # Eau limitée
                ResourceType.MINERALS: 0.7,   # Sols moyennement fertiles
                ResourceType.OXYGEN: 1.0,
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.6  # Herbes et arbustes épars
            },
            BiomeType.FOREST: {
                ResourceType.SUNLIGHT: 0.7,   # Ombrage partiel
                ResourceType.WATER: 1.0,      # Bonne rétention d'eau
                ResourceType.MINERALS: 0.9,   # Sols riches
                ResourceType.OXYGEN: 1.4,     # Forte production d'oxygène
                ResourceType.CO2: 0.1,        # Fortement consommé
                ResourceType.ORGANIC_MATTER: 1.2  # Litière forestière abondante
            },
            BiomeType.RAINFOREST: {
                ResourceType.SUNLIGHT: 0.5,   # Canopée dense
                ResourceType.WATER: 1.5,      # Très humide
                ResourceType.MINERALS: 0.7,   # Sols lessivés mais recyclage rapide
                ResourceType.OXYGEN: 1.7,     # Production maximale d'oxygène
                ResourceType.CO2: 0.1,        # Fortement consommé
                ResourceType.ORGANIC_MATTER: 1.5  # Biomasse maximale
            },
            BiomeType.SWAMP: {
                ResourceType.SUNLIGHT: 0.6,   # Partiellement ombragé
                ResourceType.WATER: 1.8,      # Saturé d'eau
                ResourceType.MINERALS: 0.8,   # Sédiments riches
                ResourceType.OXYGEN: 0.6,     # Zones anoxiques
                ResourceType.CO2: 0.5,        # Décomposition anaérobie
                ResourceType.ORGANIC_MATTER: 1.3  # Matière en décomposition
            },
            BiomeType.MOUNTAIN: {
                ResourceType.SUNLIGHT: 1.3,   # Forte exposition en altitude
                ResourceType.WATER: 0.4,      # Eau limitée (ruissellement)
                ResourceType.MINERALS: 1.4,   # Roches exposées
                ResourceType.OXYGEN: 0.8,     # Plus faible en haute altitude
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.3  # Végétation éparse
            },
            BiomeType.MOUNTAIN_FOREST: {
                ResourceType.SUNLIGHT: 0.9,
                ResourceType.WATER: 0.8,      # Brouillards et précipitations
                ResourceType.MINERALS: 1.2,
                ResourceType.OXYGEN: 1.2,
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.8  # Forêts d'altitude
            },
            BiomeType.DESERT: {
                ResourceType.SUNLIGHT: 1.6,   # Exposition maximale
                ResourceType.WATER: 0.1,      # Très sec
                ResourceType.MINERALS: 1.0,   # Sols minéraux
                ResourceType.OXYGEN: 0.9,
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.1  # Très peu de vie
            },
            BiomeType.DESERT_HILLS: {
                ResourceType.SUNLIGHT: 1.5,
                ResourceType.WATER: 0.15,     # Légèrement plus d'eau que le désert plat
                ResourceType.MINERALS: 1.3,   # Plus de roches exposées
                ResourceType.OXYGEN: 0.9,
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.15 # Légèrement plus de vie
            },
            BiomeType.TUNDRA: {
                ResourceType.SUNLIGHT: 0.9,   # Varie selon les saisons
                ResourceType.WATER: 0.5,      # Souvent gelée
                ResourceType.MINERALS: 0.6,   # Sols pauvres
                ResourceType.OXYGEN: 1.0,
                ResourceType.CO2: 0.3,        # Décomposition lente
                ResourceType.ORGANIC_MATTER: 0.4  # Mousses et lichens
            },
            BiomeType.ICE: {
                ResourceType.SUNLIGHT: 1.2,   # Forte réflexion
                ResourceType.WATER: 0.3,      # Eau gelée
                ResourceType.MINERALS: 0.3,   # Très peu accessible
                ResourceType.OXYGEN: 0.9,
                ResourceType.CO2: 0.4,        # Piégé dans la glace
                ResourceType.ORGANIC_MATTER: 0.1  # Presque pas de vie
            },
            BiomeType.VOLCANIC: {
                ResourceType.SUNLIGHT: 0.8,   # Souvent obscurci par les cendres
                ResourceType.WATER: 0.3,      # Sources chaudes
                ResourceType.MINERALS: 1.8,   # Extrêmement riche en minéraux
                ResourceType.OXYGEN: 0.5,     # Consommé par les réactions chimiques
                ResourceType.CO2: 0.8,        # Émissions volcaniques
                ResourceType.ORGANIC_MATTER: 0.2  # Bactéries extrêmophiles
            },
            BiomeType.RIVER: {
                ResourceType.SUNLIGHT: 0.9,
                ResourceType.WATER: 2.0,      # Eau courante
                ResourceType.MINERALS: 0.9,   # Sédiments transportés
                ResourceType.OXYGEN: 1.1,     # Bien oxygénée par le courant
                ResourceType.CO2: 0.2,
                ResourceType.ORGANIC_MATTER: 0.7  # Vie aquatique et débris
            },
            BiomeType.LAKE: {
                ResourceType.SUNLIGHT: 0.8,
                ResourceType.WATER: 2.1,      # Eau stagnante
                ResourceType.MINERALS: 0.7,   # Sédiments lacustres
                ResourceType.OXYGEN: 0.9,     # Varie selon la profondeur
                ResourceType.CO2: 0.3,
                ResourceType.ORGANIC_MATTER: 0.8  # Écosystème lacustre
            }
        }

        # Appliquer les modificateurs spécifiques au biome
        modifiers = biome_modifiers.get(cell.biome_type, {})

        # Initialiser les capacités de ressources
        for resource_type in ResourceType:
            base = base_resources.get(resource_type, 0.5)
            modifier = modifiers.get(resource_type, 1.0)

            # Capacité maximale de la ressource
            capacity = base * modifier

            # Ajouter une variation naturelle (±15%)
            variation = random.uniform(-0.15, 0.15) * capacity
            cell.resource_capacity[resource_type] = max(0.1, capacity + variation)

            # Niveau initial de la ressource - plus réaliste avec des variations
            # Les biomes stables ont des ressources proches de leur capacité
            # Les biomes instables ou extrêmes ont plus de variations
            stability = self._get_biome_stability(cell.biome_type)
            min_percent = 0.5 + (stability * 0.3)  # Entre 50% et 80% selon la stabilité

            cell.resources[resource_type] = cell.resource_capacity[resource_type] * random.uniform(min_percent, 1.0)

    def _get_biome_stability(self, biome_type: BiomeType) -> float:
        """Détermine la stabilité écologique d'un biome (0 = instable, 1 = très stable)."""
        stability_ratings = {
            BiomeType.DEEP_OCEAN: 0.9,      # Très stable
            BiomeType.OCEAN: 0.85,
            BiomeType.SHALLOW_WATER: 0.7,
            BiomeType.CORAL_REEF: 0.6,      # Sensible aux changements
            BiomeType.BEACH: 0.5,           # Changeant avec les marées
            BiomeType.GRASSLAND: 0.7,
            BiomeType.SAVANNA: 0.6,         # Variations saisonnières
            BiomeType.FOREST: 0.8,          # Stable
            BiomeType.RAINFOREST: 0.85,     # Très stable
            BiomeType.SWAMP: 0.6,
            BiomeType.MOUNTAIN: 0.5,        # Conditions difficiles
            BiomeType.MOUNTAIN_FOREST: 0.6,
            BiomeType.DESERT: 0.4,          # Conditions extrêmes
            BiomeType.DESERT_HILLS: 0.4,
            BiomeType.TUNDRA: 0.5,
            BiomeType.ICE: 0.7,             # Stable mais extrême
            BiomeType.VOLCANIC: 0.2,        # Très instable
            BiomeType.RIVER: 0.6,           # Variations saisonnières
            BiomeType.LAKE: 0.7
        }

        return stability_ratings.get(biome_type, 0.6)  # Valeur par défaut

    def _determine_biome(self, altitude: float, humidity: float, temperature: float) -> BiomeType:
        """Méthode de compatibilité pour l'ancienne détermination de biome."""
        return self._determine_advanced_biome(altitude, humidity, temperature, 0.0, 0.35, 0.75, 0.6, 0.3)

    def get_cell_at_position(self, position: Tuple[float, float]) -> Optional[WorldCell]:
        """Récupère la cellule à la position donnée."""
        grid_x = int(position[0] // self.cell_size)
        grid_y = int(position[1] // self.cell_size)

        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.grid[grid_x][grid_y]
        return None

    def get_neighboring_cells(self, cell: WorldCell) -> List[WorldCell]:
        """Récupère les cellules voisines d'une cellule donnée."""
        neighbors = []
        cell_x = cell.position[0] // self.cell_size
        cell_y = cell.position[1] // self.cell_size

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Ignore la cellule elle-même

                nx, ny = cell_x + dx, cell_y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    neighbors.append(self.grid[nx][ny])

        return neighbors

    def add_organism(self, organism: Organism):
        """Ajoute un organisme au monde et met à jour les statistiques d'espèces."""
        # Vérification du nombre maximal d'organismes pour éviter les problèmes de performance
        if len(self.organisms) >= self.max_organisms:
            # Supprimer les organismes les plus faibles si la limite est atteinte
            self._cull_weakest_organisms(1)  # Supprimer au moins un organisme

        # Ajouter l'organisme à la liste principale
        self.organisms.append(organism)

        # Ajouter l'organisme à la grille spatiale pour optimiser les recherches
        self.spatial_grid.add_organism(organism)

        # Mise à jour des statistiques par type d'organisme
        self.species_stats[organism.organism_type] = self.species_stats.get(organism.organism_type, 0) + 1

        # Mise à jour du registre des espèces
        if organism.species_id not in self.species_registry:
            # Nouvelle espèce découverte
            species_name = self._generate_species_name(organism)

            self.species_registry[organism.species_id] = {
                'name': species_name,
                'type': organism.organism_type,
                'count': 1,
                'first_appearance': self.year,
                'last_seen': self.year,
                'max_generation': organism.generation,
                'ancestor_ids': organism.parent_ids,
                'adaptation_score': organism.adaptation_score,
                'is_extinct': False,
                'biome_distribution': {},
                'significant_mutations': organism.mutation_count
            }

            # Si c'est une nouvelle espèce issue de parents (et non générée au départ)
            if organism.parent_ids and organism.generation > 1:
                self.speciation_events += 1

                # Enregistrer cet événement évolutif
                self.evolutionary_milestones.append({
                    'year': self.year,
                    'event_type': 'speciation',
                    'species_id': organism.species_id,
                    'species_name': species_name,
                    'parent_ids': organism.parent_ids,
                    'organism_type': organism.organism_type,
                    'description': f"Nouvelle espèce {species_name} apparue par spéciation"
                })
        else:
            # Espèce existante
            species_data = self.species_registry[organism.species_id]
            species_data['count'] += 1
            species_data['last_seen'] = self.year
            species_data['max_generation'] = max(species_data['max_generation'], organism.generation)

            # Mise à jour du score d'adaptation moyen (optimisé pour éviter les calculs coûteux)
            old_score = species_data['adaptation_score']
            count = species_data['count']
            species_data['adaptation_score'] = old_score + (organism.adaptation_score - old_score) / count

        # Mise à jour de la génération maximale
        if organism.generation > self.max_generation:
            self.max_generation = organism.generation

        # Mise à jour de la distribution par biome
        cell = self.get_cell_at_position(organism.position)
        if cell:
            biome_type = cell.biome_type
            species_data = self.species_registry[organism.species_id]
            species_data['biome_distribution'][biome_type] = species_data['biome_distribution'].get(biome_type, 0) + 1

    def _cull_weakest_organisms(self, count: int = 1):
        """Supprime les organismes les plus faibles pour maintenir les performances."""
        if len(self.organisms) <= count:
            return

        # Trier les organismes par score d'adaptation (du plus faible au plus fort)
        organisms_to_cull = sorted(
            [org for org in self.organisms if org.is_alive],
            key=lambda org: org.adaptation_score
        )[:count]

        # Supprimer les organismes les plus faibles
        for organism in organisms_to_cull:
            self._remove_organism(organism)

    def _remove_organism(self, organism: Organism):
        """Supprime un organisme du monde et met à jour les statistiques."""
        if organism in self.organisms:
            # Retirer de la liste principale
            self.organisms.remove(organism)

            # Retirer de la grille spatiale
            self.spatial_grid.remove_organism(organism)

            # Mettre à jour les statistiques
            if organism.is_alive:  # Ne pas compter les organismes déjà morts
                self.species_stats[organism.organism_type] -= 1

                # Mettre à jour le registre des espèces
                if organism.species_id in self.species_registry:
                    species_data = self.species_registry[organism.species_id]
                    species_data['count'] -= 1

                    # Vérifier si l'espèce est éteinte
                    if species_data['count'] <= 0:
                        species_data['is_extinct'] = True
                        self.extinction_count += 1

    def _generate_species_name(self, organism: Organism) -> str:
        """Génère un nom scientifique pour une nouvelle espèce."""
        # Préfixes basés sur le type d'organisme
        prefixes = {
            OrganismType.UNICELLULAR: ["Micro", "Bacil", "Mono", "Proto", "Cyano"],
            OrganismType.PLANT: ["Chloro", "Phyto", "Floro", "Botan", "Arbor"],
            OrganismType.HERBIVORE: ["Herbi", "Phyto", "Grami", "Rumi", "Pecor"],
            OrganismType.CARNIVORE: ["Carni", "Preda", "Vena", "Ferox", "Raptor"],
            OrganismType.OMNIVORE: ["Omni", "Vari", "Diver", "Panto", "Mixo"]
        }

        # Suffixes basés sur les traits dominants
        suffixes = []

        if organism.phenotype.size < 0.5:
            suffixes.extend(["minus", "parvus", "micro"])
        else:
            suffixes.extend(["magnus", "major", "gigant"])

        if organism.phenotype.max_speed > 7:
            suffixes.extend(["velox", "celer", "rapid"])
        else:
            suffixes.extend(["lentus", "tardus", "grad"])

        if organism.phenotype.strength > 1.5:
            suffixes.extend(["fortis", "robur", "potens"])
        else:
            suffixes.extend(["debil", "fragil", "tenuis"])

        # Génération du nom
        prefix = random.choice(prefixes.get(organism.organism_type, ["Vita"]))
        suffix = random.choice(suffixes)

        # Ajout d'un identifiant numérique pour l'unicité
        species_number = len(self.species_registry) + 1

        return f"{prefix}{suffix} {species_number}"

    def get_nearby_organisms(self, organism: Organism, max_distance: float = None) -> List[Organism]:
        """Récupère les organismes proches d'un organisme donné en utilisant la grille spatiale."""
        if max_distance is None:
            max_distance = organism.phenotype.vision_range

        # Utiliser la grille spatiale pour une recherche efficace
        nearby = self.spatial_grid.get_nearby_organisms(organism.position, max_distance)

        # Filtrer l'organisme lui-même
        return [other for other in nearby if other.id != organism.id]

    def _update_environmental_cycles(self, delta_time: float):
        """Met à jour tous les cycles environnementaux (jour/nuit, saisons, météo)."""
        # Mise à jour du cycle jour/nuit
        previous_day_cycle = self.day_night_cycle
        self.day_night_cycle = (self.day_night_cycle + delta_time / DAY_LENGTH) % 1.0

        # Calculer l'heure de la journée (0-24h)
        self.time_of_day = self.day_night_cycle * 24.0

        # Détecter le changement de jour
        if previous_day_cycle > self.day_night_cycle:
            self.day += 1
            # Enregistrer des statistiques quotidiennes
            self._record_daily_statistics()

        # Mise à jour du cycle annuel
        previous_year_cycle = self.year_cycle
        self.year_cycle = (self.year_cycle + delta_time / YEAR_LENGTH) % 1.0

        # Détecter le changement d'année
        if previous_year_cycle > self.year_cycle:
            self.year += 1
            # Enregistrer des statistiques annuelles
            self._record_annual_statistics()

        # Déterminer la saison actuelle
        previous_season = self.season
        self.season = int(self.year_cycle * SEASONS_COUNT) % SEASONS_COUNT

        # Détecter le changement de saison
        if previous_season != self.season:
            self._handle_season_change()

        # Mise à jour des conditions météorologiques
        self._update_weather(delta_time)

        # Mise à jour des catastrophes naturelles
        self._update_natural_disasters(delta_time)

        # Mise à jour de la température globale
        self._update_global_temperature()

    def _update_weather(self, delta_time: float):
        """Met à jour les conditions météorologiques en fonction de la saison et d'autres facteurs."""
        # Facteurs de base pour chaque saison
        season_factors = {
            0: {"precipitation": 0.4, "cloud_cover": 0.3, "wind_speed": 0.3},  # Printemps
            1: {"precipitation": 0.2, "cloud_cover": 0.2, "wind_speed": 0.2},  # Été
            2: {"precipitation": 0.5, "cloud_cover": 0.4, "wind_speed": 0.4},  # Automne
            3: {"precipitation": 0.6, "cloud_cover": 0.5, "wind_speed": 0.5}   # Hiver
        }

        # Récupérer les facteurs de la saison actuelle
        current_factors = season_factors[self.season]

        # Ajouter de l'aléatoire pour des variations quotidiennes
        daily_random = math.sin(self.day * 0.1) * 0.2

        # Calculer les nouvelles conditions météorologiques avec inertie
        inertia = 0.95  # Les conditions changent lentement

        for condition in ["precipitation", "cloud_cover", "wind_speed"]:
            base_value = current_factors[condition]
            random_factor = random.uniform(-0.1, 0.1) + daily_random
            target_value = max(0.0, min(1.0, base_value + random_factor))

            # Appliquer l'inertie pour des changements progressifs
            self.weather_conditions[condition] = (
                self.weather_conditions[condition] * inertia +
                target_value * (1 - inertia)
            )

        # Mise à jour de la direction du vent
        wind_change = random.uniform(-0.1, 0.1) * delta_time
        self.weather_conditions["wind_direction"] = (
            self.weather_conditions["wind_direction"] + wind_change
        ) % (2 * math.pi)

        # Possibilité d'événements météorologiques extrêmes
        self._check_for_extreme_weather()

    def _check_for_extreme_weather(self):
        """Vérifie si des événements météorologiques extrêmes se produisent."""
        # Probabilité de base d'événements extrêmes
        extreme_probability = 0.0001  # Très rare

        # Augmenter la probabilité en fonction de la saison
        if self.season == 1:  # Été
            extreme_probability *= 2  # Plus de chances d'orages et canicules
        elif self.season == 3:  # Hiver
            extreme_probability *= 2  # Plus de chances de blizzards

        # Vérifier si un événement extrême se produit
        if random.random() < extreme_probability:
            event_types = ["hurricane", "tornado", "drought", "flood", "blizzard", "heatwave"]
            weights = [0.1, 0.1, 0.2, 0.2, 0.2, 0.2]

            # Ajuster les poids selon la saison
            if self.season == 0:  # Printemps
                weights = [0.1, 0.3, 0.1, 0.3, 0.0, 0.2]
            elif self.season == 1:  # Été
                weights = [0.2, 0.2, 0.3, 0.1, 0.0, 0.2]
            elif self.season == 2:  # Automne
                weights = [0.3, 0.2, 0.1, 0.3, 0.0, 0.1]
            elif self.season == 3:  # Hiver
                weights = [0.0, 0.0, 0.0, 0.2, 0.7, 0.1]

            event_type = random.choices(event_types, weights=weights)[0]
            duration = random.uniform(1, 5) * DAY_LENGTH  # 1-5 jours

            # Ajouter l'événement à la liste des catastrophes naturelles
            self.natural_disasters.append({
                "type": event_type,
                "start_time": self.day * DAY_LENGTH + self.day_night_cycle * DAY_LENGTH,
                "duration": duration,
                "intensity": random.uniform(0.5, 1.0),
                "affected_area": self._generate_disaster_area()
            })

            # Enregistrer l'événement dans les jalons évolutifs
            self.evolutionary_milestones.append({
                'year': self.year,
                'day': self.day,
                'event_type': 'natural_disaster',
                'disaster_type': event_type,
                'description': f"Catastrophe naturelle: {event_type}"
            })

    def _generate_disaster_area(self):
        """Génère une zone affectée par une catastrophe naturelle."""
        # Centre de la catastrophe
        center_x = random.uniform(0, self.width)
        center_y = random.uniform(0, self.height)

        # Rayon de la catastrophe (10-30% de la taille du monde)
        radius = random.uniform(0.1, 0.3) * min(self.width, self.height)

        return {
            "center": (center_x, center_y),
            "radius": radius
        }

    def _update_natural_disasters(self, delta_time: float):
        """Met à jour les catastrophes naturelles actives."""
        current_time = self.day * DAY_LENGTH + self.day_night_cycle * DAY_LENGTH

        # Mettre à jour la liste des catastrophes actives
        active_disasters = []
        for disaster in self.natural_disasters:
            end_time = disaster["start_time"] + disaster["duration"]

            if current_time <= end_time:
                active_disasters.append(disaster)

        self.natural_disasters = active_disasters

    def _apply_weather_effects(self, delta_time: float, active_cells: set):
        """Applique les effets des conditions météorologiques et des catastrophes naturelles."""
        # Appliquer les effets des catastrophes naturelles
        for disaster in self.natural_disasters:
            center = disaster["affected_area"]["center"]
            radius = disaster["affected_area"]["radius"]
            intensity = disaster["intensity"]
            disaster_type = disaster["type"]

            # Ajouter les cellules affectées à la liste des cellules actives
            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    cell_pos = (x * self.cell_size + self.cell_size/2,
                               y * self.cell_size + self.cell_size/2)

                    # Calculer la distance au centre de la catastrophe
                    distance = math.sqrt((cell_pos[0] - center[0])**2 + (cell_pos[1] - center[1])**2)

                    if distance <= radius:
                        active_cells.add((x, y))

                        # Appliquer les effets spécifiques à chaque type de catastrophe
                        if disaster_type == "hurricane" or disaster_type == "tornado":
                            # Augmenter les précipitations et le vent
                            if (x, y) in active_cells and self.grid[x][y]:
                                cell = self.grid[x][y]
                                cell.humidity = min(100, cell.humidity + intensity * delta_time * 20)
                                # Réduire les ressources
                                for resource_type in ResourceType:
                                    cell.resources[resource_type] *= max(0.5, 1.0 - intensity * 0.5)

                        elif disaster_type == "drought":
                            # Réduire l'humidité et l'eau
                            if (x, y) in active_cells and self.grid[x][y]:
                                cell = self.grid[x][y]
                                cell.humidity = max(0, cell.humidity - intensity * delta_time * 10)
                                cell.resources[ResourceType.WATER] *= max(0.1, 1.0 - intensity * 0.3)

                        elif disaster_type == "flood":
                            # Augmenter l'eau, réduire les autres ressources
                            if (x, y) in active_cells and self.grid[x][y]:
                                cell = self.grid[x][y]
                                cell.humidity = 100
                                cell.resources[ResourceType.WATER] = cell.resource_capacity[ResourceType.WATER]
                                cell.resources[ResourceType.ORGANIC_MATTER] *= max(0.3, 1.0 - intensity * 0.2)

                        elif disaster_type == "blizzard":
                            # Réduire la température et la lumière
                            if (x, y) in active_cells and self.grid[x][y]:
                                cell = self.grid[x][y]
                                cell.temperature -= intensity * 10
                                cell.resources[ResourceType.SUNLIGHT] *= max(0.2, 1.0 - intensity * 0.8)

                        elif disaster_type == "heatwave":
                            # Augmenter la température, réduire l'eau
                            if (x, y) in active_cells and self.grid[x][y]:
                                cell = self.grid[x][y]
                                cell.temperature += intensity * 15
                                cell.resources[ResourceType.WATER] *= max(0.3, 1.0 - intensity * 0.5)
                                cell.humidity = max(0, cell.humidity - intensity * delta_time * 5)

    def _get_seasonal_sunlight_modifier(self):
        """Calcule le modificateur de lumière du soleil en fonction de la saison avec des effets plus prononcés."""
        # Valeurs de base pour chaque saison - Amplifiées pour un impact plus visible
        season_modifiers = [1.1, 1.4, 0.8, 0.5]  # Printemps, Été, Automne, Hiver

        # Transition douce entre les saisons avec une courbe sinusoïdale pour plus de naturel
        season_progress = self.year_cycle * SEASONS_COUNT - self.season
        next_season = (self.season + 1) % SEASONS_COUNT

        # Utiliser une fonction sinusoïdale pour une transition plus naturelle
        blend_factor = (1 - math.cos(season_progress * math.pi)) / 2

        # Interpolation entre les saisons
        return season_modifiers[self.season] * (1 - blend_factor) + season_modifiers[next_season] * blend_factor

    def _get_seasonal_temperature_modifier(self):
        """Calcule le modificateur de température en fonction de la saison."""
        # Modificateurs de température pour chaque saison (en degrés Celsius)
        temp_modifiers = [5.0, 15.0, 5.0, -10.0]  # Printemps, Été, Automne, Hiver

        # Transition douce entre les saisons
        season_progress = self.year_cycle * SEASONS_COUNT - self.season
        next_season = (self.season + 1) % SEASONS_COUNT

        # Utiliser une fonction sinusoïdale pour une transition plus naturelle
        blend_factor = (1 - math.cos(season_progress * math.pi)) / 2

        # Interpolation entre les saisons
        return temp_modifiers[self.season] * (1 - blend_factor) + temp_modifiers[next_season] * blend_factor

    def _get_day_night_temperature_modifier(self):
        """Calcule le modificateur de température en fonction du cycle jour/nuit."""
        # Le cycle jour/nuit est entre 0 et 1
        day_progress = self.day_cycle % 1.0

        # Température plus basse la nuit, plus haute le jour
        if day_progress < 0.25:  # Aube - température qui monte
            return -5.0 + day_progress * 20.0
        elif day_progress < 0.5:  # Jour - température stable ou qui monte légèrement
            return 0.0 + (day_progress - 0.25) * 4.0
        elif day_progress < 0.75:  # Crépuscule - température qui baisse
            return 1.0 - (day_progress - 0.5) * 12.0
        else:  # Nuit - température basse
            return -5.0

    def _get_seasonal_precipitation_modifier(self):
        """Calcule le modificateur de précipitations en fonction de la saison."""
        # Modificateurs de précipitations pour chaque saison
        precip_modifiers = [1.5, 0.7, 1.2, 1.0]  # Printemps (plus humide), Été (sec), Automne, Hiver

        # Transition douce entre les saisons
        season_progress = self.year_cycle * SEASONS_COUNT - self.season
        next_season = (self.season + 1) % SEASONS_COUNT

        # Utiliser une fonction sinusoïdale pour une transition plus naturelle
        blend_factor = (1 - math.cos(season_progress * math.pi)) / 2

        # Interpolation entre les saisons
        return precip_modifiers[self.season] * (1 - blend_factor) + precip_modifiers[next_season] * blend_factor

    def _calculate_cell_temperature(self, cell: WorldCell, sunlight_factor: float):
        """Calcule la température d'une cellule en fonction de divers facteurs."""
        # Température de base de la cellule
        base_temp = cell.temperature

        # Modificateur saisonnier
        season_temp_modifiers = [5, 15, 0, -10]  # Modificateurs pour chaque saison
        season_mod = season_temp_modifiers[self.season]

        # Variation jour/nuit (plus chaud le jour, plus froid la nuit)
        day_night_variation = 10 * (sunlight_factor - 0.5)

        # Effet de l'altitude (plus froid en altitude)
        altitude_effect = -15 * max(0, cell.altitude)

        # Effet des conditions météorologiques
        weather_effect = -5 * self.weather_conditions["cloud_cover"]  # Nuages = plus froid

        # Effet des catastrophes naturelles
        disaster_effect = 0
        for disaster in self.natural_disasters:
            center = disaster["affected_area"]["center"]
            radius = disaster["affected_area"]["radius"]
            intensity = disaster["intensity"]

            # Calculer la distance au centre de la catastrophe
            distance = math.sqrt((cell.position[0] - center[0])**2 + (cell.position[1] - center[1])**2)

            if distance <= radius:
                if disaster["type"] == "heatwave":
                    disaster_effect += 20 * intensity
                elif disaster["type"] == "blizzard":
                    disaster_effect -= 20 * intensity

        # Calculer la température finale
        final_temp = base_temp + season_mod + day_night_variation + altitude_effect + weather_effect + disaster_effect

        # Limiter à des valeurs réalistes
        return max(-30, min(50, final_temp))

    def _handle_season_change(self):
        """Gère les changements qui se produisent lors d'un changement de saison."""
        season_names = ["printemps", "été", "automne", "hiver"]
        print(f"Changement de saison: {season_names[self.season]}")

        # Enregistrer le changement de saison dans les jalons évolutifs
        self.evolutionary_milestones.append({
            'year': self.year,
            'day': self.day,
            'event_type': 'season_change',
            'season': season_names[self.season],
            'description': f"Changement de saison: {season_names[self.season]}"
        })

        # Ajuster les ressources globales en fonction de la saison
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                cell = self.grid[x][y]
                if cell:
                    # Printemps: croissance des plantes
                    if self.season == 0:
                        cell.resources[ResourceType.ORGANIC_MATTER] *= 1.2
                        cell.resources[ResourceType.WATER] *= 1.1

                    # Été: plus de lumière, moins d'eau
                    elif self.season == 1:
                        cell.resources[ResourceType.SUNLIGHT] *= 1.2
                        cell.resources[ResourceType.WATER] *= 0.9

                    # Automne: moins de lumière, plus de matière organique (feuilles mortes)
                    elif self.season == 2:
                        cell.resources[ResourceType.SUNLIGHT] *= 0.9
                        cell.resources[ResourceType.ORGANIC_MATTER] *= 1.1

                    # Hiver: moins de lumière et de ressources
                    elif self.season == 3:
                        cell.resources[ResourceType.SUNLIGHT] *= 0.7
                        cell.resources[ResourceType.ORGANIC_MATTER] *= 0.8
                        cell.resources[ResourceType.WATER] *= 0.9

    def _update_global_temperature(self):
        """Met à jour la température globale en fonction des cycles climatiques."""
        # Cycle climatique à long terme (changements sur plusieurs années)
        self.climate_cycle = (self.climate_cycle + 0.0001) % 1.0

        # Variation sinusoïdale de la température globale
        climate_variation = math.sin(self.climate_cycle * 2 * math.pi) * 3.0

        # Variation saisonnière
        season_variation = math.sin(self.year_cycle * 2 * math.pi) * 10.0

        # Température globale de base
        base_temperature = 15.0

        # Calculer la température globale
        self.global_temperature = base_temperature + climate_variation + season_variation

    def _record_daily_statistics(self):
        """Enregistre les statistiques quotidiennes."""
        # Compter les organismes par type
        type_counts = {org_type: 0 for org_type in OrganismType}
        for organism in self.organisms:
            if organism.is_alive:
                type_counts[organism.organism_type] += 1

        # Enregistrer les données
        daily_data = {
            'day': self.day,
            'year': self.year,
            'organism_counts': type_counts,
            'temperature': self.global_temperature,
            'weather': self.weather_conditions.copy(),
            'active_disasters': len(self.natural_disasters)
        }

        # Ajouter aux données historiques (limiter la taille pour éviter les problèmes de mémoire)
        self.historical_data.append(daily_data)
        if len(self.historical_data) > 365:  # Garder un an de données
            self.historical_data.pop(0)

    def _record_annual_statistics(self):
        """Enregistre les statistiques annuelles et génère un rapport."""
        # Compter les espèces par type
        species_by_type = {org_type: set() for org_type in OrganismType}
        for organism in self.organisms:
            if organism.is_alive:
                species_by_type[organism.organism_type].add(organism.species_id)

        species_counts = {org_type: len(species) for org_type, species in species_by_type.items()}

        # Calculer les espèces dominantes
        self._calculate_dominant_species()

        # Enregistrer les données annuelles
        annual_data = {
            'year': self.year,
            'species_counts': species_counts,
            'organism_counts': self.species_stats.copy(),
            'extinctions': self.extinction_count,
            'speciations': self.speciation_events,
            'max_generation': self.max_generation,
            'dominant_species': {k: v['name'] if v else "None" for k, v in self.dominant_species.items()}
        }

        # Afficher un rapport annuel
        print(f"\n=== RAPPORT ANNUEL - ANNÉE {self.year} ===")
        print(f"Nombre total d'organismes: {sum(self.species_stats.values())}")
        print(f"Nombre d'espèces: {sum(species_counts.values())}")
        print(f"Extinctions: {self.extinction_count}")
        print(f"Événements de spéciation: {self.speciation_events}")
        print(f"Génération maximale: {self.max_generation}")
        print("Espèces dominantes:")
        for org_type in OrganismType:
            dominant = self.dominant_species.get(org_type)
            if dominant:
                print(f"  {org_type.name}: {dominant['name']} (score: {dominant['score']:.2f})")
            else:
                print(f"  {org_type.name}: Aucune")
        print("===============================\n")

    def _calculate_dominant_species(self):
        """Calcule les espèces dominantes pour chaque type d'organisme."""
        # Réinitialiser les espèces dominantes
        self.dominant_species = {org_type: None for org_type in OrganismType}

        # Regrouper les organismes par espèce et type
        species_data = {}
        for organism in self.organisms:
            if not organism.is_alive:
                continue

            if organism.species_id not in species_data:
                species_data[organism.species_id] = {
                    'type': organism.organism_type,
                    'count': 0,
                    'total_score': 0,
                    'name': organism.scientific_name if hasattr(organism, 'scientific_name') else "Unknown"
                }

            species_data[organism.species_id]['count'] += 1
            if hasattr(organism, '_calculate_species_dominance'):
                species_data[organism.species_id]['total_score'] += organism._calculate_species_dominance()
            else:
                # Fallback si la méthode n'existe pas
                species_data[organism.species_id]['total_score'] += 0.5

        # Calculer le score moyen pour chaque espèce
        for species_id, data in species_data.items():
            if data['count'] > 0:
                data['avg_score'] = data['total_score'] / data['count']
            else:
                data['avg_score'] = 0

        # Trouver l'espèce dominante pour chaque type
        for species_id, data in species_data.items():
            org_type = data['type']
            current_dominant = self.dominant_species[org_type]

            # Une espèce est dominante si elle a un score plus élevé et au moins 3 individus
            if data['count'] >= 3 and (current_dominant is None or data['avg_score'] > current_dominant['score']):
                self.dominant_species[org_type] = {
                    'id': species_id,
                    'name': data['name'],
                    'count': data['count'],
                    'score': data['avg_score']
                }

    def update(self, delta_time: float):
        """Met à jour l'état du monde et de tous ses composants avec optimisation des performances."""
        # Mise à jour du cycle jour/nuit
        previous_day_cycle = self.day_night_cycle
        self.day_night_cycle = (self.day_night_cycle + delta_time / DAY_LENGTH) % 1.0

        # Calculer l'heure de la journée (0-24h)
        self.time_of_day = self.day_night_cycle * 24.0

        # Détecter le changement de jour
        if previous_day_cycle > self.day_night_cycle:
            self.day += 1

        # Mise à jour du cycle annuel
        previous_year_cycle = self.year_cycle
        self.year_cycle = (self.year_cycle + delta_time / YEAR_LENGTH) % 1.0

        # Détecter le changement d'année
        if previous_year_cycle > self.year_cycle:
            self.year += 1

        # Déterminer la saison actuelle
        previous_season = self.season
        self.season = int(self.year_cycle * SEASONS_COUNT) % SEASONS_COUNT

        # Facteur de lumière basé sur le cycle jour/nuit
        sunlight_factor = math.sin(self.day_night_cycle * 2 * math.pi) * 0.5 + 0.5

        # Facteur saisonnier basé sur la position dans l'année
        seasonal_factor = math.sin(self.year_cycle * 2 * math.pi) * 0.5 + 0.5

        # Déterminer le niveau de détail (LOD) en fonction du nombre d'organismes
        organism_count = len(self.organisms)
        update_ratio = 1.0  # Par défaut, mettre à jour tous les organismes

        # Ajuster le ratio de mise à jour en fonction du nombre d'organismes
        for threshold, ratio in sorted(self.lod_thresholds.items()):
            if organism_count > threshold:
                update_ratio = ratio

        # Incrémenter le compteur de mise à jour
        self.update_counter += 1

        # Mise à jour des cellules - optimisé pour ne mettre à jour que les cellules actives
        # Utiliser un ensemble pour éviter les doublons
        active_cells = set()

        # Reconstruire la grille spatiale périodiquement pour éviter les erreurs d'accumulation
        if self.update_counter % 100 == 0:
            self._rebuild_spatial_grid()

        # Appliquer les effets des conditions météorologiques et des catastrophes naturelles
        self._apply_weather_effects(delta_time, active_cells)

        # Ajouter les cellules contenant des organismes et leurs voisines
        # Optimisation: limiter le nombre de cellules à vérifier
        max_cells_to_check = min(1000, len(self.organisms) * 3)
        cells_checked = 0

        for organism in self.organisms:
            if not organism.is_alive or cells_checked >= max_cells_to_check:
                continue

            cell_x = int(organism.position[0] // self.cell_size)
            cell_y = int(organism.position[1] // self.cell_size)

            # Ajouter la cellule et ses voisines immédiates
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = cell_x + dx, cell_y + dy
                    if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                        active_cells.add((nx, ny))
                        cells_checked += 1

        # Mettre à jour uniquement les cellules actives
        for x, y in active_cells:
            cell = self.grid[x][y]

            # Ajustement de la lumière du soleil selon le cycle jour/nuit et la saison
            base_sunlight = cell.resource_capacity[ResourceType.SUNLIGHT]
            seasonal_sunlight_modifier = self._get_seasonal_sunlight_modifier()
            weather_sunlight_modifier = 1.0 - (self.weather_conditions["cloud_cover"] * 0.7)

            # Calculer la lumière du soleil finale
            final_sunlight = base_sunlight * sunlight_factor * seasonal_sunlight_modifier * weather_sunlight_modifier
            cell.resources[ResourceType.SUNLIGHT] = final_sunlight

            # Ajustement de la température selon la saison et l'heure du jour
            cell.temperature = self._calculate_cell_temperature(cell, sunlight_factor)

            # Ajustement de l'humidité selon les précipitations
            cell.humidity = min(100, cell.humidity + self.weather_conditions["precipitation"] * delta_time * 10)

            # Mise à jour des ressources de la cellule
            neighbors = self.get_neighboring_cells(cell)
            cell.update(delta_time, neighbors)

        # Mise à jour des organismes avec niveau de détail (LOD) - Optimisé
        # Éviter la copie complète de la liste pour économiser de la mémoire
        organisms_to_update = []

        # Si le ratio est inférieur à 1, ne mettre à jour qu'une partie des organismes
        if update_ratio < 1.0:
            # Sélectionner aléatoirement des organismes sans copier toute la liste
            update_count = int(organism_count * update_ratio)
            # Utiliser un échantillonnage aléatoire plus efficace
            if update_count > 0:
                indices = set(random.sample(range(organism_count), update_count))
                organisms_to_update = [org for i, org in enumerate(self.organisms) if i in indices]
        else:
            # Utiliser directement la liste originale sans copie
            organisms_to_update = self.organisms

        # Compteur pour limiter les nouvelles reproductions - Optimisé
        # Calculer une fois et stocker pour éviter les calculs répétés
        if organism_count > 0:
            # Ajuster la formule pour être plus efficace avec de grandes populations
            reproduction_limit = max(10, min(100, int(2000 / (organism_count ** 0.7))))
        else:
            reproduction_limit = 100  # Valeur par défaut si aucun organisme
        reproduction_count = 0

        # Mettre à jour la grille spatiale moins fréquemment pour les grandes populations
        if self.update_counter % max(1, min(10, int(organism_count / 500))) == 0:
            self._rebuild_spatial_grid()

        for organism in organisms_to_update:
            if not organism.is_alive:
                # Gestion de la décomposition des organismes morts
                if random.random() < delta_time * 0.1:  # Décomposition progressive
                    cell = self.get_cell_at_position(organism.position)
                    if cell:
                        biomass = organism.phenotype.size * 10
                        cell.add_decomposition(biomass)

                    # Retrait de l'organisme
                    self._remove_organism(organism)
                continue

            # Mise à jour de la position dans la grille spatiale
            self.spatial_grid.update_organism_position(organism)

            # Récupère les organismes proches pour les interactions (optimisé)
            nearby_organisms = self.get_nearby_organisms(organism)

            # Décision et action
            organism.decide_action(self, nearby_organisms)

            # Mise à jour de l'état physiologique
            organism.update(self, delta_time)

            # Appliquer la pression de sélection naturelle
            self._apply_selection_pressure(organism, delta_time)

            # Limiter les reproductions quand il y a beaucoup d'organismes
            # Augmentation de la limite de reproduction pour favoriser la stabilité
            if reproduction_count < reproduction_limit:
                # Vérification de la reproduction asexuée pour les unicellulaires et les plantes
                if organism.ready_to_mate:
                    # Facteur d'équilibre écologique - favorise les espèces sous-représentées
                    type_count = sum(1 for org in self.organisms if org.is_alive and org.organism_type == organism.organism_type)
                    total_count = sum(1 for org in self.organisms if org.is_alive)

                    # Calculer le ratio idéal pour chaque type d'organisme
                    ideal_ratios = {
                        OrganismType.UNICELLULAR: 0.25,
                        OrganismType.PLANT: 0.35,
                        OrganismType.HERBIVORE: 0.25,
                        OrganismType.CARNIVORE: 0.10,
                        OrganismType.OMNIVORE: 0.05
                    }

                    # Calculer le ratio actuel
                    current_ratio = type_count / max(1, total_count)
                    ideal_ratio = ideal_ratios.get(organism.organism_type, 0.2)

                    # Bonus de reproduction si l'espèce est sous-représentée
                    balance_factor = max(0.5, min(2.0, ideal_ratio / max(0.01, current_ratio)))

                    # Reproduction asexuée pour les unicellulaires
                    if organism.organism_type == OrganismType.UNICELLULAR:
                        # Éviter la division par zéro si max_organisms est 0
                        reproduction_chance = delta_time * 0.15 * balance_factor  # Augmenté de 0.1 à 0.15
                        if self.max_organisms > 0:
                            # Formule adoucie pour permettre plus de reproductions
                            reproduction_chance *= max(0.2, 1.0 - (organism_count / self.max_organisms) * 0.8)

                        if random.random() < reproduction_chance:
                            offspring = organism.try_reproduce(None)
                            if offspring:
                                self.add_organism(offspring)
                                reproduction_count += 1

                    # Auto-pollinisation pour les plantes (si aucun partenaire n'est trouvé)
                    elif organism.organism_type == OrganismType.PLANT:
                        # Vérifier si des partenaires potentiels sont à proximité (optimisé)
                        plant_mates = [other for other in nearby_organisms
                                      if other.organism_type == OrganismType.PLANT and other.ready_to_mate]

                        has_potential_mates = any(
                            math.sqrt((organism.position[0] - other.position[0])**2 +
                                     (organism.position[1] - other.position[1])**2) < 15  # Distance augmentée de 10 à 15
                            for other in plant_mates
                        )

                        # Si pas de partenaires potentiels, chance d'auto-pollinisation
                        reproduction_chance = delta_time * 0.08 * balance_factor  # Augmenté de 0.05 à 0.08
                        if self.max_organisms > 0:
                            # Formule adoucie pour permettre plus de reproductions
                            reproduction_chance *= max(0.2, 1.0 - (organism_count / self.max_organisms) * 0.8)

                        if not has_potential_mates and random.random() < reproduction_chance:
                            offspring = organism.try_reproduce(None)
                            if offspring:
                                self.add_organism(offspring)
                                reproduction_count += 1

                # Vérification des interactions entre organismes (optimisé)
                for other in nearby_organisms:
                    if not other.is_alive:
                        continue

                    # Calcul de distance optimisé (utiliser la distance au carré pour éviter la racine carrée)
                    dx = organism.position[0] - other.position[0]
                    dy = organism.position[1] - other.position[1]
                    dist_squared = dx*dx + dy*dy

                    # Reproduction sexuée si les deux sont prêts et compatibles
                    if (dist_squared < 36 and  # 6^2 - Distance augmentée pour faciliter la reproduction
                        organism.ready_to_mate and
                        other.ready_to_mate and
                        organism.organism_type == other.organism_type and
                        reproduction_count < reproduction_limit):

                        # Appliquer le facteur d'équilibre écologique
                        type_count = sum(1 for org in self.organisms if org.is_alive and org.organism_type == organism.organism_type)
                        total_count = sum(1 for org in self.organisms if org.is_alive)

                        # Calculer le ratio idéal pour chaque type d'organisme
                        ideal_ratios = {
                            OrganismType.UNICELLULAR: 0.25,
                            OrganismType.PLANT: 0.35,
                            OrganismType.HERBIVORE: 0.25,
                            OrganismType.CARNIVORE: 0.10,
                            OrganismType.OMNIVORE: 0.05
                        }

                        # Calculer le ratio actuel
                        current_ratio = type_count / max(1, total_count)
                        ideal_ratio = ideal_ratios.get(organism.organism_type, 0.2)

                        # Bonus de reproduction si l'espèce est sous-représentée
                        balance_factor = max(0.5, min(2.0, ideal_ratio / max(0.01, current_ratio)))

                        # Augmenter les chances de reproduction pour les espèces sous-représentées
                        if random.random() < balance_factor * 0.8:
                            offspring = organism.try_reproduce(other)
                            if offspring:
                                self.add_organism(offspring)
                                reproduction_count += 1

                    # Prédation (carnivores et omnivores) - avec équilibre écologique
                    elif (dist_squared < 4 and  # 2^2
                          (organism.organism_type == OrganismType.CARNIVORE or
                           organism.organism_type == OrganismType.OMNIVORE) and
                          (other.organism_type == OrganismType.HERBIVORE or
                           other.organism_type == OrganismType.UNICELLULAR or
                           (organism.organism_type == OrganismType.OMNIVORE and
                            other.organism_type == OrganismType.PLANT))):

                        # Vérifier l'équilibre proie-prédateur (optimisé)
                        # Utiliser les statistiques globales au lieu de recalculer à chaque fois
                        if self.update_counter % 10 == 0:  # Mettre à jour les ratios seulement périodiquement
                            # Mettre à jour les ratios globaux si nécessaire
                            if not hasattr(self, 'predator_prey_ratios'):
                                self.predator_prey_ratios = {}

                            prey_type = other.organism_type
                            predator_type = organism.organism_type
                            ratio_key = (predator_type, prey_type)

                            # Calculer le ratio seulement si nécessaire (toutes les 10 mises à jour)
                            if ratio_key not in self.predator_prey_ratios or self.update_counter % 100 == 0:
                                prey_count = sum(1 for org in self.organisms if org.is_alive and org.organism_type == prey_type)
                                predator_count = sum(1 for org in self.organisms if org.is_alive and org.organism_type == predator_type)
                                ideal_ratio = 4.0
                                current_ratio = prey_count / max(1, predator_count)
                                predation_factor = min(1.0, current_ratio / ideal_ratio)
                                self.predator_prey_ratios[ratio_key] = (current_ratio, predation_factor)

                        # Récupérer les valeurs calculées précédemment
                        ratio_key = (organism.organism_type, other.organism_type)
                        current_ratio, predation_factor = self.predator_prey_ratios.get(ratio_key, (4.0, 1.0))

                        # Attaque si le prédateur est plus fort et si l'équilibre écologique le permet
                        is_stronger = organism.phenotype.strength > other.phenotype.strength * 0.8 or other.health < 50
                        is_hungry = organism.energy < organism.phenotype.energy_capacity * 0.2
                        ecological_balance = random.random() < predation_factor * 0.8

                        if is_stronger and (ecological_balance or is_hungry):
                            # Attaquer la proie
                            organism._attack(other)

                            # Bonus de santé pour les proies si elles sont rares (seulement si nécessaire)
                            if current_ratio < 2.0 and not is_hungry and self.update_counter % 5 == 0:
                                # Limiter le nombre de proies à vérifier pour améliorer les performances
                                prey_boost_count = 0
                                for potential_prey in nearby_organisms:
                                    if prey_boost_count >= 3:  # Limiter à 3 proies maximum
                                        break
                                    if potential_prey.is_alive and potential_prey.organism_type == other.organism_type:
                                        potential_prey.health = min(100, potential_prey.health + 5)
                                        prey_boost_count += 1

        # Collecte des statistiques (moins fréquemment si beaucoup d'organismes)
        stats_interval = 1
        if organism_count > 0:
            stats_interval = max(1, int(organism_count / 1000))

        if self.update_counter % stats_interval == 0:
            self._collect_statistics()

        # Avancement du temps
        self.climate_cycle += delta_time / 3600  # Cycle climatique plus lent
        if self.climate_cycle >= 1.0:
            self.climate_cycle = 0.0
            self.year += 1

    def _rebuild_spatial_grid(self):
        """Reconstruit complètement la grille spatiale pour éviter les erreurs d'accumulation.
        Version optimisée pour de meilleures performances."""
        # Utiliser une approche plus efficace pour reconstruire la grille
        self.spatial_grid.clear()

        # Traiter les organismes par lots pour améliorer les performances
        batch_size = 100
        for i in range(0, len(self.organisms), batch_size):
            batch = self.organisms[i:i+batch_size]
            for organism in batch:
                if organism.is_alive:
                    self.spatial_grid.add_organism(organism)

    def _collect_statistics(self):
        """Collecte des statistiques sur l'écosystème. Version optimisée."""
        # Initialiser les compteurs
        stats = {org_type: 0 for org_type in OrganismType}

        # Compter les organismes en une seule passe
        for organism in self.organisms:
            if organism.is_alive:
                stats[organism.organism_type] += 1

        # Mettre à jour les statistiques
        self.species_stats = stats

        # Mise à jour des statistiques évolutives (moins fréquemment)
        if self.update_counter % 10 == 0:
            self._update_evolutionary_statistics()

        # Enregistrement des données historiques (beaucoup moins fréquemment)
        # Réduire la fréquence d'enregistrement pour améliorer les performances
        if len(self.historical_data) == 0 or (len(self.historical_data) < 100 and random.random() < 0.005) or random.random() < 0.001:
            self.historical_data.append({
                'time': len(self.historical_data),
                'stats': stats.copy(),
                'year': self.year,
                'max_generation': self.max_generation,
                'extinct_species': self.extinction_count,
                'speciation_events': self.speciation_events
            })

            # Limiter la taille des données historiques pour économiser la mémoire
            if len(self.historical_data) > 1000:
                # Conserver seulement un échantillon des données anciennes
                new_history = self.historical_data[-500:]  # Garder les 500 plus récentes
                # Ajouter quelques points de données plus anciens pour les tendances à long terme
                sample_indices = sorted(random.sample(range(len(self.historical_data) - 500), 100))
                for idx in sample_indices:
                    new_history.append(self.historical_data[idx])
                self.historical_data = sorted(new_history, key=lambda x: x['time'])

    def _update_evolutionary_statistics(self):
        """Met à jour les statistiques évolutives globales."""
        # Calcul des espèces dominantes par type d'organisme
        dominant_species = {}

        for species_id, data in self.species_registry.items():
            if data.get('is_extinct', False) or data.get('count', 0) == 0:
                continue

            org_type = data.get('type')
            if org_type not in dominant_species or data.get('count', 0) > self.species_registry[dominant_species[org_type]].get('count', 0):
                dominant_species[org_type] = species_id

        self.dominant_species = dominant_species

        # Calcul de l'adaptation moyenne par biome
        biome_adaptations = {biome_type: [] for biome_type in BiomeType}

        for organism in self.organisms:
            if not organism.is_alive:
                continue

            cell = self.get_cell_at_position(organism.position)
            if cell:
                biome_type = cell.biome_type
                adaptation = self._calculate_biome_adaptation(organism, cell)
                biome_adaptations[biome_type].append(adaptation)

        # Calcul des moyennes
        self.adaptation_by_biome = {}
        for biome_type, adaptations in biome_adaptations.items():
            if adaptations:
                self.adaptation_by_biome[biome_type] = sum(adaptations) / len(adaptations)

    # Dictionnaires globaux pour l'adaptation aux biomes (évite de les recréer à chaque appel)
    _biome_adaptation_cache = {}
    _base_adaptation_table = None

    def _init_adaptation_tables(self):
        """Initialise les tables d'adaptation une seule fois pour améliorer les performances."""
        if self._base_adaptation_table is None:
            # Facteurs d'adaptation de base par type d'organisme et biome - AMÉLIORÉS
            self.__class__._base_adaptation_table = {
                OrganismType.UNICELLULAR: {
                    BiomeType.OCEAN: 0.95, BiomeType.DEEP_OCEAN: 0.85, BiomeType.SHALLOW_WATER: 0.9,
                    BiomeType.CORAL_REEF: 0.85, BiomeType.BEACH: 0.6, BiomeType.GRASSLAND: 0.5,
                    BiomeType.SAVANNA: 0.45, BiomeType.FOREST: 0.4, BiomeType.RAINFOREST: 0.5,
                    BiomeType.SWAMP: 0.7, BiomeType.MOUNTAIN: 0.3, BiomeType.MOUNTAIN_FOREST: 0.35,
                    BiomeType.DESERT: 0.4, BiomeType.DESERT_HILLS: 0.35, BiomeType.TUNDRA: 0.3,
                    BiomeType.ICE: 0.25, BiomeType.VOLCANIC: 0.4, BiomeType.RIVER: 0.85, BiomeType.LAKE: 0.8
                },
                OrganismType.PLANT: {
                    BiomeType.OCEAN: 0.4, BiomeType.DEEP_OCEAN: 0.2, BiomeType.SHALLOW_WATER: 0.7,
                    BiomeType.CORAL_REEF: 0.6, BiomeType.BEACH: 0.6, BiomeType.GRASSLAND: 0.95,
                    BiomeType.SAVANNA: 0.85, BiomeType.FOREST: 0.9, BiomeType.RAINFOREST: 0.95,
                    BiomeType.SWAMP: 0.8, BiomeType.MOUNTAIN: 0.5, BiomeType.MOUNTAIN_FOREST: 0.7,
                    BiomeType.DESERT: 0.4, BiomeType.DESERT_HILLS: 0.35, BiomeType.TUNDRA: 0.3,
                    BiomeType.ICE: 0.2, BiomeType.VOLCANIC: 0.3, BiomeType.RIVER: 0.7, BiomeType.LAKE: 0.75
                },
                OrganismType.HERBIVORE: {
                    BiomeType.OCEAN: 0.2, BiomeType.DEEP_OCEAN: 0.1, BiomeType.SHALLOW_WATER: 0.4,
                    BiomeType.CORAL_REEF: 0.3, BiomeType.BEACH: 0.6, BiomeType.GRASSLAND: 0.95,
                    BiomeType.SAVANNA: 0.9, BiomeType.FOREST: 0.8, BiomeType.RAINFOREST: 0.75,
                    BiomeType.SWAMP: 0.6, BiomeType.MOUNTAIN: 0.6, BiomeType.MOUNTAIN_FOREST: 0.7,
                    BiomeType.DESERT: 0.5, BiomeType.DESERT_HILLS: 0.45, BiomeType.TUNDRA: 0.4,
                    BiomeType.ICE: 0.25, BiomeType.VOLCANIC: 0.3, BiomeType.RIVER: 0.6, BiomeType.LAKE: 0.55
                },
                OrganismType.CARNIVORE: {
                    BiomeType.OCEAN: 0.3, BiomeType.DEEP_OCEAN: 0.2, BiomeType.SHALLOW_WATER: 0.5,
                    BiomeType.CORAL_REEF: 0.6, BiomeType.BEACH: 0.6, BiomeType.GRASSLAND: 0.8,
                    BiomeType.SAVANNA: 0.85, BiomeType.FOREST: 0.9, BiomeType.RAINFOREST: 0.8,
                    BiomeType.SWAMP: 0.7, BiomeType.MOUNTAIN: 0.7, BiomeType.MOUNTAIN_FOREST: 0.75,
                    BiomeType.DESERT: 0.6, BiomeType.DESERT_HILLS: 0.65, BiomeType.TUNDRA: 0.5,
                    BiomeType.ICE: 0.4, BiomeType.VOLCANIC: 0.4, BiomeType.RIVER: 0.6, BiomeType.LAKE: 0.55
                },
                OrganismType.OMNIVORE: {
                    BiomeType.OCEAN: 0.3, BiomeType.DEEP_OCEAN: 0.2, BiomeType.SHALLOW_WATER: 0.5,
                    BiomeType.CORAL_REEF: 0.55, BiomeType.BEACH: 0.7, BiomeType.GRASSLAND: 0.9,
                    BiomeType.SAVANNA: 0.85, BiomeType.FOREST: 0.9, BiomeType.RAINFOREST: 0.85,
                    BiomeType.SWAMP: 0.75, BiomeType.MOUNTAIN: 0.7, BiomeType.MOUNTAIN_FOREST: 0.8,
                    BiomeType.DESERT: 0.6, BiomeType.DESERT_HILLS: 0.55, BiomeType.TUNDRA: 0.5,
                    BiomeType.ICE: 0.35, BiomeType.VOLCANIC: 0.45, BiomeType.RIVER: 0.65, BiomeType.LAKE: 0.6
                }
            }

    def _calculate_biome_adaptation(self, organism: Organism, cell: 'WorldCell') -> float:
        """Calcule l'adaptation d'un organisme à un biome spécifique. Version optimisée."""
        # Initialiser les tables d'adaptation si nécessaire
        if self._base_adaptation_table is None:
            self._init_adaptation_tables()

        # Vérifier si l'adaptation est déjà en cache
        cache_key = (organism.id, cell.position)

        # Utiliser le cache seulement si l'organisme n'a pas changé récemment
        if cache_key in self._biome_adaptation_cache and self.update_counter % 10 != 0:
            return self._biome_adaptation_cache[cache_key]

        biome_type = cell.biome_type
        org_type = organism.organism_type

        # Adaptation de base pour ce type d'organisme dans ce biome
        adaptation = self._base_adaptation_table.get(org_type, {}).get(biome_type, 0.6)

        # Facteur d'adaptation génétique - calculé moins fréquemment
        if hasattr(organism, 'generation'):
            generation_factor = min(0.2, organism.generation * 0.01)
            adaptation += generation_factor

        # Température - calcul simplifié
        optimal_temp = getattr(organism, 'optimal_temperature', 20)
        temp_range = organism.phenotype.temperature_range
        temp_diff = abs(cell.temperature - optimal_temp)
        temp_adaptation = max(0, 1.0 - temp_diff / (temp_range * 1.2))

        # Ressources - calcul simplifié selon le type d'organisme
        if org_type == OrganismType.PLANT:
            # Simplifier le calcul pour les plantes
            resource_adaptation = (cell.resources[ResourceType.SUNLIGHT] + cell.resources[ResourceType.WATER]) / 160
        elif org_type == OrganismType.HERBIVORE:
            # Simplifier pour les herbivores
            resource_adaptation = min(1.0, cell.resources[ResourceType.ORGANIC_MATTER] /
                                   (cell.resource_capacity[ResourceType.ORGANIC_MATTER] * 0.7))
        else:
            # Valeur par défaut pour les autres types
            resource_adaptation = 0.7

        # Adaptation finale - calcul simplifié
        final_adaptation = adaptation * 0.6 + temp_adaptation * 0.25 + resource_adaptation * 0.15
        result = max(0.2, min(1.0, final_adaptation))

        # Mettre en cache le résultat
        self._biome_adaptation_cache[cache_key] = result

        # Nettoyer le cache périodiquement pour éviter qu'il ne devienne trop grand
        if self.update_counter % 1000 == 0:
            self._biome_adaptation_cache.clear()

        return result

    def _apply_selection_pressure(self, organism: Organism, delta_time: float):
        """Applique la pression de sélection naturelle sur un organisme."""
        # Obtenir la cellule actuelle
        cell = self.get_cell_at_position(organism.position)
        if not cell:
            return

        # Facteurs environnementaux qui affectent la survie
        biome_adaptation = self._calculate_biome_adaptation(organism, cell)

        # Pression de sélection basée sur l'adaptation au biome - RÉDUITE
        if biome_adaptation < 0.2:  # Seuil réduit de 0.3 à 0.2
            # Environnement très hostile pour cet organisme
            health_impact = (0.2 - biome_adaptation) * 5 * delta_time  # Impact réduit de 10 à 5
            organism.health = max(0, organism.health - health_impact)
        elif biome_adaptation > 0.7:  # Bonus pour bonne adaptation
            # Environnement favorable - léger bonus de santé
            health_bonus = (biome_adaptation - 0.7) * 2 * delta_time
            organism.health = min(100, organism.health + health_bonus)

        # Compétition pour les ressources - RÉDUITE
        nearby_organisms = self.get_nearby_organisms(organism, 20)
        same_type_count = sum(1 for org in nearby_organisms if org.organism_type == organism.organism_type)

        # Seuil de surpopulation augmenté et pénalité réduite
        if same_type_count > 15:  # Seuil augmenté de 10 à 15
            # Réduction de l'énergie disponible due à la compétition
            competition_factor = (same_type_count - 15) / 15
            energy_penalty = competition_factor * 1 * delta_time  # Pénalité réduite de 2 à 1
            organism.energy = max(0, organism.energy - energy_penalty)

        # Bonus pour les petites populations - favorise la diversité
        elif same_type_count < 5 and organism.energy < organism.phenotype.energy_capacity * 0.8:
            # Bonus d'énergie pour les espèces rares
            energy_bonus = (5 - same_type_count) * 0.5 * delta_time
            organism.energy = min(organism.phenotype.energy_capacity, organism.energy + energy_bonus)

    def spawn_random_organisms(self, count: int, weights=None):
        """Génère des organismes aléatoires dans le monde.

        Args:
            count: Nombre d'organismes à générer
            weights: Liste de poids pour chaque type d'organisme [unicellulaire, plante, herbivore, carnivore, omnivore]
        """
        if weights is None:
            weights = [0.3, 0.3, 0.2, 0.1, 0.1]  # Unicellulaire, Plante, Herbivore, Carnivore, Omnivore

        # Normalisation des poids
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [0.2, 0.2, 0.2, 0.2, 0.2]  # Poids égaux si somme nulle

        for _ in range(count):
            # Position aléatoire
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)

            # Type d'organisme aléatoire avec pondération
            org_type = random.choices(list(OrganismType), weights=weights)[0]

            # Création de l'organisme
            organism = Organism((x, y), None, org_type)

            # Vérification que l'organisme est dans un biome compatible
            cell = self.get_cell_at_position((x, y))
            if cell:
                # Vérification de compatibilité basique
                if (org_type == OrganismType.UNICELLULAR or
                    (org_type == OrganismType.PLANT and cell.biome_type != BiomeType.OCEAN and cell.biome_type != BiomeType.DESERT) or
                    (org_type in [OrganismType.HERBIVORE, OrganismType.CARNIVORE, OrganismType.OMNIVORE] and
                     cell.biome_type not in [BiomeType.OCEAN, BiomeType.SHALLOW_WATER])):
                    self.add_organism(organism)

    def get_cell_at_position(self, position: Tuple[float, float]) -> Optional[WorldCell]:
        """Récupère la cellule à une position donnée."""
        x = int(position[0] // self.cell_size)
        y = int(position[1] // self.cell_size)

        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.grid[x][y]

        return None

    def get_neighboring_cells(self, cell: WorldCell) -> List[WorldCell]:
        """Récupère les cellules voisines d'une cellule donnée."""
        neighbors = []
        cell_x = int(cell.position[0] // self.cell_size)
        cell_y = int(cell.position[1] // self.cell_size)

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue  # Ignorer la cellule elle-même

                nx, ny = cell_x + dx, cell_y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    neighbors.append(self.grid[nx][ny])

        return neighbors

    def draw(self, surface, camera_offset=(0, 0), zoom=1.0, selected_organism=None):
        """Dessine le monde et tous ses composants sur la surface donnée avec optimisation des performances."""
        # Calcule les limites visibles de l'écran
        screen_width, screen_height = surface.get_size()
        visible_min_x = camera_offset[0] - self.cell_size
        visible_min_y = camera_offset[1] - self.cell_size
        visible_max_x = camera_offset[0] + screen_width / zoom + self.cell_size
        visible_max_y = camera_offset[1] + screen_height / zoom + self.cell_size

        # Convertit en indices de grille
        min_grid_x = max(0, int(visible_min_x // self.cell_size))
        min_grid_y = max(0, int(visible_min_y // self.cell_size))
        max_grid_x = min(self.grid_width, int(visible_max_x // self.cell_size) + 1)
        max_grid_y = min(self.grid_height, int(visible_max_y // self.cell_size) + 1)

        # Optimisation: Utiliser une surface de rendu pour les cellules
        cell_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        # Déterminer le niveau de détail pour les cellules en fonction du zoom
        cell_detail = 1
        if zoom < 0.5:
            cell_detail = 2  # Dessiner une cellule sur deux
        if zoom < 0.25:
            cell_detail = 4  # Dessiner une cellule sur quatre

        # Optimisation: regrouper les cellules par couleur pour réduire les appels de dessin
        color_groups = {}

        # Collecter les cellules par couleur
        for x in range(min_grid_x, max_grid_x, cell_detail):
            for y in range(min_grid_y, max_grid_y, cell_detail):
                if x < self.grid_width and y < self.grid_height:
                    cell = self.grid[x][y]

                    # Position à l'écran
                    screen_x = (cell.position[0] - camera_offset[0]) * zoom
                    screen_y = (cell.position[1] - camera_offset[1]) * zoom

                    # Taille à l'écran (ajustée pour le niveau de détail)
                    cell_width = self.cell_size * zoom * cell_detail
                    cell_height = self.cell_size * zoom * cell_detail

                    # Obtenir la couleur de la cellule
                    cell_color = cell.get_color()
                    color_key = tuple(cell_color)  # Convertir en tuple pour pouvoir l'utiliser comme clé

                    # Ajouter aux groupes de couleur
                    if color_key not in color_groups:
                        color_groups[color_key] = []
                    color_groups[color_key].append((screen_x, screen_y, cell_width, cell_height))

        # Dessiner chaque groupe de couleur en une seule fois
        for color, rects in color_groups.items():
            for rect in rects:
                pygame.draw.rect(cell_surface, color, rect)

        # Appliquer la surface des cellules sur la surface principale
        surface.blit(cell_surface, (0, 0))

        # Ajouter des effets visuels pour le cycle jour/nuit
        if hasattr(self, 'day_cycle'):
            # Créer un effet de lumière en fonction de l'heure de la journée
            day_progress = self.day_cycle % 1.0  # Normaliser entre 0 et 1

            # Calculer l'intensité lumineuse (plus sombre la nuit)
            if day_progress < 0.25:  # Aube
                light_intensity = day_progress * 4  # 0 -> 1
            elif day_progress < 0.75:  # Jour
                light_intensity = 1.0
            else:  # Crépuscule et nuit
                light_intensity = max(0, 1 - (day_progress - 0.75) * 4)  # 1 -> 0

            # Créer un effet d'éclairage global
            if light_intensity < 1.0:
                # Créer une surface semi-transparente pour l'effet de nuit
                darkness = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
                darkness_alpha = int(150 * (1 - light_intensity))  # Plus sombre quand l'intensité est faible
                darkness.fill((0, 0, 50, darkness_alpha))  # Teinte bleutée pour la nuit
                surface.blit(darkness, (0, 0))

        # Déterminer le niveau de détail pour le rendu des organismes
        organism_count = len(self.organisms)
        render_detail_level = 1.0  # Niveau de détail complet par défaut

        # Ajuster le niveau de détail en fonction du nombre d'organismes et du zoom
        if zoom < 0.5:
            render_detail_level *= 0.5  # Réduire encore plus si le zoom est faible

        if organism_count > 3000:
            render_detail_level *= 0.5  # Dessiner un organisme sur deux
        if organism_count > 6000:
            render_detail_level *= 0.5  # Dessiner un organisme sur quatre
        if organism_count > 10000:
            render_detail_level *= 0.5  # Dessiner un organisme sur huit

        # Optimisation: utiliser une surface dédiée pour les organismes
        organism_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        # Optimisation: regrouper les organismes par type pour le rendu par lots
        organism_groups = {
            OrganismType.UNICELLULAR: [],
            OrganismType.PLANT: [],
            OrganismType.HERBIVORE: [],
            OrganismType.CARNIVORE: [],
            OrganismType.OMNIVORE: []
        }

        # Utiliser la grille spatiale pour récupérer efficacement les organismes visibles
        visible_organisms = []

        # Utiliser la grille spatiale si disponible, sinon parcourir tous les organismes
        if hasattr(self, 'spatial_grid') and self.spatial_grid:
            # Calculer les cellules de la grille spatiale visibles
            min_spatial_x = int(visible_min_x / self.spatial_grid.cell_size)
            min_spatial_y = int(visible_min_y / self.spatial_grid.cell_size)
            max_spatial_x = int(visible_max_x / self.spatial_grid.cell_size) + 1
            max_spatial_y = int(visible_max_y / self.spatial_grid.cell_size) + 1

            # Récupérer les organismes dans les cellules visibles
            for x in range(min_spatial_x, max_spatial_x):
                for y in range(min_spatial_y, max_spatial_y):
                    cell_key = (x, y)
                    if cell_key in self.spatial_grid.grid:
                        visible_organisms.extend(self.spatial_grid.grid[cell_key])
        else:
            # Parcourir tous les organismes (moins efficace)
            for organism in self.organisms:
                if organism.is_alive:
                    # Vérifie si l'organisme est dans la zone visible
                    org_x, org_y = organism.position
                    if (visible_min_x <= org_x <= visible_max_x and
                        visible_min_y <= org_y <= visible_max_y):
                        visible_organisms.append(organism)

        # Appliquer le niveau de détail (ne dessiner qu'une fraction des organismes)
        if render_detail_level < 1.0 and len(visible_organisms) > 100:
            # Toujours inclure l'organisme sélectionné
            selected_included = False
            if selected_organism and selected_organism.is_alive:
                for org in visible_organisms:
                    if org.id == selected_organism.id:
                        selected_included = True
                        break
                if not selected_included:
                    visible_organisms.append(selected_organism)

            # Échantillonner les organismes à dessiner
            sample_size = max(50, int(len(visible_organisms) * render_detail_level))
            if sample_size < len(visible_organisms):
                # Utiliser un échantillonnage stratifié pour maintenir la diversité
                # Regrouper par type d'organisme
                type_groups = {org_type: [] for org_type in OrganismType}
                for org in visible_organisms:
                    type_groups[org.organism_type].append(org)

                # Échantillonner proportionnellement de chaque groupe
                sampled_organisms = []
                for org_type, orgs in type_groups.items():
                    if orgs:
                        group_size = max(1, int(len(orgs) * render_detail_level))
                        sampled_organisms.extend(random.sample(orgs, min(group_size, len(orgs))))

                # S'assurer que l'organisme sélectionné est inclus
                if selected_organism and selected_organism.is_alive:
                    selected_in_sample = False
                    for org in sampled_organisms:
                        if org.id == selected_organism.id:
                            selected_in_sample = True
                            break
                    if not selected_in_sample:
                        sampled_organisms.append(selected_organism)

                visible_organisms = sampled_organisms

        # Regrouper les organismes par type pour le rendu par lots
        for organism in visible_organisms:
            organism_groups[organism.organism_type].append(organism)

        # Dessiner les organismes par type (d'abord les plus petits, puis les plus grands)
        for org_type in [OrganismType.UNICELLULAR, OrganismType.PLANT,
                         OrganismType.HERBIVORE, OrganismType.OMNIVORE, OrganismType.CARNIVORE]:
            # Dessiner tous les organismes de ce type
            for organism in organism_groups[org_type]:
                # Vérifie si c'est l'organisme sélectionné
                is_selected = selected_organism is not None and organism.id == selected_organism.id

                # Dessiner avec un niveau de détail adapté au zoom
                if zoom < 0.3 and not is_selected:
                    # Version simplifiée pour les zooms lointains
                    # Position à l'écran
                    screen_x = int((organism.position[0] - camera_offset[0]) * zoom)
                    screen_y = int((organism.position[1] - camera_offset[1]) * zoom)

                    # Taille simplifiée
                    size = max(2, int(organism.phenotype.size * zoom))

                    # Couleur selon le type
                    if org_type == OrganismType.UNICELLULAR:
                        color = (100, 100, 255)
                    elif org_type == OrganismType.PLANT:
                        color = (0, 200, 0)
                    elif org_type == OrganismType.HERBIVORE:
                        color = (200, 200, 0)
                    elif org_type == OrganismType.CARNIVORE:
                        color = (200, 0, 0)
                    else:  # OMNIVORE
                        color = (200, 0, 200)

                    # Dessiner un simple cercle
                    pygame.draw.circle(organism_surface, color, (screen_x, screen_y), size)
                else:
                    # Rendu détaillé pour les zooms proches
                    organism.draw(organism_surface, camera_offset, zoom, selected=is_selected)

        # Appliquer la surface des organismes sur la surface principale
        surface.blit(organism_surface, (0, 0))

        # Ajouter des effets visuels pour les organismes sélectionnés
        if selected_organism and selected_organism.is_alive:
            # Position à l'écran
            screen_x = int((selected_organism.position[0] - camera_offset[0]) * zoom)
            screen_y = int((selected_organism.position[1] - camera_offset[1]) * zoom)

            # Dessiner un halo autour de l'organisme sélectionné
            size = max(10, int(selected_organism.phenotype.size * zoom * 2))

            # Créer un effet de pulsation
            pulse = (math.sin(time.time() * 5) + 1) / 2  # Valeur entre 0 et 1
            pulse_size = int(size * (1 + pulse * 0.3))

            # Dessiner un cercle semi-transparent
            glow_surface = pygame.Surface((pulse_size*2, pulse_size*2), pygame.SRCALPHA)
            alpha = int(100 + pulse * 100)  # Transparence variable
            pygame.draw.circle(glow_surface, (255, 255, 100, alpha), (pulse_size, pulse_size), pulse_size)
            surface.blit(glow_surface, (screen_x - pulse_size, screen_y - pulse_size))


class UIElement:
    """Classe de base pour les éléments d'interface utilisateur."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True

    def draw(self, surface):
        """Méthode à implémenter dans les classes dérivées."""
        pass

    def update(self, mouse_pos):
        """Méthode à implémenter dans les classes dérivées."""
        pass

class Panel(UIElement):
    """Panneau d'interface utilisateur avec titre et contenu."""
    def __init__(self, x, y, width, height, title="", bg_color=(30, 30, 50), border_color=(80, 80, 120),
                 title_color=(200, 200, 100), content_color=WHITE, alpha=220):
        super().__init__(x, y, width, height)
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        self.title_color = title_color
        self.content_color = content_color
        self.alpha = alpha
        self.content = []
        self.title_height = 30 if title else 0
        self.padding = 10
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 30)

    def draw(self, surface):
        """Dessine le panneau avec son titre et son contenu."""
        if not self.visible:
            return

        # Créer une surface avec transparence
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        panel_surface.fill((self.bg_color[0], self.bg_color[1], self.bg_color[2], self.alpha))

        # Dessiner la bordure
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.rect.width, self.rect.height), 2)

        # Dessiner le titre s'il existe
        if self.title:
            title_rect = pygame.Rect(0, 0, self.rect.width, self.title_height)
            pygame.draw.rect(panel_surface, (self.bg_color[0]+20, self.bg_color[1]+20, self.bg_color[2]+20, self.alpha), title_rect)
            pygame.draw.line(panel_surface, self.border_color, (0, self.title_height), (self.rect.width, self.title_height))

            title_surface = self.title_font.render(self.title, True, self.title_color)
            title_pos = (self.rect.width // 2 - title_surface.get_width() // 2, self.title_height // 2 - title_surface.get_height() // 2)
            panel_surface.blit(title_surface, title_pos)

        # Appliquer la surface sur l'écran
        surface.blit(panel_surface, self.rect.topleft)

        # Dessiner le contenu
        content_y = self.rect.y + self.title_height + self.padding
        for item in self.content:
            if isinstance(item, tuple) and len(item) == 2:
                # Texte simple (texte, couleur)
                text, color = item
                text_surface = self.font.render(text, True, color)
                surface.blit(text_surface, (self.rect.x + self.padding, content_y))
                content_y += text_surface.get_height() + 5
            elif isinstance(item, tuple) and len(item) == 3 and item[0] == "progress":
                # Barre de progression (type, label, valeur, max_valeur, couleur)
                _, label_value, color = item
                label, value = label_value

                # Texte du label
                label_surface = self.font.render(f"{label}:", True, self.content_color)
                surface.blit(label_surface, (self.rect.x + self.padding, content_y))

                # Barre de progression
                bar_width = 150
                bar_height = 15
                bar_x = self.rect.x + self.rect.width - bar_width - self.padding
                bar_y = content_y + label_surface.get_height() // 2 - bar_height // 2

                # Fond de la barre
                pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

                # Valeur normalisée entre 0 et 1
                normalized_value = max(0, min(1, value))
                filled_width = int(bar_width * normalized_value)

                # Barre remplie
                pygame.draw.rect(surface, color, (bar_x, bar_y, filled_width, bar_height))

                # Bordure
                pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

                # Valeur numérique
                value_text = f"{value:.2f}"
                value_surface = self.font.render(value_text, True, self.content_color)
                surface.blit(value_surface, (bar_x + bar_width + 5, content_y))

                content_y += max(label_surface.get_height(), bar_height) + 10
            elif isinstance(item, UIElement):
                # Sous-élément d'interface
                item.rect.x = self.rect.x + self.padding
                item.rect.y = content_y
                item.draw(surface)
                content_y += item.rect.height + 5

    def add_text(self, text, color=None):
        """Ajoute une ligne de texte au panneau."""
        if color is None:
            color = self.content_color
        self.content.append((text, color))

    def add_progress_bar(self, label, value, color=(100, 200, 100)):
        """Ajoute une barre de progression au panneau."""
        self.content.append(("progress", (label, value), color))

    def add_element(self, element):
        """Ajoute un élément d'interface au panneau."""
        self.content.append(element)

    def clear(self):
        """Efface tout le contenu du panneau."""
        self.content = []

class Slider(UIElement):
    """Classe pour créer des sliders interactifs dans l'interface."""
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, label="",
                 track_color=(60, 60, 80), handle_color=(100, 120, 200), label_color=WHITE):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.track_color = track_color
        self.handle_color = handle_color
        self.label_color = label_color
        self.dragging = False
        self.handle_width = 16
        self.handle_height = height + 8
        self.handle_rect = pygame.Rect(0, 0, self.handle_width, self.handle_height)
        self.font = pygame.font.SysFont(None, 24)
        self.update_handle_position()

    def draw(self, surface):
        """Dessine le slider sur la surface donnée."""
        if not self.visible:
            return

        # Fond du slider (piste)
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(surface, self.track_color, track_rect, border_radius=3)

        # Partie remplie du slider
        filled_width = self.handle_rect.centerx - self.rect.x
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, filled_width, 6)
            filled_color = (min(255, self.handle_color[0] + 20),
                           min(255, self.handle_color[1] + 20),
                           min(255, self.handle_color[2] + 20))
            pygame.draw.rect(surface, filled_color, filled_rect, border_radius=3)

        # Poignée du slider
        pygame.draw.rect(surface, self.handle_color, self.handle_rect, border_radius=self.handle_width//2)
        pygame.draw.rect(surface, (min(255, self.handle_color[0] + 50),
                                  min(255, self.handle_color[1] + 50),
                                  min(255, self.handle_color[2] + 50)),
                        self.handle_rect, 2, border_radius=self.handle_width//2)

        # Étiquette
        label_text = f"{self.label}"
        text_surface = self.font.render(label_text, True, self.label_color)
        text_rect = text_surface.get_rect(bottomleft=(self.rect.x, self.rect.y - 5))
        surface.blit(text_surface, text_rect)

        # Valeur
        value_text = f"{self.value:.2f}"
        value_surface = self.font.render(value_text, True, self.label_color)
        value_rect = value_surface.get_rect(bottomright=(self.rect.right, self.rect.y - 5))
        surface.blit(value_surface, value_rect)

    def update_handle_position(self):
        """Met à jour la position de la poignée en fonction de la valeur."""
        value_ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + int(value_ratio * self.rect.width) - self.handle_rect.width // 2
        self.handle_rect.x = max(self.rect.x - self.handle_width//2,
                               min(self.rect.right - self.handle_width//2, handle_x))
        self.handle_rect.centery = self.rect.centery

    def update(self, mouse_pos):
        """Met à jour l'état du slider en fonction de la position de la souris."""
        if not self.visible:
            return

        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # Bouton gauche de la souris
            if self.handle_rect.collidepoint(mouse_pos) or self.dragging:
                self.dragging = True
                x_pos = max(self.rect.x, min(self.rect.right, mouse_pos[0]))
                position_ratio = (x_pos - self.rect.x) / self.rect.width
                self.value = self.min_value + position_ratio * (self.max_value - self.min_value)
                self.update_handle_position()
        else:
            self.dragging = False

    def handle_event(self, event):
        """Gère les événements pour le slider."""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x_pos = max(self.rect.x, min(self.rect.right, event.pos[0]))
            position_ratio = (x_pos - self.rect.x) / self.rect.width
            self.value = self.min_value + position_ratio * (self.max_value - self.min_value)
            self.update_handle_position()
            return True
        return False

class Button(UIElement):
    """Classe pour créer des boutons interactifs dans l'interface."""
    def __init__(self, x, y, width, height, text, color=(60, 60, 100), hover_color=(80, 80, 150),
                 text_color=WHITE, border_radius=5, icon=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.icon = icon
        self.hovered = False
        self.clicked = False
        self.font = pygame.font.SysFont(None, 28)

    def draw(self, surface):
        """Dessine le bouton sur la surface donnée."""
        if not self.visible:
            return

        # Déterminer la couleur en fonction de l'état
        color = self.hover_color if self.hovered else self.color
        if self.clicked:
            # Assombrir la couleur si cliqué
            color = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 30))

        # Dessiner le fond avec des coins arrondis
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        # Dessiner la bordure
        border_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=self.border_radius)

        # Dessiner l'icône si elle existe
        icon_width = 0
        if self.icon:
            icon_pos = (self.rect.x + 10, self.rect.centery - self.icon.get_height() // 2)
            surface.blit(self.icon, icon_pos)
            icon_width = self.icon.get_width() + 5

        # Dessiner le texte
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect()

        # Centrer le texte, en tenant compte de l'icône si elle existe
        if self.icon:
            text_rect.midleft = (self.rect.x + 15 + icon_width, self.rect.centery)
        else:
            text_rect.center = self.rect.center

        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        """Met à jour l'état du bouton en fonction de la position de la souris."""
        if not self.visible:
            return
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        """Gère les événements pour le bouton."""
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.clicked = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_clicked = self.clicked and self.hovered
            self.clicked = False
            return was_clicked
        return False

    def is_clicked(self, mouse_pos, mouse_click):
        """Vérifie si le bouton est cliqué."""
        if not self.visible:
            return False
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Slider:
    """Classe pour créer des sliders interactifs dans l'interface."""
    def __init__(self, x, y, width, height, min_value, max_value, initial_value, label, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.color = color
        self.handle_rect = pygame.Rect(0, 0, 20, height + 10)
        self.update_handle_position()
        self.dragging = False

    def update_handle_position(self):
        """Met à jour la position de la poignée du slider."""
        value_range = self.max_value - self.min_value
        position_ratio = (self.value - self.min_value) / value_range
        handle_x = self.rect.x + position_ratio * self.rect.width - self.handle_rect.width / 2
        self.handle_rect.x = handle_x
        self.handle_rect.y = self.rect.y - 5

    def draw(self, surface):
        """Dessine le slider sur la surface donnée."""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # Bordure
        pygame.draw.rect(surface, (200, 200, 200), self.handle_rect)
        pygame.draw.rect(surface, WHITE, self.handle_rect, 2)  # Bordure de la poignée

        font = pygame.font.SysFont(None, 24)
        label_text = f"{self.label}: {self.value:.1f}"
        text_surface = font.render(label_text, True, WHITE)
        text_rect = text_surface.get_rect(midleft=(self.rect.x, self.rect.y - 15))
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos, mouse_pressed):
        """Met à jour l'état du slider en fonction de la position de la souris."""
        if mouse_pressed[0]:  # Bouton gauche de la souris
            if self.handle_rect.collidepoint(mouse_pos):
                self.dragging = True
            elif self.dragging:
                # Mettre à jour la valeur en fonction de la position de la souris
                x_pos = max(self.rect.x, min(mouse_pos[0], self.rect.x + self.rect.width))
                position_ratio = (x_pos - self.rect.x) / self.rect.width
                self.value = self.min_value + position_ratio * (self.max_value - self.min_value)
                self.update_handle_position()
        else:
            self.dragging = False

class WorldCreator:
    """Interface pour créer un monde personnalisé."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 32)

        # Paramètres du monde
        self.world_width = MAP_WIDTH
        self.world_height = MAP_HEIGHT
        self.cell_size = CELL_SIZE

        # Paramètres de population initiale
        self.initial_organisms = 200
        self.unicellular_ratio = 0.3
        self.plant_ratio = 0.3
        self.herbivore_ratio = 0.2
        self.carnivore_ratio = 0.1
        self.omnivore_ratio = 0.1

        # Paramètres environnementaux
        self.ocean_ratio = 0.35
        self.mountain_ratio = 0.15
        self.forest_ratio = 0.25
        self.desert_ratio = 0.1
        self.swamp_ratio = 0.05
        self.volcanic_ratio = 0.02
        self.temperature = 20.0

        # Création des contrôles
        button_width = 200
        button_height = 50
        slider_width = 300
        slider_height = 20

        # Boutons
        self.create_button = Button(SCREEN_WIDTH // 2 - button_width // 2,
                                   SCREEN_HEIGHT - 100,
                                   button_width, button_height,
                                   "Créer le monde", (0, 100, 0), (0, 150, 0))

        self.back_button = Button(50, SCREEN_HEIGHT - 100,
                                 button_width, button_height,
                                 "Retour", (100, 0, 0), (150, 0, 0))

        # Sliders
        self.sliders = [
            Slider(SCREEN_WIDTH // 4, 150, slider_width, slider_height, 50, 500, self.initial_organisms, "Organismes initiaux"),
            Slider(SCREEN_WIDTH // 4, 200, slider_width, slider_height, 0.1, 0.5, self.unicellular_ratio, "Ratio unicellulaires"),
            Slider(SCREEN_WIDTH // 4, 250, slider_width, slider_height, 0.1, 0.5, self.plant_ratio, "Ratio plantes"),
            Slider(SCREEN_WIDTH // 4, 300, slider_width, slider_height, 0.1, 0.5, self.herbivore_ratio, "Ratio herbivores"),
            Slider(SCREEN_WIDTH // 4, 350, slider_width, slider_height, 0.0, 0.3, self.carnivore_ratio, "Ratio carnivores"),
            Slider(SCREEN_WIDTH // 4, 400, slider_width, slider_height, 0.0, 0.3, self.omnivore_ratio, "Ratio omnivores"),

            Slider(SCREEN_WIDTH * 3 // 4 - slider_width, 150, slider_width, slider_height, 0.1, 0.5, self.ocean_ratio, "Ratio océans"),
            Slider(SCREEN_WIDTH * 3 // 4 - slider_width, 200, slider_width, slider_height, 0.1, 0.4, self.mountain_ratio, "Ratio montagnes"),
            Slider(SCREEN_WIDTH * 3 // 4 - slider_width, 250, slider_width, slider_height, 0.1, 0.4, self.forest_ratio, "Ratio forêts"),
            Slider(SCREEN_WIDTH * 3 // 4 - slider_width, 300, slider_width, slider_height, 0.0, 0.3, self.desert_ratio, "Ratio déserts"),
            Slider(SCREEN_WIDTH * 3 // 4 - slider_width, 350, slider_width, slider_height, 5.0, 35.0, self.temperature, "Température (°C)")
        ]

    def run(self):
        """Exécute l'interface de création de monde."""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        mouse_click = True

            # Mise à jour des contrôles
            self.create_button.update(mouse_pos)
            self.back_button.update(mouse_pos)

            for slider in self.sliders:
                slider.update(mouse_pos, mouse_pressed)

            # Vérification des clics
            if self.create_button.is_clicked(mouse_pos, mouse_click):
                return self.create_world()

            if self.back_button.is_clicked(mouse_pos, mouse_click):
                return None

            # Mise à jour des paramètres
            self.initial_organisms = int(self.sliders[0].value)
            self.unicellular_ratio = self.sliders[1].value
            self.plant_ratio = self.sliders[2].value
            self.herbivore_ratio = self.sliders[3].value
            self.carnivore_ratio = self.sliders[4].value
            self.omnivore_ratio = self.sliders[5].value

            self.ocean_ratio = self.sliders[6].value
            self.mountain_ratio = self.sliders[7].value
            self.forest_ratio = self.sliders[8].value
            self.desert_ratio = self.sliders[9].value
            self.temperature = self.sliders[10].value

            # Normalisation des ratios d'organismes
            total_ratio = (self.unicellular_ratio + self.plant_ratio +
                          self.herbivore_ratio + self.carnivore_ratio +
                          self.omnivore_ratio)

            if total_ratio > 0:
                self.unicellular_ratio /= total_ratio
                self.plant_ratio /= total_ratio
                self.herbivore_ratio /= total_ratio
                self.carnivore_ratio /= total_ratio
                self.omnivore_ratio /= total_ratio

            # Dessin de l'interface
            self.draw()

            # Mise à jour de l'affichage
            pygame.display.flip()
            self.clock.tick(60)

        return None

    def draw(self):
        """Dessine l'interface de création de monde."""
        self.screen.fill((20, 20, 40))

        # Titre
        title_text = self.font.render("Création d'un Nouveau Monde", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)

        # Sous-titres
        subtitle_font = pygame.font.SysFont(None, 28)

        population_text = subtitle_font.render("Paramètres de Population", True, (200, 200, 100))
        population_rect = population_text.get_rect(topleft=(SCREEN_WIDTH // 4, 100))
        self.screen.blit(population_text, population_rect)

        environment_text = subtitle_font.render("Paramètres Environnementaux", True, (100, 200, 200))
        environment_rect = environment_text.get_rect(topleft=(SCREEN_WIDTH * 3 // 4 - 300, 100))
        self.screen.blit(environment_text, environment_rect)

        # Dessiner les contrôles
        self.create_button.draw(self.screen)
        self.back_button.draw(self.screen)

        for slider in self.sliders:
            slider.draw(self.screen)

        # Aperçu du monde (simplifié)
        preview_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 450, 300, 200)
        pygame.draw.rect(self.screen, (50, 50, 70), preview_rect)
        pygame.draw.rect(self.screen, WHITE, preview_rect, 2)

        # Dessiner un aperçu simplifié des biomes
        ocean_height = int(preview_rect.height * self.ocean_ratio)
        mountain_height = int(preview_rect.height * self.mountain_ratio)
        forest_height = int(preview_rect.height * self.forest_ratio)
        desert_height = int(preview_rect.height * self.desert_ratio)

        # Océan
        pygame.draw.rect(self.screen, (0, 0, 150),
                        (preview_rect.x, preview_rect.y,
                         preview_rect.width, ocean_height))

        # Montagnes
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (preview_rect.x, preview_rect.y + ocean_height,
                         preview_rect.width, mountain_height))

        # Forêts
        pygame.draw.rect(self.screen, (0, 100, 0),
                        (preview_rect.x, preview_rect.y + ocean_height + mountain_height,
                         preview_rect.width, forest_height))

        # Déserts
        pygame.draw.rect(self.screen, (194, 178, 78),
                        (preview_rect.x, preview_rect.y + ocean_height + mountain_height + forest_height,
                         preview_rect.width, desert_height))

        # Texte d'aperçu
        preview_text = subtitle_font.render("Aperçu du monde", True, WHITE)
        preview_text_rect = preview_text.get_rect(midtop=(preview_rect.centerx, preview_rect.y - 30))
        self.screen.blit(preview_text, preview_text_rect)

    def create_world(self):
        """Crée un monde avec les paramètres spécifiés."""
        world = World(self.world_width, self.world_height, cell_size=self.cell_size)

        # Personnalisation du monde
        world.global_temperature = self.temperature

        # Personnalisation des biomes lors de la génération
        world.biome_ratios = {
            "ocean": self.ocean_ratio,
            "mountain": self.mountain_ratio,
            "forest": self.forest_ratio,
            "desert": self.desert_ratio,
            "swamp": 0.05,
            "volcanic": 0.02
        }

        print(f"Création d'un monde de {self.world_width}x{self.world_height} pixels avec des cellules de {self.cell_size} pixels")
        print(f"Nombre total de cellules: {world.grid_width}x{world.grid_height} = {world.grid_width * world.grid_height}")

        # Génération du monde avec les ratios personnalisés
        world._generate_world()

        # Génération des organismes initiaux avec les ratios spécifiés
        weights = [
            self.unicellular_ratio,
            self.plant_ratio,
            self.herbivore_ratio,
            self.carnivore_ratio,
            self.omnivore_ratio
        ]

        print(f"Génération de {self.initial_organisms} organismes initiaux...")
        world.spawn_random_organisms(self.initial_organisms, weights)

        return world

class Button:
    """Classe représentant un bouton interactif avec des effets visuels améliorés."""
    def __init__(self, x, y, width, height, text, color, hover_color,
                 border_radius=0, font_size=28, text_color=(255, 255, 255),
                 border_color=None, border_width=0, sound=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = text_color
        self.border_radius = border_radius
        self.border_color = border_color
        self.border_width = border_width
        self.font = pygame.font.SysFont(None, font_size)
        self.sound = sound
        self.hovered = False

        # Effet de pulsation
        self.pulse_effect = False
        self.pulse_time = 0
        self.pulse_speed = 0.005
        self.pulse_amplitude = 0.2

        # Animation de clic
        self.clicked = False
        self.click_time = 0
        self.click_duration = 0.2  # secondes

        # Effet d'ombre
        self.shadow_offset = 3
        self.shadow_color = (0, 0, 0, 128)  # Noir semi-transparent

        # Rendu du texte
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos):
        """Met à jour l'état du bouton en fonction de la position de la souris."""
        # Vérifier si la souris survole le bouton
        self.hovered = self.rect.collidepoint(mouse_pos)

        # Mise à jour de la couleur
        if self.hovered and not self.clicked:
            self.current_color = self.hover_color
            # Activer l'effet de pulsation lors du survol
            self.pulse_effect = True
        elif not self.clicked:
            self.current_color = self.base_color
            self.pulse_effect = False

        # Mise à jour de l'effet de pulsation
        if self.pulse_effect:
            self.pulse_time += self.pulse_speed
            pulse_factor = math.sin(self.pulse_time) * self.pulse_amplitude

            # Ajuster la couleur avec l'effet de pulsation
            r = min(255, max(0, self.current_color[0] * (1 + pulse_factor)))
            g = min(255, max(0, self.current_color[1] * (1 + pulse_factor)))
            b = min(255, max(0, self.current_color[2] * (1 + pulse_factor)))

            self.current_color = (r, g, b)

        # Mise à jour de l'animation de clic
        if self.clicked:
            current_time = time.time()
            if current_time - self.click_time > self.click_duration:
                self.clicked = False
            else:
                # Animation de "pression" du bouton
                progress = (current_time - self.click_time) / self.click_duration
                if progress < 0.5:
                    # Phase d'enfoncement
                    self.current_color = tuple(max(0, c - 30) for c in self.base_color)
                else:
                    # Phase de relâchement
                    self.current_color = tuple(min(255, c + 30) for c in self.hover_color)

    def is_clicked(self, mouse_pos, mouse_click):
        """Vérifie si le bouton est cliqué."""
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            self.clicked = True
            self.click_time = time.time()
            # Jouer un son si disponible
            if self.sound:
                self.sound.play()
            return True
        return False

    def draw(self, surface):
        """Dessine le bouton avec des effets visuels."""
        # Dessiner l'ombre
        shadow_rect = pygame.Rect(
            self.rect.x + self.shadow_offset,
            self.rect.y + self.shadow_offset,
            self.rect.width,
            self.rect.height
        )

        # Créer une surface pour l'ombre semi-transparente
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            shadow_surface,
            self.shadow_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
            border_radius=self.border_radius
        )

        # Appliquer l'ombre si le bouton n'est pas cliqué
        if not self.clicked:
            surface.blit(shadow_surface, shadow_rect)

        # Dessiner le corps du bouton
        button_rect = self.rect.copy()
        if self.clicked:
            # Effet d'enfoncement lors du clic
            button_rect.x += 2
            button_rect.y += 2

        pygame.draw.rect(
            surface,
            self.current_color,
            button_rect,
            border_radius=self.border_radius
        )

        # Dessiner la bordure si spécifiée
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                surface,
                self.border_color,
                button_rect,
                width=self.border_width,
                border_radius=self.border_radius
            )

        # Dessiner le texte
        text_rect = self.text_rect.copy()
        if self.clicked:
            # Déplacer le texte avec le bouton lors du clic
            text_rect.x += 2
            text_rect.y += 2

        surface.blit(self.text_surface, text_rect)


class Panel:
    """Panneau d'interface utilisateur pour afficher des informations."""
    def __init__(self, x, y, width, height, title=None, alpha=200,
                 bg_color=(20, 30, 50), border_color=(100, 150, 200),
                 title_color=(220, 220, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.alpha = alpha
        self.bg_color = bg_color
        self.border_color = border_color
        self.title_color = title_color

        # Polices
        self.title_font = pygame.font.SysFont(None, 28)
        self.text_font = pygame.font.SysFont(None, 22)

        # Contenu
        self.content = []
        self.scroll_position = 0
        self.max_scroll = 0

        # Barres de défilement
        self.scrollbar_width = 10
        self.scrollbar_active = False
        self.scrollbar_dragging = False

    def add_text(self, text, color=(200, 200, 200)):
        """Ajoute une ligne de texte au panneau."""
        self.content.append({"type": "text", "text": text, "color": color})

    def add_separator(self, color=(100, 100, 150)):
        """Ajoute une ligne de séparation."""
        self.content.append({"type": "separator", "color": color})

    def add_progress_bar(self, label, value, color=(0, 200, 100)):
        """Ajoute une barre de progression avec étiquette."""
        self.content.append({
            "type": "progress_bar",
            "label": label,
            "value": max(0, min(1, value)),  # Valeur entre 0 et 1
            "color": color
        })

    def add_chart(self, data, labels=None, title=None, color_map=None):
        """Ajoute un graphique simple."""
        if not data:
            return

        if not labels:
            labels = [str(i) for i in range(len(data))]

        if not color_map:
            color_map = [(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
                         for _ in range(len(data))]

        self.content.append({
            "type": "chart",
            "data": data,
            "labels": labels,
            "title": title,
            "color_map": color_map
        })

    def handle_event(self, event):
        """Gère les événements pour le panneau (défilement, etc.)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Molette vers le haut
                self.scroll_position = max(0, self.scroll_position - 20)
            elif event.button == 5:  # Molette vers le bas
                self.scroll_position = min(self.max_scroll, self.scroll_position + 20)

            # Gestion du clic sur la barre de défilement
            scrollbar_rect = self._get_scrollbar_rect()
            if scrollbar_rect.collidepoint(event.pos):
                self.scrollbar_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.scrollbar_dragging:
            # Déplacer la barre de défilement
            _, mouse_y = event.pos
            relative_y = mouse_y - self.rect.y
            scroll_ratio = relative_y / self.rect.height
            self.scroll_position = int(scroll_ratio * self.max_scroll)
            self.scroll_position = max(0, min(self.max_scroll, self.scroll_position))

    def _get_scrollbar_rect(self):
        """Calcule la position et la taille de la barre de défilement."""
        if self.max_scroll <= 0:
            return pygame.Rect(0, 0, 0, 0)  # Pas de barre si pas de défilement

        # Hauteur proportionnelle au contenu visible
        content_ratio = min(1.0, self.rect.height / (self.rect.height + self.max_scroll))
        scrollbar_height = max(20, int(self.rect.height * content_ratio))

        # Position proportionnelle au défilement
        scroll_ratio = 0 if self.max_scroll == 0 else self.scroll_position / self.max_scroll
        scrollbar_y = self.rect.y + int(scroll_ratio * (self.rect.height - scrollbar_height))

        return pygame.Rect(
            self.rect.right - self.scrollbar_width - 2,
            scrollbar_y,
            self.scrollbar_width,
            scrollbar_height
        )

    def draw(self, surface):
        """Dessine le panneau et son contenu."""
        # Créer une surface avec transparence
        panel_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        panel_surface.fill((self.bg_color[0], self.bg_color[1], self.bg_color[2], self.alpha))

        # Dessiner la bordure
        pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.rect.width, self.rect.height), 2)

        # Dessiner le titre
        if self.title:
            title_surface = self.title_font.render(self.title, True, self.title_color)
            title_rect = title_surface.get_rect(midtop=(self.rect.width // 2, 10))
            panel_surface.blit(title_surface, title_rect)

            # Ligne sous le titre
            pygame.draw.line(
                panel_surface,
                self.border_color,
                (20, title_rect.bottom + 5),
                (self.rect.width - 20, title_rect.bottom + 5),
                1
            )

            content_start_y = title_rect.bottom + 15
        else:
            content_start_y = 10

        # Dessiner le contenu avec défilement
        y_pos = content_start_y - self.scroll_position
        max_y = 0

        for item in self.content:
            item_type = item["type"]

            if y_pos + 30 >= 0 and y_pos <= self.rect.height:  # Ne dessiner que les éléments visibles
                if item_type == "text":
                    if item["text"]:  # Vérifier que le texte n'est pas vide
                        text_surface = self.text_font.render(item["text"], True, item["color"])
                        panel_surface.blit(text_surface, (20, y_pos))
                    y_pos += 25

                elif item_type == "separator":
                    pygame.draw.line(
                        panel_surface,
                        item["color"],
                        (20, y_pos + 5),
                        (self.rect.width - 20, y_pos + 5),
                        1
                    )
                    y_pos += 15

                elif item_type == "progress_bar":
                    # Étiquette
                    label_surface = self.text_font.render(item["label"], True, (200, 200, 200))
                    panel_surface.blit(label_surface, (20, y_pos))

                    # Barre de progression
                    bar_width = self.rect.width - 50
                    bar_height = 10
                    bar_x = 25
                    bar_y = y_pos + 20

                    # Fond de la barre
                    pygame.draw.rect(
                        panel_surface,
                        (60, 60, 60),
                        (bar_x, bar_y, bar_width, bar_height)
                    )

                    # Barre de progression
                    progress_width = int(bar_width * item["value"])
                    if progress_width > 0:
                        pygame.draw.rect(
                            panel_surface,
                            item["color"],
                            (bar_x, bar_y, progress_width, bar_height)
                        )

                    # Bordure
                    pygame.draw.rect(
                        panel_surface,
                        (100, 100, 100),
                        (bar_x, bar_y, bar_width, bar_height),
                        1
                    )

                    # Pourcentage
                    percent_text = f"{int(item['value'] * 100)}%"
                    percent_surface = self.text_font.render(percent_text, True, (220, 220, 220))
                    percent_rect = percent_surface.get_rect(midright=(bar_x + bar_width + 20, bar_y + bar_height // 2))
                    panel_surface.blit(percent_surface, percent_rect)

                    y_pos += 40

                elif item_type == "chart":
                    chart_height = 100
                    chart_width = self.rect.width - 50
                    chart_x = 25
                    chart_y = y_pos + 20

                    # Titre du graphique
                    if item.get("title"):
                        title_surface = self.text_font.render(item["title"], True, (220, 220, 220))
                        title_rect = title_surface.get_rect(midtop=(chart_x + chart_width // 2, y_pos))
                        panel_surface.blit(title_surface, title_rect)

                    # Fond du graphique
                    pygame.draw.rect(
                        panel_surface,
                        (40, 40, 50),
                        (chart_x, chart_y, chart_width, chart_height)
                    )

                    # Dessiner les barres ou lignes
                    data = item["data"]
                    if data:
                        max_value = max(data)
                        if max_value > 0:
                            bar_width = chart_width / len(data)
                            for i, value in enumerate(data):
                                bar_height = (value / max_value) * chart_height
                                bar_x = chart_x + i * bar_width
                                bar_y = chart_y + chart_height - bar_height

                                pygame.draw.rect(
                                    panel_surface,
                                    item["color_map"][i % len(item["color_map"])],
                                    (bar_x, bar_y, bar_width - 2, bar_height)
                                )

                    # Bordure
                    pygame.draw.rect(
                        panel_surface,
                        (100, 100, 120),
                        (chart_x, chart_y, chart_width, chart_height),
                        1
                    )

                    y_pos += chart_height + 40
            else:
                # Estimer la hauteur des éléments non visibles
                if item_type == "text":
                    y_pos += 25
                elif item_type == "separator":
                    y_pos += 15
                elif item_type == "progress_bar":
                    y_pos += 40
                elif item_type == "chart":
                    y_pos += 140  # Hauteur estimée du graphique

            max_y = y_pos

        # Calculer la hauteur maximale de défilement
        self.max_scroll = max(0, max_y - self.rect.height + 20)

        # Dessiner la barre de défilement si nécessaire
        if self.max_scroll > 0:
            scrollbar_rect = self._get_scrollbar_rect()
            scrollbar_rect.x -= self.rect.x  # Ajuster pour la surface du panneau
            scrollbar_rect.y -= self.rect.y

            # Fond de la barre de défilement
            pygame.draw.rect(
                panel_surface,
                (60, 60, 70),
                (self.rect.width - self.scrollbar_width - 2, 0, self.scrollbar_width, self.rect.height)
            )

            # Barre de défilement
            pygame.draw.rect(
                panel_surface,
                (120, 120, 150),
                scrollbar_rect
            )

        # Afficher le panneau
        surface.blit(panel_surface, self.rect)


class EvolutionStatsPanel:
    """Panneau de visualisation des statistiques d'évolution."""
    def __init__(self, x, y, width, height):
        self.panel = Panel(x, y, width, height, "Statistiques d'Évolution", alpha=230)
        self.visible = False
        self.world = None
        self.update_interval = 2.0  # Secondes entre les mises à jour
        self.last_update = 0

        # Données pour les graphiques
        self.population_history = []
        self.species_history = []
        self.adaptation_history = []
        self.max_history_points = 50

        # Couleurs pour les différents types d'organismes
        self.organism_colors = {
            OrganismType.UNICELLULAR: (100, 200, 255),
            OrganismType.PLANT: (50, 180, 50),
            OrganismType.HERBIVORE: (200, 180, 50),
            OrganismType.CARNIVORE: (200, 50, 50),
            OrganismType.OMNIVORE: (180, 100, 180)
        }

    def toggle(self):
        """Affiche ou masque le panneau de statistiques."""
        self.visible = not self.visible

    def set_world(self, world):
        """Définit le monde à analyser."""
        self.world = world
        self.reset_data()

    def reset_data(self):
        """Réinitialise les données historiques."""
        self.population_history = []
        self.species_history = []
        self.adaptation_history = []
        self.last_update = 0

    def update(self, delta_time):
        """Met à jour les statistiques d'évolution."""
        if not self.visible or not self.world:
            return

        self.last_update += delta_time
        if self.last_update < self.update_interval:
            return

        self.last_update = 0

        # Collecter les données actuelles
        if hasattr(self.world, 'species_stats'):
            # Population par type d'organisme
            population_data = [
                self.world.species_stats.get(OrganismType.UNICELLULAR, 0),
                self.world.species_stats.get(OrganismType.PLANT, 0),
                self.world.species_stats.get(OrganismType.HERBIVORE, 0),
                self.world.species_stats.get(OrganismType.CARNIVORE, 0),
                self.world.species_stats.get(OrganismType.OMNIVORE, 0)
            ]
            self.population_history.append(population_data)

            # Nombre d'espèces
            if hasattr(self.world, 'species_registry'):
                active_species = sum(1 for data in self.world.species_registry.values()
                                    if not data.get('is_extinct', False) and data.get('count', 0) > 0)
                extinct_species = self.world.extinction_count if hasattr(self.world, 'extinction_count') else 0
                self.species_history.append((active_species, extinct_species))

            # Adaptation moyenne
            if hasattr(self.world, 'adaptation_by_biome'):
                avg_adaptation = sum(self.world.adaptation_by_biome.values()) / max(1, len(self.world.adaptation_by_biome))
                self.adaptation_history.append(avg_adaptation)

        # Limiter la taille des historiques
        if len(self.population_history) > self.max_history_points:
            self.population_history = self.population_history[-self.max_history_points:]
        if len(self.species_history) > self.max_history_points:
            self.species_history = self.species_history[-self.max_history_points:]
        if len(self.adaptation_history) > self.max_history_points:
            self.adaptation_history = self.adaptation_history[-self.max_history_points:]

        # Mettre à jour le contenu du panneau
        self._update_panel_content()

    def _update_panel_content(self):
        """Met à jour le contenu du panneau avec les données actuelles."""
        if not self.world:
            return

        # Vider le panneau
        self.panel.content = []

        # Informations générales
        self.panel.add_text("Informations générales", (220, 220, 255))
        self.panel.add_separator()

        # Année et génération
        if hasattr(self.world, 'year'):
            self.panel.add_text(f"Année: {self.world.year}", (200, 200, 200))
        if hasattr(self.world, 'max_generation'):
            self.panel.add_text(f"Génération max: {self.world.max_generation}", (200, 200, 200))

        # Événements évolutifs
        if hasattr(self.world, 'speciation_events'):
            self.panel.add_text(f"Événements de spéciation: {self.world.speciation_events}", (180, 220, 180))
        if hasattr(self.world, 'extinction_count'):
            self.panel.add_text(f"Espèces éteintes: {self.world.extinction_count}", (220, 180, 180))

        self.panel.add_separator()

        # Population actuelle
        self.panel.add_text("Population actuelle", (220, 220, 255))

        if hasattr(self.world, 'species_stats'):
            total_population = sum(self.world.species_stats.values())
            self.panel.add_text(f"Population totale: {total_population}", (200, 200, 200))

            # Répartition par type d'organisme
            for org_type in OrganismType:
                count = self.world.species_stats.get(org_type, 0)
                if count > 0:
                    percentage = count / max(1, total_population) * 100
                    self.panel.add_progress_bar(
                        f"{org_type.name}: {count}",
                        count / max(1, total_population),
                        self.organism_colors.get(org_type, (150, 150, 150))
                    )

        self.panel.add_separator()

        # Graphique d'évolution de la population
        if self.population_history:
            # Préparer les données pour le graphique
            data_points = []
            for i in range(len(self.population_history[0])):
                data_points.append([history[i] for history in self.population_history])

            # Ajouter un graphique pour chaque type d'organisme
            self.panel.add_text("Évolution de la population", (220, 220, 255))

            # Graphique combiné
            combined_data = [sum(point) for point in zip(*data_points)]
            self.panel.add_chart(
                combined_data,
                title="Population totale",
                color_map=[(150, 150, 220)]
            )

            # Graphiques individuels
            for i, org_type in enumerate(OrganismType):
                if i < len(data_points) and max(data_points[i]) > 0:
                    self.panel.add_chart(
                        data_points[i],
                        title=f"Population {org_type.name}",
                        color_map=[self.organism_colors.get(org_type, (150, 150, 150))]
                    )

        self.panel.add_separator()

        # Graphique d'évolution des espèces
        if self.species_history:
            self.panel.add_text("Évolution des espèces", (220, 220, 255))

            active_species = [history[0] for history in self.species_history]
            extinct_species = [history[1] for history in self.species_history]

            self.panel.add_chart(
                active_species,
                title="Espèces actives",
                color_map=[(100, 200, 100)]
            )

            self.panel.add_chart(
                extinct_species,
                title="Espèces éteintes (cumulatif)",
                color_map=[(200, 100, 100)]
            )

        self.panel.add_separator()

        # Graphique d'adaptation
        if self.adaptation_history:
            self.panel.add_text("Adaptation moyenne", (220, 220, 255))

            self.panel.add_chart(
                self.adaptation_history,
                title="Adaptation moyenne des organismes",
                color_map=[(100, 180, 220)]
            )

            # Adaptation par biome
            if hasattr(self.world, 'adaptation_by_biome') and self.world.adaptation_by_biome:
                self.panel.add_text("Adaptation par biome", (200, 200, 200))

                for biome_type, adaptation in sorted(
                    self.world.adaptation_by_biome.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]:  # Top 5 des biomes
                    self.panel.add_progress_bar(
                        f"{biome_type.name}",
                        adaptation,
                        (100 + int(adaptation * 100), 150, 200)
                    )

        self.panel.add_separator()

        # Espèces dominantes
        if hasattr(self.world, 'dominant_species') and self.world.dominant_species:
            self.panel.add_text("Espèces dominantes", (220, 220, 255))

            for org_type, species_id in self.world.dominant_species.items():
                if species_id in self.world.species_registry:
                    species_data = self.world.species_registry[species_id]
                    species_name = species_data.get('name', 'Espèce inconnue')
                    species_count = species_data.get('count', 0)
                    species_gen = species_data.get('generation', 0)

                    self.panel.add_text(f"{org_type.name}: {species_name}", self.organism_colors.get(org_type, (150, 150, 150)))
                    self.panel.add_text(f"  Population: {species_count}, Génération: {species_gen}", (180, 180, 180))

    def handle_event(self, event):
        """Gère les événements pour le panneau de statistiques."""
        if self.visible:
            self.panel.handle_event(event)

    def draw(self, surface):
        """Dessine le panneau de statistiques."""
        if self.visible:
            self.panel.draw(surface)


class GenomeViewerPanel:
    """Panneau de visualisation du génome d'un organisme."""
    def __init__(self, x, y, width, height):
        self.panel = Panel(x, y, width, height, "Visualisation du Génome", alpha=230)
        self.visible = False
        self.organism = None

        # Couleurs pour les différents types de gènes
        self.gene_colors = {
            "metabolism": (100, 200, 100),
            "speed": (100, 100, 200),
            "strength": (200, 100, 100),
            "vision": (200, 200, 100),
            "immunity": (200, 100, 200),
            "learning": (100, 200, 200),
            "default": (150, 150, 150)
        }

    def toggle(self):
        """Affiche ou masque le panneau de visualisation du génome."""
        self.visible = not self.visible

    def set_organism(self, organism):
        """Définit l'organisme à analyser."""
        self.organism = organism
        self._update_panel_content()

    def _update_panel_content(self):
        """Met à jour le contenu du panneau avec les données du génome actuel."""
        if not self.organism:
            return

        # Vider le panneau
        self.panel.content = []

        # Informations générales sur l'organisme
        self.panel.add_text(f"Organisme: {self.organism.id[:8]}", (220, 220, 255))
        self.panel.add_text(f"Type: {self.organism.organism_type.name}", (200, 200, 200))

        # Informations taxonomiques
        self.panel.add_text("Classification taxonomique:", (220, 220, 255))
        self.panel.add_text(f"Nom scientifique: {self.organism.scientific_name}", (200, 200, 200))
        self.panel.add_text(f"Nom commun: {self.organism.common_name}", (200, 200, 200))

        # Afficher la taxonomie complète si disponible
        if hasattr(self.organism, 'taxonomy_id') and self.organism.taxonomy_id:
            taxonomy = Taxonomy.get_full_taxonomy(self.organism.taxonomy_id)
            self.panel.add_text(f"Domaine: {taxonomy.get('DOMAIN', 'Inconnu')}", (180, 180, 180))
            self.panel.add_text(f"Règne: {taxonomy.get('KINGDOM', 'Inconnu')}", (180, 180, 180))
            self.panel.add_text(f"Embranchement: {taxonomy.get('PHYLUM', 'Inconnu')}", (180, 180, 180))

        self.panel.add_text(f"Espèce ID: {self.organism.species_id[:8]}", (180, 180, 180))
        self.panel.add_text(f"Génération: {self.organism.generation}", (200, 200, 200))

        self.panel.add_separator()

        # Statistiques vitales
        self.panel.add_text("Statistiques vitales", (220, 220, 255))
        self.panel.add_progress_bar("Santé", self.organism.health / 100, (100, 200, 100))
        self.panel.add_progress_bar("Énergie", self.organism.energy / 100, (100, 100, 200))
        self.panel.add_progress_bar("Âge", self.organism.age / max(1, self.organism.phenotype.lifespan), (200, 150, 100))

        self.panel.add_separator()

        # Phénotype
        self.panel.add_text("Phénotype", (220, 220, 255))

        # Traits principaux
        traits = [
            ("Taille", self.organism.phenotype.size, (150, 150, 200)),
            ("Vitesse", self.organism.phenotype.max_speed / 10, (100, 150, 200)),
            ("Force", self.organism.phenotype.strength, (200, 100, 100)),
            ("Métabolisme", self.organism.phenotype.metabolism_rate, (100, 200, 100)),
            ("Vision", self.organism.phenotype.vision_range / 50, (200, 200, 100)),
            ("Immunité", self.organism.phenotype.immune_system, (200, 100, 200))
        ]

        for name, value, color in traits:
            self.panel.add_progress_bar(name, min(1.0, value), color)

        self.panel.add_separator()

        # Génome
        self.panel.add_text("Structure du génome", (220, 220, 255))
        self.panel.add_text(f"Chromosomes: {len(self.organism.genome.chromosomes)}", (200, 200, 200))

        # Compter les gènes
        gene_count = sum(len(chrom.genes) for chrom in self.organism.genome.chromosomes)
        self.panel.add_text(f"Gènes: {gene_count}", (200, 200, 200))

        # Analyse des gènes par catégorie
        gene_categories = {}
        mutation_rates = []

        for chrom in self.organism.genome.chromosomes:
            for gene_id, gene in chrom.genes.items():
                # Catégoriser les gènes
                category = "default"
                for key in self.gene_colors.keys():
                    if key in gene_id:
                        category = key
                        break

                gene_categories[category] = gene_categories.get(category, 0) + 1
                mutation_rates.append(gene.mutation_rate)

        # Afficher la répartition des gènes
        if gene_categories:
            self.panel.add_text("Répartition des gènes", (200, 200, 200))

            for category, count in sorted(gene_categories.items(), key=lambda x: x[1], reverse=True):
                if category in self.gene_colors:
                    color = self.gene_colors[category]
                else:
                    color = self.gene_colors["default"]

                self.panel.add_progress_bar(
                    f"{category.capitalize()}: {count}",
                    count / gene_count,
                    color
                )

        # Taux de mutation moyen
        if mutation_rates:
            avg_mutation = sum(mutation_rates) / len(mutation_rates)
            self.panel.add_text(f"Taux de mutation moyen: {avg_mutation:.4f}", (200, 200, 200))

        self.panel.add_separator()

        # Adaptation
        self.panel.add_text("Adaptation", (220, 220, 255))
        self.panel.add_progress_bar("Score d'adaptation", self.organism.adaptation_score, (100, 180, 220))

        # Historique des mutations
        if hasattr(self.organism, 'mutation_history') and self.organism.mutation_history:
            self.panel.add_text("Mutations récentes", (220, 220, 255))

            for mutation in self.organism.mutation_history[-5:]:  # 5 dernières mutations
                self.panel.add_text(f"- {mutation}", (180, 180, 180))

    def handle_event(self, event):
        """Gère les événements pour le panneau de visualisation du génome."""
        if self.visible:
            self.panel.handle_event(event)

    def draw(self, surface):
        """Dessine le panneau de visualisation du génome."""
        if self.visible:
            self.panel.draw(surface)


class BiomesListPanel:
    """Panneau listant les différents biomes présents dans le jeu."""
    def __init__(self, x, y, width, height):
        self.panel = Panel(x, y, width, height, "Biomes du Monde", alpha=230)
        self.visible = False
        self.world = None

        # Couleurs associées aux biomes
        self.biome_colors = {
            BiomeType.OCEAN: (0, 50, 200),
            BiomeType.DEEP_OCEAN: (0, 30, 150),
            BiomeType.SHALLOW_WATER: (50, 100, 220),
            BiomeType.CORAL_REEF: (100, 200, 255),
            BiomeType.BEACH: (240, 220, 130),
            BiomeType.GRASSLAND: (100, 200, 100),
            BiomeType.SAVANNA: (200, 200, 100),
            BiomeType.FOREST: (30, 150, 50),
            BiomeType.RAINFOREST: (20, 120, 20),
            BiomeType.SWAMP: (70, 100, 70),
            BiomeType.MOUNTAIN: (150, 150, 150),
            BiomeType.MOUNTAIN_FOREST: (100, 150, 100),
            BiomeType.DESERT: (240, 200, 100),
            BiomeType.DESERT_HILLS: (200, 170, 80),
            BiomeType.TUNDRA: (200, 200, 220),
            BiomeType.ICE: (220, 240, 255),
            BiomeType.VOLCANIC: (150, 50, 50),
            BiomeType.RIVER: (50, 150, 255),
            BiomeType.LAKE: (100, 150, 255)
        }

        # Descriptions des biomes
        self.biome_descriptions = {
            BiomeType.OCEAN: "Vastes étendues d'eau salée profondes",
            BiomeType.DEEP_OCEAN: "Zones océaniques très profondes et sombres",
            BiomeType.SHALLOW_WATER: "Eaux peu profondes près des côtes",
            BiomeType.CORAL_REEF: "Écosystèmes marins riches en biodiversité",
            BiomeType.BEACH: "Zones côtières sablonneuses",
            BiomeType.GRASSLAND: "Plaines herbeuses avec peu d'arbres",
            BiomeType.SAVANNA: "Prairies avec arbres épars et saison sèche marquée",
            BiomeType.FOREST: "Zones boisées à feuilles caduques",
            BiomeType.RAINFOREST: "Forêts denses et humides à forte biodiversité",
            BiomeType.SWAMP: "Zones humides et marécageuses",
            BiomeType.MOUNTAIN: "Terrains élevés et rocheux",
            BiomeType.MOUNTAIN_FOREST: "Forêts situées en altitude",
            BiomeType.DESERT: "Zones arides avec peu de précipitations",
            BiomeType.DESERT_HILLS: "Déserts avec relief accidenté",
            BiomeType.TUNDRA: "Plaines froides avec végétation basse",
            BiomeType.ICE: "Zones gelées en permanence",
            BiomeType.VOLCANIC: "Régions avec activité volcanique",
            BiomeType.RIVER: "Cours d'eau douce",
            BiomeType.LAKE: "Étendues d'eau douce entourées de terre"
        }

    def toggle(self):
        """Affiche ou masque le panneau de liste des biomes."""
        self.visible = not self.visible
        if self.visible:
            self._update_panel_content()

    def set_world(self, world):
        """Définit le monde à analyser."""
        self.world = world
        self._update_panel_content()

    def _update_panel_content(self):
        """Met à jour le contenu du panneau avec les données du monde."""
        if not self.world:
            return

        # Vider le panneau
        self.panel.content = []

        # Titre
        self.panel.add_text("Biomes présents dans le monde", (220, 220, 255))
        self.panel.add_separator()

        # Créer une liste statique des biomes pour le moment
        # Puisque nous ne pouvons pas accéder directement aux cellules du monde
        biome_list = [
            (BiomeType.OCEAN, "Océans et mers profondes"),
            (BiomeType.FOREST, "Forêts tempérées"),
            (BiomeType.GRASSLAND, "Prairies et plaines"),
            (BiomeType.MOUNTAIN, "Montagnes"),
            (BiomeType.DESERT, "Déserts"),
            (BiomeType.TUNDRA, "Toundra arctique"),
            (BiomeType.LAKE, "Lacs d'eau douce"),
            (BiomeType.RIVER, "Rivières et fleuves"),
            (BiomeType.BEACH, "Plages et côtes"),
            (BiomeType.SWAMP, "Marécages")
        ]

        # Afficher les informations sur chaque biome
        self.panel.add_text("Types de biomes dans ce monde:", (200, 200, 200))
        self.panel.add_separator()

        for biome_type, description in biome_list:
            # Obtenir la couleur du biome
            color = self.biome_colors.get(biome_type, (150, 150, 150))

            # Ajouter le nom du biome
            self.panel.add_text(f"{biome_type.name}", color)

            # Ajouter une description
            self.panel.add_text(f"  {description}", (180, 180, 180))

            # Ajouter un séparateur entre les biomes
            self.panel.add_separator()

        # Ajouter des informations générales sur les biomes
        self.panel.add_text("Informations sur les biomes", (220, 220, 255))
        self.panel.add_text("Les biomes sont des écosystèmes caractérisés", (200, 200, 200))
        self.panel.add_text("par leur climat, leur flore et leur faune.", (200, 200, 200))
        self.panel.add_text("Chaque biome offre des ressources différentes", (200, 200, 200))
        self.panel.add_text("et influence l'évolution des organismes.", (200, 200, 200))

        # Ajouter des statistiques sur les organismes par biome si disponibles
        if hasattr(self.world, 'adaptation_by_biome') and self.world.adaptation_by_biome:
            self.panel.add_separator()
            self.panel.add_text("Adaptation des organismes par biome:", (220, 220, 255))

            for biome_type, adaptation in sorted(self.world.adaptation_by_biome.items(),
                                               key=lambda x: x[1], reverse=True):
                # Obtenir la couleur du biome
                color = self.biome_colors.get(biome_type, (150, 150, 150))

                # Ajouter le niveau d'adaptation pour ce biome
                self.panel.add_text(f"{biome_type.name}: {adaptation:.2f}", color)

                # Ajouter une barre de progression pour visualiser l'adaptation
                self.panel.add_progress_bar("", adaptation, color)

        # Ajouter des statistiques sur les populations d'organismes
        if hasattr(self.world, 'species_stats') and self.world.species_stats:
            self.panel.add_separator()
            self.panel.add_text("Population par type d'organisme:", (220, 220, 255))

            total_organisms = sum(self.world.species_stats.values())

            for org_type, count in sorted(self.world.species_stats.items(),
                                        key=lambda x: x[1], reverse=True):
                # Définir une couleur pour chaque type d'organisme
                if org_type == OrganismType.PLANT:
                    color = (0, 200, 0)  # Vert
                elif org_type == OrganismType.HERBIVORE:
                    color = (200, 200, 0)  # Jaune
                elif org_type == OrganismType.CARNIVORE:
                    color = (200, 0, 0)  # Rouge
                elif org_type == OrganismType.OMNIVORE:
                    color = (200, 0, 200)  # Magenta
                else:  # UNICELLULAR
                    color = (0, 150, 200)  # Bleu clair

                # Calculer le pourcentage
                percentage = (count / total_organisms) * 100 if total_organisms > 0 else 0

                # Ajouter les informations sur la population
                self.panel.add_text(f"{org_type.name}: {count} ({percentage:.1f}%)", color)

                # Ajouter une barre de progression
                self.panel.add_progress_bar("", percentage/100, color)

    def handle_event(self, event):
        """Gère les événements pour le panneau de liste des biomes."""
        if self.visible:
            self.panel.handle_event(event)

    def draw(self, surface):
        """Dessine le panneau de liste des biomes."""
        if self.visible:
            self.panel.draw(surface)


class SettingsMenu:
    """Menu des paramètres du jeu permettant de personnaliser les contrôles."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Fond
        self.background_color = (20, 30, 50)

        # Titre
        self.title = "Paramètres"

        # Liste des contrôles à configurer
        self.controls_list = [
            {"name": "Déplacer à gauche", "key": "move_left", "value": CONTROLS.move_left},
            {"name": "Déplacer à droite", "key": "move_right", "value": CONTROLS.move_right},
            {"name": "Déplacer en haut", "key": "move_up", "value": CONTROLS.move_up},
            {"name": "Déplacer en bas", "key": "move_down", "value": CONTROLS.move_down},
            {"name": "Zoom avant", "key": "zoom_in", "value": CONTROLS.zoom_in},
            {"name": "Zoom arrière", "key": "zoom_out", "value": CONTROLS.zoom_out},
            {"name": "Pause", "key": "pause", "value": CONTROLS.pause},
            {"name": "Centrer la carte", "key": "center_map", "value": CONTROLS.center_map},
            {"name": "Suivre l'organisme", "key": "follow_organism", "value": CONTROLS.follow_organism},
            {"name": "Capture d'écran", "key": "take_screenshot", "value": CONTROLS.take_screenshot}
        ]

        # Contrôle actuellement en cours de configuration
        self.selected_control = None

        # Boutons
        button_width = 200
        button_height = 50

        self.save_button = Button(
            SCREEN_WIDTH // 2 - button_width - 20, SCREEN_HEIGHT - 100,
            button_width, button_height,
            "Sauvegarder", (0, 120, 60), (0, 180, 90),
            border_radius=10, font_size=28
        )

        self.cancel_button = Button(
            SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 100,
            button_width, button_height,
            "Annuler", (150, 30, 30), (200, 60, 60),
            border_radius=10, font_size=28
        )

    def run(self):
        """Exécute le menu des paramètres."""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.KEYDOWN:
                    if self.selected_control is not None:
                        # Enregistrer la nouvelle touche
                        control_key = self.controls_list[self.selected_control]["key"]
                        setattr(CONTROLS, control_key, event.key)
                        self.controls_list[self.selected_control]["value"] = event.key
                        self.selected_control = None
                    elif event.key == pygame.K_ESCAPE:
                        return "main_menu"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        # Vérifier si un bouton a été cliqué
                        if self.save_button.is_clicked(mouse_pos, True):
                            self.save_controls()
                            return "main_menu"

                        elif self.cancel_button.is_clicked(mouse_pos, True):
                            return "main_menu"

                        # Vérifier si un contrôle a été cliqué
                        for i, control in enumerate(self.controls_list):
                            control_rect = pygame.Rect(
                                SCREEN_WIDTH // 2 - 150, 150 + i * 40,
                                300, 30
                            )
                            if control_rect.collidepoint(mouse_pos):
                                self.selected_control = i
                                break

            # Mise à jour des boutons
            self.save_button.update(mouse_pos)
            self.cancel_button.update(mouse_pos)

            # Dessin
            self.draw()

            # Mise à jour de l'affichage
            pygame.display.flip()
            self.clock.tick(FPS)

        return "main_menu"

    def draw(self):
        """Dessine l'interface du menu des paramètres."""
        # Fond
        self.screen.fill(self.background_color)

        # Titre
        title_text = self.font.render(self.title, True, (220, 220, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_text, title_rect)

        # Sous-titre
        subtitle_text = self.small_font.render("Cliquez sur un contrôle pour le modifier", True, (180, 180, 220))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Liste des contrôles
        for i, control in enumerate(self.controls_list):
            # Rectangle de fond pour le contrôle sélectionné
            control_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 250, 150 + i * 40,
                500, 30
            )

            # Mise en évidence du contrôle sélectionné
            if self.selected_control == i:
                pygame.draw.rect(self.screen, (60, 80, 120), control_rect)
                status_text = self.small_font.render("Appuyez sur une touche...", True, (255, 255, 100))
            else:
                # Nom du contrôle
                pygame.draw.rect(self.screen, (40, 50, 80), control_rect, 0, 5)

            # Nom du contrôle
            name_text = self.small_font.render(control["name"], True, (220, 220, 220))
            name_rect = name_text.get_rect(midleft=(SCREEN_WIDTH // 2 - 240, 150 + i * 40 + 15))
            self.screen.blit(name_text, name_rect)

            # Valeur du contrôle (nom de la touche)
            key_name = pygame.key.name(control["value"]).upper()
            key_text = self.small_font.render(key_name, True, (180, 220, 255))
            key_rect = key_text.get_rect(midright=(SCREEN_WIDTH // 2 + 240, 150 + i * 40 + 15))
            self.screen.blit(key_text, key_rect)

            # Afficher le message pour le contrôle sélectionné
            if self.selected_control == i:
                self.screen.blit(status_text, status_text.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 40 + 15)))

        # Boutons
        self.save_button.draw(self.screen)
        self.cancel_button.draw(self.screen)

    def save_controls(self):
        """Sauvegarde les contrôles personnalisés."""
        # Mettre à jour les contrôles
        for control in self.controls_list:
            setattr(CONTROLS, control["key"], control["value"])

        # Sauvegarder dans un fichier
        CONTROLS.save_to_file()

class MainMenu:
    """Menu principal du jeu avec une interface améliorée."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 48)

        # Chargement des ressources graphiques
        self.background_color = (15, 15, 35)
        self.accent_color = (50, 120, 200)

        # Animation de fond
        self.particles = []
        self.create_particles(100)  # Créer des particules pour l'animation de fond

        # Dimensions des boutons
        button_width = 320
        button_height = 60
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        # Espacement vertical
        button_start_y = 220
        button_spacing = 80

        # Création des boutons avec un style amélioré
        self.new_game_button = Button(
            button_x, button_start_y,
            button_width, button_height,
            "Nouvelle Simulation",
            (0, 120, 60), (0, 180, 90),
            border_radius=15, font_size=32
        )

        self.create_world_button = Button(
            button_x, button_start_y + button_spacing,
            button_width, button_height,
            "Créer un Monde Personnalisé",
            (30, 80, 150), (40, 120, 200),
            border_radius=15, font_size=32
        )

        self.scenarios_button = Button(
            button_x, button_start_y + button_spacing * 2,
            button_width, button_height,
            "Scénarios Évolutifs",
            (150, 80, 30), (200, 120, 40),
            border_radius=15, font_size=32
        )

        self.load_world_button = Button(
            button_x, button_start_y + button_spacing * 3,
            button_width, button_height,
            "Charger une Simulation",
            (100, 50, 120), (150, 75, 180),
            border_radius=15, font_size=32
        )

        self.settings_button = Button(
            button_x, button_start_y + button_spacing * 4,
            button_width, button_height,
            "Paramètres",
            (80, 80, 80), (120, 120, 120),
            border_radius=15, font_size=32
        )

        self.quit_button = Button(
            button_x, button_start_y + button_spacing * 5,
            button_width, button_height,
            "Quitter",
            (150, 30, 30), (200, 50, 50),
            border_radius=15, font_size=32
        )

        # Boutons d'information
        info_button_size = 40
        self.info_button = Button(
            SCREEN_WIDTH - info_button_size - 20, 20,
            info_button_size, info_button_size,
            "?", (50, 50, 100), (80, 80, 150),
            border_radius=20, font_size=24
        )

        # État pour l'affichage des informations
        self.show_info = False

        # Texte d'information
        self.info_text = [
            "BioEvolve est un simulateur d'évolution biologique réaliste",
            "qui modélise les processus évolutifs fondamentaux:",
            "",
            "• Sélection naturelle et adaptation",
            "• Mutations génétiques et dérive génétique",
            "• Spéciation et diversification",
            "• Interactions écologiques et coévolution",
            "",
            "Observez comment les organismes s'adaptent à leur environnement",
            "et évoluent au fil du temps pour former de nouvelles espèces."
        ]

    def create_particles(self, count):
        """Crée des particules pour l'animation de fond."""
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.uniform(1, 3)
            speed = random.uniform(0.2, 1.0)
            color = (
                random.randint(30, 70),
                random.randint(50, 100),
                random.randint(100, 200)
            )
            self.particles.append({
                'pos': [x, y],
                'size': size,
                'speed': speed,
                'color': color,
                'angle': random.uniform(0, 2 * math.pi)
            })

    def update_particles(self):
        """Met à jour les particules pour l'animation de fond."""
        for particle in self.particles:
            # Mouvement sinusoïdal
            particle['angle'] += 0.01
            particle['pos'][0] += math.sin(particle['angle']) * 0.5
            particle['pos'][1] -= particle['speed']

            # Réinitialiser les particules qui sortent de l'écran
            if particle['pos'][1] < -10:
                particle['pos'][1] = SCREEN_HEIGHT + 10
                particle['pos'][0] = random.randint(0, SCREEN_WIDTH)

    def run(self):
        """Exécute le menu principal avec animations et effets visuels."""
        # Animation d'entrée
        fade_alpha = 255
        fade_speed = 5

        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        mouse_click = True

            # Animation de fondu en entrée
            if fade_alpha > 0:
                fade_alpha = max(0, fade_alpha - fade_speed)

            # Mise à jour des particules
            self.update_particles()

            # Mise à jour des boutons avec effets de survol
            self.new_game_button.update(mouse_pos)
            self.create_world_button.update(mouse_pos)
            self.scenarios_button.update(mouse_pos)
            self.load_world_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)
            self.info_button.update(mouse_pos)

            # Vérification des clics avec effets sonores
            if self.new_game_button.is_clicked(mouse_pos, mouse_click):
                # Effet de transition
                self.transition_effect()
                return "new_game"

            if self.create_world_button.is_clicked(mouse_pos, mouse_click):
                self.transition_effect()
                return "create_world"

            if self.scenarios_button.is_clicked(mouse_pos, mouse_click):
                self.transition_effect()
                return "scenarios"

            if self.load_world_button.is_clicked(mouse_pos, mouse_click):
                self.transition_effect()
                return "load_world"

            if self.settings_button.is_clicked(mouse_pos, mouse_click):
                self.transition_effect()
                return "settings"

            if self.quit_button.is_clicked(mouse_pos, mouse_click):
                self.transition_effect()
                self.running = False
                return "quit"

            if self.info_button.is_clicked(mouse_pos, mouse_click):
                self.show_info = not self.show_info

            # Dessin de l'interface avec effets visuels
            self.draw()

            # Superposition du fondu
            if fade_alpha > 0:
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(fade_alpha)
                self.screen.blit(fade_surface, (0, 0))

            # Mise à jour de l'affichage
            pygame.display.flip()
            self.clock.tick(60)

        return "quit"

    def transition_effect(self):
        """Effet de transition lors du clic sur un bouton."""
        for alpha in range(0, 256, 10):
            self.draw()
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(5)

    def draw(self):
        """Dessine le menu principal avec des effets visuels améliorés."""
        # Fond avec dégradé
        self.screen.fill(self.background_color)

        # Dessin des particules
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['pos'][0]), int(particle['pos'][1])),
                particle['size']
            )

        # Logo et titre avec effet de lueur
        title_font = pygame.font.SysFont(None, 72)
        title_shadow = title_font.render("BioEvolve", True, (30, 100, 180))
        title_text = title_font.render("BioEvolve", True, (100, 200, 255))

        # Animation du titre
        title_offset = math.sin(pygame.time.get_ticks() / 1000) * 3

        # Ombre du titre
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 100 + 2))
        self.screen.blit(title_shadow, shadow_rect)

        # Titre principal
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100 + title_offset))
        self.screen.blit(title_text, title_rect)

        # Sous-titre avec style
        subtitle_font = pygame.font.SysFont(None, 28)
        subtitle_text = subtitle_font.render("Simulateur d'Évolution Biologique", True, (180, 220, 255))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Ligne décorative
        line_width = 400
        pygame.draw.line(
            self.screen,
            (80, 120, 200),
            (SCREEN_WIDTH // 2 - line_width // 2, 190),
            (SCREEN_WIDTH // 2 + line_width // 2, 190),
            2
        )

        # Dessiner les boutons avec effets
        self.new_game_button.draw(self.screen)
        self.create_world_button.draw(self.screen)
        self.scenarios_button.draw(self.screen)
        self.load_world_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.quit_button.draw(self.screen)
        self.info_button.draw(self.screen)

        # Affichage du panneau d'information si activé
        if self.show_info:
            self.draw_info_panel()

        # Version avec style
        version_font = pygame.font.SysFont(None, 20)
        version_text = version_font.render("Version 2.0 - Évolution Réaliste", True, (150, 180, 220))
        version_rect = version_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(version_text, version_rect)

        # Copyright
        copyright_text = version_font.render("© 2025 BioEvolve Team", True, (120, 120, 150))
        copyright_rect = copyright_text.get_rect(bottomleft=(20, SCREEN_HEIGHT - 20))
        self.screen.blit(copyright_text, copyright_rect)

    def draw_info_panel(self):
        """Affiche un panneau d'information sur le jeu."""
        # Fond semi-transparent
        info_surface = pygame.Surface((SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200))
        info_surface.fill((30, 40, 80))
        info_surface.set_alpha(230)

        # Position du panneau
        panel_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(info_surface, panel_rect)

        # Bordure
        pygame.draw.rect(self.screen, (100, 150, 200), panel_rect, 2, border_radius=10)

        # Titre du panneau
        info_title_font = pygame.font.SysFont(None, 36)
        info_title = info_title_font.render("À propos de BioEvolve", True, (200, 220, 255))
        info_title_rect = info_title.get_rect(midtop=(SCREEN_WIDTH // 2, panel_rect.top + 20))
        self.screen.blit(info_title, info_title_rect)

        # Contenu
        info_font = pygame.font.SysFont(None, 24)
        line_height = 30

        for i, line in enumerate(self.info_text):
            text = info_font.render(line, True, (220, 220, 220))
            rect = text.get_rect(midtop=(SCREEN_WIDTH // 2, info_title_rect.bottom + 20 + i * line_height))
            self.screen.blit(text, rect)

        # Bouton de fermeture
        close_text = info_font.render("Cliquez n'importe où pour fermer", True, (180, 180, 200))
        close_rect = close_text.get_rect(midbottom=(SCREEN_WIDTH // 2, panel_rect.bottom - 20))
        self.screen.blit(close_text, close_rect)

class GameSimulation:
    """Classe gérant la simulation principale du jeu avec une interface améliorée."""
    def __init__(self, screen, clock, world):
        self.screen = screen
        self.clock = clock
        self.world = world

        # Variables pour la caméra - centrer la carte au démarrage
        self.camera_offset = [
            (self.world.width - SCREEN_WIDTH) / 2,
            (self.world.height - SCREEN_HEIGHT) / 2
        ]
        self.zoom = 0.5
        self.target_zoom = 0.5  # Pour animation de zoom fluide

        # Variables pour la simulation
        self.paused = False
        self.simulation_speed = SIMULATION_SPEED
        self.running = True

        # Variable pour suivre l'organisme sélectionné
        self.selected_organism = None
        self.follow_selected = False

        # Variable pour éviter les répétitions de touches
        self.key_pressed = False

        # Panneaux d'interface
        self.info_panel = Panel(10, 10, 280, 400, "Informations de Simulation", alpha=200)
        self.controls_panel = Panel(10, SCREEN_HEIGHT - 100, 280, 90, "Contrôles", alpha=200)

        # Panneaux avancés
        self.stats_panel = EvolutionStatsPanel(SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT // 2 - 300, 800, 600)
        self.stats_panel.set_world(self.world)

        self.genome_panel = GenomeViewerPanel(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 250, 700, 500)

        self.biome_panel = BiomesListPanel(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 200, 600, 400)
        self.biome_panel.set_world(self.world)

        # Boutons d'interface
        button_width = 40
        button_height = 40
        button_spacing = 10
        button_y = SCREEN_HEIGHT - button_height - 10

        self.buttons = {
            "stats": Button(
                10, button_y, button_width, button_height,
                "S", (50, 100, 150), (80, 150, 200),
                border_radius=5, font_size=20
            ),
            "pause": Button(
                10 + (button_width + button_spacing), button_y, button_width, button_height,
                "⏸", (150, 50, 50), (200, 80, 80),
                border_radius=5, font_size=20
            ),
            "speed_down": Button(
                10 + (button_width + button_spacing) * 2, button_y, button_width, button_height,
                "−", (100, 100, 100), (150, 150, 150),
                border_radius=5, font_size=20
            ),
            "speed_up": Button(
                10 + (button_width + button_spacing) * 3, button_y, button_width, button_height,
                "+", (100, 100, 100), (150, 150, 150),
                border_radius=5, font_size=20
            ),
            "add_organisms": Button(
                10 + (button_width + button_spacing) * 4, button_y, button_width, button_height,
                "🦠", (50, 150, 50), (80, 200, 80),
                border_radius=5, font_size=20
            ),
            "follow": Button(
                10 + (button_width + button_spacing) * 5, button_y, button_width, button_height,
                "👁", (150, 100, 50), (200, 150, 80),
                border_radius=5, font_size=20
            ),
            "screenshot": Button(
                10 + (button_width + button_spacing) * 6, button_y, button_width, button_height,
                "📷", (50, 50, 150), (80, 80, 200),
                border_radius=5, font_size=20
            ),
            "center": Button(
                10 + (button_width + button_spacing) * 7, button_y, button_width, button_height,
                "⌖", (50, 150, 150), (80, 200, 200),
                border_radius=5, font_size=20
            ),
            "menu": Button(
                10 + (button_width + button_spacing) * 7, button_y, button_width, button_height,
                "⚙", (100, 50, 100), (150, 80, 150),
                border_radius=5, font_size=20
            )
        }

        # Minimap
        self.show_minimap = True
        self.minimap_rect = pygame.Rect(SCREEN_WIDTH - 210, SCREEN_HEIGHT - 210, 200, 200)

        # Effets visuels
        self.visual_effects = []

        # Initialiser les commandes
        self._init_controls_panel()

    def _init_controls_panel(self):
        """Initialise le panneau de commandes."""
        self.controls_panel.content = []
        self.controls_panel.add_text("Espace: Pause/Reprendre", (180, 180, 220))
        self.controls_panel.add_text("R: Ajouter organismes aléatoires", (180, 180, 220))
        self.controls_panel.add_text("+/-: Ajuster vitesse", (180, 180, 220))

    def handle_events(self):
        """Gère les événements utilisateur."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    self._add_visual_effect("Pause" if self.paused else "Reprise", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    self.simulation_speed = min(10.0, self.simulation_speed * 1.5)
                    self._add_visual_effect(f"Vitesse: x{self.simulation_speed:.1f}", (SCREEN_WIDTH // 2, 100))

                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    self.simulation_speed = max(0.1, self.simulation_speed / 1.5)
                    self._add_visual_effect(f"Vitesse: x{self.simulation_speed:.1f}", (SCREEN_WIDTH // 2, 100))

                elif event.key == pygame.K_r:
                    # Ajouter des organismes aléatoires
                    count = 20
                    self.world.spawn_random_organisms(count)
                    self._add_visual_effect(f"+{count} organismes", (SCREEN_WIDTH // 2, 100))

                elif event.key == pygame.K_f:
                    # Suivre l'organisme sélectionné
                    if self.selected_organism:
                        self.follow_selected = not self.follow_selected
                        status = "activé" if self.follow_selected else "désactivé"
                        self._add_visual_effect(f"Suivi {status}", (SCREEN_WIDTH // 2, 100))

                elif event.key == pygame.K_s:
                    # Afficher/masquer les statistiques d'évolution
                    self.stats_panel.toggle()

                elif event.key == pygame.K_g:
                    # Afficher/masquer la visualisation du génome
                    if self.selected_organism:
                        self.genome_panel.set_organism(self.selected_organism)
                        self.genome_panel.toggle()

                elif event.key == pygame.K_b:
                    # Afficher/masquer le panneau des biomes
                    self.biome_panel.toggle()

                elif event.key == pygame.K_m:
                    # Afficher/masquer la minimap
                    self.show_minimap = not self.show_minimap

                elif event.key == pygame.K_p:
                    # Capture d'écran
                    self._take_screenshot()

                elif event.key == pygame.K_ESCAPE:
                    # Si un panneau est ouvert, le fermer
                    if self.stats_panel.visible:
                        self.stats_panel.toggle()
                    elif self.genome_panel.visible:
                        self.genome_panel.toggle()
                    elif self.biome_panel.visible:
                        self.biome_panel.toggle()
                    # Sinon, désélectionner l'organisme
                    elif self.selected_organism:
                        self.selected_organism = None
                        self.follow_selected = False
                    # Si rien n'est ouvert ou sélectionné, retourner au menu
                    else:
                        return "main_menu"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

                if event.button == 4:  # Molette vers le haut
                    self.target_zoom = min(2.0, self.target_zoom * 1.1)

                elif event.button == 5:  # Molette vers le bas
                    self.target_zoom = max(0.2, self.target_zoom / 1.1)

                elif event.button == 1:  # Clic gauche
                    # Vérifier si un bouton a été cliqué
                    button_clicked = False

                    for button_name, button in self.buttons.items():
                        if button.is_clicked(mouse_pos, True):
                            button_clicked = True
                            self._handle_button_click(button_name)
                            break

                    # Vérifier si un panneau a été cliqué
                    if not button_clicked:
                        if self.stats_panel.visible:
                            self.stats_panel.handle_event(event)
                        elif self.genome_panel.visible:
                            self.genome_panel.handle_event(event)
                        elif self.biome_panel.visible:
                            self.biome_panel.handle_event(event)
                        else:
                            # Conversion des coordonnées de l'écran en coordonnées du monde
                            world_x = self.camera_offset[0] + mouse_pos[0] / self.zoom
                            world_y = self.camera_offset[1] + mouse_pos[1] / self.zoom

                            # Recherche de l'organisme le plus proche du clic
                            closest_organism = None
                            min_distance = 20 / self.zoom  # Distance maximale de sélection

                            for organism in self.world.organisms:
                                if organism.is_alive:
                                    dist = math.sqrt((organism.position[0] - world_x)**2 +
                                                   (organism.position[1] - world_y)**2)
                                    if dist < min_distance:
                                        min_distance = dist
                                        closest_organism = organism

                            if closest_organism:
                                self.selected_organism = closest_organism
                                self._add_visual_effect("Organisme sélectionné",
                                                      (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
                            else:
                                # Afficher le panneau des biomes si on clique sur une cellule
                                cell = self.world.get_cell_at_position((world_x, world_y))
                                if cell:
                                    self.biome_panel.toggle()

            # Transmettre les événements aux panneaux actifs
            if self.stats_panel.visible:
                self.stats_panel.handle_event(event)
            if self.genome_panel.visible:
                self.genome_panel.handle_event(event)
            if self.biome_panel.visible:
                self.biome_panel.handle_event(event)

        # Mise à jour des boutons
        for button in self.buttons.values():
            button.update(mouse_pos)

        # Déplacement de la caméra avec les touches personnalisables
        keys = pygame.key.get_pressed()
        camera_speed = 10 / self.zoom

        if not self.follow_selected:
            # Utilisation des contrôles personnalisés
            if keys[CONTROLS.move_left]:
                self.camera_offset[0] = max(0, self.camera_offset[0] - camera_speed)
            if keys[CONTROLS.move_right]:
                self.camera_offset[0] = min(self.world.width - SCREEN_WIDTH / self.zoom,
                                          self.camera_offset[0] + camera_speed)
            if keys[CONTROLS.move_up]:
                self.camera_offset[1] = max(0, self.camera_offset[1] - camera_speed)
            if keys[CONTROLS.move_down]:
                self.camera_offset[1] = min(self.world.height - SCREEN_HEIGHT / self.zoom,
                                          self.camera_offset[1] + camera_speed)

            # Touche pour centrer la carte
            if keys[CONTROLS.center_map]:
                self.center_camera()

        # Autres contrôles clavier
        if keys[CONTROLS.pause] and not self.key_pressed:
            self.paused = not self.paused
            self._add_visual_effect("Pause" if self.paused else "Reprise",
                                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.key_pressed = True
        elif not any([keys[CONTROLS.pause], keys[CONTROLS.take_screenshot], keys[CONTROLS.follow_organism]]):
            self.key_pressed = False

        return None

    def center_camera(self):
        """Centre la caméra sur la carte."""
        self.camera_offset = [
            (self.world.width - SCREEN_WIDTH / self.zoom) / 2,
            (self.world.height - SCREEN_HEIGHT / self.zoom) / 2
        ]
        self._add_visual_effect("Carte centrée", (SCREEN_WIDTH // 2, 100))

    def _handle_button_click(self, button_name):
        """Gère les clics sur les boutons de l'interface."""
        if button_name == "stats":
            self.stats_panel.toggle()

        elif button_name == "pause":
            self.paused = not self.paused
            self._add_visual_effect("Pause" if self.paused else "Reprise",
                                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        elif button_name == "speed_down":
            self.simulation_speed = max(0.1, self.simulation_speed / 1.5)
            self._add_visual_effect(f"Vitesse: x{self.simulation_speed:.1f}",
                                  (SCREEN_WIDTH // 2, 100))

        elif button_name == "speed_up":
            self.simulation_speed = min(10.0, self.simulation_speed * 1.5)
            self._add_visual_effect(f"Vitesse: x{self.simulation_speed:.1f}",
                                  (SCREEN_WIDTH // 2, 100))

        elif button_name == "add_organisms":
            count = 20
            self.world.spawn_random_organisms(count)
            self._add_visual_effect(f"+{count} organismes", (SCREEN_WIDTH // 2, 100))

        elif button_name == "follow":
            if self.selected_organism:
                self.follow_selected = not self.follow_selected
                status = "activé" if self.follow_selected else "désactivé"
                self._add_visual_effect(f"Suivi {status}", (SCREEN_WIDTH // 2, 100))

        elif button_name == "screenshot":
            self._take_screenshot()

        elif button_name == "center":
            self.center_camera()

        elif button_name == "menu":
            # Ouvrir un menu contextuel
            self.paused = True
            return "main_menu"

    def _add_visual_effect(self, text, position, duration=1.5, color=(255, 255, 255)):
        """Ajoute un effet visuel temporaire à l'écran."""
        self.visual_effects.append({
            'text': text,
            'position': position,
            'duration': duration,
            'start_time': time.time(),
            'color': color,
            'alpha': 255
        })

    def _take_screenshot(self):
        """Prend une capture d'écran de la simulation."""
        # Créer un dossier pour les captures si nécessaire
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Générer un nom de fichier unique avec la date et l'heure
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{screenshots_dir}/bioevolve-{timestamp}.png"

        # Sauvegarder la capture d'écran
        pygame.image.save(self.screen, filename)

        # Afficher un message de confirmation
        self._add_visual_effect("Capture d'écran sauvegardée",
                              (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),
                              duration=2.0,
                              color=(150, 255, 150))

    def update(self):
        """Met à jour l'état de la simulation."""
        # Animation fluide du zoom
        zoom_speed = 0.1
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * zoom_speed
        else:
            self.zoom = self.target_zoom

        # Mise à jour de la simulation si non pausée
        if not self.paused:
            delta_time = self.clock.get_time() / 1000.0 * self.simulation_speed
            self.world.update(delta_time)

            # Vérifier si l'organisme sélectionné est toujours vivant
            if self.selected_organism and not self.selected_organism.is_alive:
                self.selected_organism = None
                self.follow_selected = False
                self._add_visual_effect("Organisme mort", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                      color=(255, 100, 100))

        # Suivre l'organisme sélectionné si activé
        if self.follow_selected and self.selected_organism:
            target_x = self.selected_organism.position[0] - SCREEN_WIDTH / (2 * self.zoom)
            target_y = self.selected_organism.position[1] - SCREEN_HEIGHT / (2 * self.zoom)

            # Déplacement fluide de la caméra
            camera_lerp = 0.1
            self.camera_offset[0] += (target_x - self.camera_offset[0]) * camera_lerp
            self.camera_offset[1] += (target_y - self.camera_offset[1]) * camera_lerp

            # Limiter aux bords du monde
            self.camera_offset[0] = max(0, min(self.world.width - SCREEN_WIDTH / self.zoom,
                                             self.camera_offset[0]))
            self.camera_offset[1] = max(0, min(self.world.height - SCREEN_HEIGHT / self.zoom,
                                             self.camera_offset[1]))

        # Mise à jour des panneaux
        self.stats_panel.update(self.clock.get_time() / 1000.0)

        if self.selected_organism and self.genome_panel.visible:
            self.genome_panel.set_organism(self.selected_organism)

        # Mise à jour des effets visuels
        current_time = time.time()
        for effect in self.visual_effects[:]:
            elapsed = current_time - effect['start_time']
            if elapsed > effect['duration']:
                self.visual_effects.remove(effect)
            else:
                # Faire disparaître progressivement
                fade_start = effect['duration'] * 0.7
                if elapsed > fade_start:
                    fade_progress = (elapsed - fade_start) / (effect['duration'] - fade_start)
                    effect['alpha'] = int(255 * (1 - fade_progress))

    def _update_info_panel(self):
        """Met à jour le contenu du panneau d'informations avec des informations améliorées."""
        self.info_panel.content = []

        # Informations de base avec icônes
        self.info_panel.add_text(f"🌍 Année: {self.world.year:.1f}", (220, 220, 150))

        # Afficher le cycle jour/nuit et la saison
        if hasattr(self.world, 'day_cycle'):
            day_progress = self.world.day_cycle % 1.0
            if day_progress < 0.25:
                time_icon = "🌅"  # Aube
                time_text = "Aube"
                time_color = (255, 200, 100)
            elif day_progress < 0.5:
                time_icon = "☀️"  # Jour
                time_text = "Jour"
                time_color = (255, 255, 150)
            elif day_progress < 0.75:
                time_icon = "🌇"  # Crépuscule
                time_text = "Crépuscule"
                time_color = (255, 150, 100)
            else:
                time_icon = "🌙"  # Nuit
                time_text = "Nuit"
                time_color = (150, 150, 255)

            self.info_panel.add_text(f"{time_icon} {time_text} ({day_progress*24:.1f}h)", time_color)

        # Afficher la saison actuelle
        if hasattr(self.world, 'season'):
            season_names = ["Printemps", "Été", "Automne", "Hiver"]
            season_icons = ["🌱", "☀️", "🍂", "❄️"]
            season_colors = [(100, 255, 100), (255, 255, 0), (255, 150, 50), (200, 200, 255)]

            season_text = season_names[self.world.season]
            season_icon = season_icons[self.world.season]
            season_color = season_colors[self.world.season]

            self.info_panel.add_text(f"{season_icon} {season_text}", season_color)

            # Ajouter une barre de progression pour la saison
            if hasattr(self.world, 'year_cycle'):
                season_progress = (self.world.year_cycle * 4) % 1.0
                self.info_panel.add_progress_bar("Progression", season_progress, season_color)

        # Informations sur la simulation
        self.info_panel.add_text(f"⏱️ Vitesse: x{self.simulation_speed:.1f}")
        self.info_panel.add_text(f"🔍 Zoom: {self.zoom:.1f}")
        self.info_panel.add_text(f"{'⏸️ PAUSE' if self.paused else '▶️ En cours'}",
                               (255, 150, 150) if self.paused else (150, 255, 150))

        # Afficher les FPS avec une couleur qui change selon la performance
        fps = int(self.clock.get_fps())
        if fps >= 45:
            fps_color = (100, 255, 100)  # Vert pour bon FPS
        elif fps >= 30:
            fps_color = (255, 255, 100)  # Jaune pour FPS moyen
        else:
            fps_color = (255, 100, 100)  # Rouge pour FPS bas
        self.info_panel.add_text(f"🖥️ FPS: {fps}", fps_color)

        # Ajouter des informations sur le climat
        if hasattr(self.world, 'global_temperature'):
            temp = self.world.global_temperature
            if temp < 0:
                temp_icon = "❄️"
                temp_color = (150, 150, 255)
            elif temp < 15:
                temp_icon = "🌡️"
                temp_color = (150, 200, 255)
            elif temp < 25:
                temp_icon = "🌡️"
                temp_color = (100, 255, 100)
            elif temp < 35:
                temp_icon = "🌡️"
                temp_color = (255, 200, 100)
            else:
                temp_icon = "🔥"
                temp_color = (255, 100, 100)

            self.info_panel.add_text(f"{temp_icon} Température: {temp:.1f}°C", temp_color)

        self.info_panel.add_separator()

        # Statistiques de population avec icônes
        self.info_panel.add_text("👥 Population", (200, 200, 120))
        total_organisms = len(self.world.organisms)
        self.info_panel.add_text(f"Total: {total_organisms}")

        # Calculer les pourcentages pour chaque type d'organisme
        unicellular_count = self.world.species_stats.get(OrganismType.UNICELLULAR, 0)
        plant_count = self.world.species_stats.get(OrganismType.PLANT, 0)
        herbivore_count = self.world.species_stats.get(OrganismType.HERBIVORE, 0)
        carnivore_count = self.world.species_stats.get(OrganismType.CARNIVORE, 0)
        omnivore_count = self.world.species_stats.get(OrganismType.OMNIVORE, 0)

        # Ajouter des barres de progression pour chaque type avec icônes
        if total_organisms > 0:
            self.info_panel.add_progress_bar("🦠 Unicellulaires", unicellular_count / total_organisms, (100, 100, 220))
            self.info_panel.add_progress_bar("🌿 Plantes", plant_count / total_organisms, (100, 220, 100))
            self.info_panel.add_progress_bar("🐰 Herbivores", herbivore_count / total_organisms, (220, 220, 100))
            self.info_panel.add_progress_bar("🦁 Carnivores", carnivore_count / total_organisms, (220, 100, 100))
            self.info_panel.add_progress_bar("🦝 Omnivores", omnivore_count / total_organisms, (220, 150, 100))

        # Statistiques d'évolution
        self.info_panel.add_separator()
        self.info_panel.add_text("🧬 Évolution", (200, 200, 120))
        self.info_panel.add_text(f"Génération max: {self.world.max_generation}")

        active_species = sum(1 for _, data in self.world.species_registry.items()
                           if not data.get('is_extinct', False) and data.get('count', 0) > 0)
        self.info_panel.add_text(f"🌱 Espèces actives: {active_species}")
        self.info_panel.add_text(f"☠️ Espèces éteintes: {self.world.extinction_count}")
        self.info_panel.add_text(f"🔄 Spéciations: {self.world.speciation_events}")

        # Ajouter des informations sur l'écosystème
        self.info_panel.add_separator()
        self.info_panel.add_text("🌐 Écosystème", (200, 200, 120))

        # Calculer le ratio proie/prédateur
        prey_count = plant_count + unicellular_count + herbivore_count
        predator_count = carnivore_count + omnivore_count

        if predator_count > 0:
            prey_predator_ratio = prey_count / predator_count

            # Évaluer l'équilibre de l'écosystème
            if 3 <= prey_predator_ratio <= 7:
                balance_text = "Équilibré"
                balance_color = (100, 255, 100)
            elif prey_predator_ratio < 3:
                balance_text = "Trop de prédateurs"
                balance_color = (255, 150, 100)
            else:
                balance_text = "Trop de proies"
                balance_color = (150, 150, 255)

            self.info_panel.add_text(f"⚖️ Équilibre: {balance_text}", balance_color)
            self.info_panel.add_text(f"Ratio proie/prédateur: {prey_predator_ratio:.1f}:1")

    def _draw_minimap(self):
        """Dessine une minimap du monde."""
        if not self.show_minimap:
            return

        # Créer une surface pour la minimap
        minimap_surface = pygame.Surface((self.minimap_rect.width, self.minimap_rect.height))
        minimap_surface.fill((20, 20, 30))

        # Facteur d'échelle pour la minimap
        scale_x = self.minimap_rect.width / self.world.width
        scale_y = self.minimap_rect.height / self.world.height

        # Dessiner les biomes (simplifié)
        for x in range(0, self.world.grid_width, 4):  # Échantillonner pour les performances
            for y in range(0, self.world.grid_height, 4):
                cell = self.world.grid[x][y]

                # Couleur basée sur le biome
                if cell.biome_type == BiomeType.OCEAN:
                    color = (0, 50, 100)
                elif cell.biome_type == BiomeType.SHALLOW_WATER:
                    color = (0, 100, 150)
                elif cell.biome_type == BiomeType.BEACH:
                    color = (200, 200, 100)
                elif cell.biome_type == BiomeType.GRASSLAND:
                    color = (100, 150, 50)
                elif cell.biome_type == BiomeType.FOREST:
                    color = (0, 100, 0)
                elif cell.biome_type == BiomeType.MOUNTAIN:
                    color = (100, 100, 100)
                elif cell.biome_type == BiomeType.DESERT:
                    color = (200, 180, 100)
                else:
                    color = (50, 50, 50)

                # Position sur la minimap
                mini_x = int(cell.position[0] * scale_x)
                mini_y = int(cell.position[1] * scale_y)

                # Dessiner un point pour cette cellule
                pygame.draw.rect(minimap_surface, color, (mini_x, mini_y, 2, 2))

        # Dessiner les organismes (points colorés)
        for organism in self.world.organisms:
            if organism.is_alive:
                # Couleur basée sur le type d'organisme
                if organism.organism_type == OrganismType.PLANT:
                    color = (0, 255, 0)
                elif organism.organism_type == OrganismType.HERBIVORE:
                    color = (255, 255, 0)
                elif organism.organism_type == OrganismType.CARNIVORE:
                    color = (255, 0, 0)
                elif organism.organism_type == OrganismType.OMNIVORE:
                    color = (255, 0, 255)
                else:
                    color = (0, 200, 255)

                # Position sur la minimap
                mini_x = int(organism.position[0] * scale_x)
                mini_y = int(organism.position[1] * scale_y)

                # Dessiner un point pour cet organisme
                pygame.draw.circle(minimap_surface, color, (mini_x, mini_y), 1)

        # Dessiner le rectangle de la vue actuelle
        view_x = int(self.camera_offset[0] * scale_x)
        view_y = int(self.camera_offset[1] * scale_y)
        view_width = int(SCREEN_WIDTH / self.zoom * scale_x)
        view_height = int(SCREEN_HEIGHT / self.zoom * scale_y)

        pygame.draw.rect(minimap_surface, (255, 255, 255),
                        (view_x, view_y, view_width, view_height), 1)

        # Dessiner la bordure de la minimap
        pygame.draw.rect(minimap_surface, (100, 100, 150),
                        (0, 0, self.minimap_rect.width, self.minimap_rect.height), 2)

        # Afficher la minimap
        self.screen.blit(minimap_surface, self.minimap_rect)

    def _draw_visual_effects(self):
        """Dessine les effets visuels temporaires."""
        for effect in self.visual_effects:
            # Créer une police pour le texte
            font_size = 28
            font = pygame.font.SysFont(None, font_size)

            # Rendu du texte avec transparence
            text_surface = font.render(effect['text'], True, effect['color'])
            text_surface.set_alpha(effect['alpha'])

            # Position centrée
            text_rect = text_surface.get_rect(center=effect['position'])

            # Dessiner le texte
            self.screen.blit(text_surface, text_rect)

    def _draw_organism_details(self):
        """Dessine les détails de l'organisme sélectionné."""
        if not self.selected_organism or not self.selected_organism.is_alive:
            return

        # Créer un panneau pour les détails de l'organisme
        organism_panel = Panel(SCREEN_WIDTH - 300, 10, 290, 500,
                              f"Organisme: {self.selected_organism.organism_type.name}",
                              alpha=220)

        # Détails de base
        details = self.selected_organism.get_details() if hasattr(self.selected_organism, 'get_details') else {}

        # Ajouter les détails importants
        if "Espèce" in details:
            organism_panel.add_text(f"Espèce: {details['Espèce']}", (220, 220, 150))

        organism_panel.add_text(f"Génération: {self.selected_organism.generation}", (200, 200, 200))

        # Convertir les valeurs en nombres flottants si possible, sinon utiliser les valeurs telles quelles
        try:
            age = float(details.get('Âge', 0))
            organism_panel.add_text(f"Âge: {age:.1f}", (200, 200, 200))
        except (ValueError, TypeError):
            organism_panel.add_text(f"Âge: {details.get('Âge', 0)}", (200, 200, 200))

        try:
            health = float(details.get('Santé', 0))
            organism_panel.add_text(f"Santé: {health:.1f}%",
                                  (100, 220, 100) if health > 50 else (220, 100, 100))
        except (ValueError, TypeError):
            organism_panel.add_text(f"Santé: {details.get('Santé', 0)}%",
                                  (100, 220, 100) if str(details.get('Santé', 0)).replace('%', '').strip() > '50' else (220, 100, 100))

        try:
            energy = float(details.get('Énergie', 0))
            max_energy = float(details.get('Énergie max', 0))
            organism_panel.add_text(f"Énergie: {energy:.1f}/{max_energy:.1f}",
                                  (220, 220, 100))
        except (ValueError, TypeError):
            organism_panel.add_text(f"Énergie: {details.get('Énergie', 0)}/{details.get('Énergie max', 0)}",
                                  (220, 220, 100))

        # Ajouter une séparation
        organism_panel.add_text("")
        organism_panel.add_text("Traits phénotypiques", (200, 150, 150))

        # Traits phénotypiques avec barres de progression
        traits = [
            ("Taille", self.selected_organism.phenotype.size, 3.0, (150, 150, 200)),
            ("Vitesse", self.selected_organism.phenotype.max_speed, 10.0, (100, 200, 200)),
            ("Force", self.selected_organism.phenotype.strength, 2.0, (200, 100, 100)),
            ("Métabolisme", self.selected_organism.phenotype.metabolism_rate, 2.0, (200, 200, 100)),
            ("Vision", self.selected_organism.phenotype.vision_range, 50.0, (150, 200, 150)),
            ("Immunité", self.selected_organism.phenotype.immune_strength, 1.0, (200, 150, 200)),
            ("Apprentissage", self.selected_organism.phenotype.learning_rate, 1.0, (200, 200, 150))
        ]

        for trait, value, max_val, color in traits:
            organism_panel.add_progress_bar(trait, value / max_val, color)

        # Ajouter des informations sur l'adaptation
        organism_panel.add_text("")
        organism_panel.add_text("Adaptation", (200, 150, 150))

        # Obtenir la cellule actuelle pour l'adaptation au biome
        cell = self.world.get_cell_at_position(self.selected_organism.position)
        if cell:
            biome_adaptation = self.world._calculate_biome_adaptation(self.selected_organism, cell)
            biome_name = cell.biome_type.name.replace('_', ' ').title()

            # Couleur basée sur le niveau d'adaptation
            adaptation_color = (
                int(255 * (1 - biome_adaptation)),
                int(255 * biome_adaptation),
                100
            )

            organism_panel.add_text(f"Biome actuel: {biome_name}", (180, 180, 220))
            organism_panel.add_progress_bar("Adaptation au biome", biome_adaptation, adaptation_color)

        # Dessiner le panneau d'organisme
        organism_panel.draw(self.screen)

        # Dessiner une ligne de la caméra à l'organisme pour le localiser facilement
        world_pos = self.selected_organism.position
        screen_pos = (
            int((world_pos[0] - self.camera_offset[0]) * self.zoom),
            int((world_pos[1] - self.camera_offset[1]) * self.zoom)
        )

        # Dessiner un cercle autour de l'organisme sélectionné
        radius = max(5, int(self.selected_organism.phenotype.size * 10 * self.zoom))
        pygame.draw.circle(self.screen, (255, 255, 100), screen_pos, radius, 2)

    def draw(self):
        """Dessine la simulation et l'interface utilisateur."""
        # Effacement de l'écran
        self.screen.fill(BLACK)

        # Dessin du monde avec l'organisme sélectionné
        self.world.draw(self.screen, self.camera_offset, self.zoom, selected_organism=self.selected_organism)

        # Mise à jour et dessin du panneau d'informations
        self._update_info_panel()
        self.info_panel.draw(self.screen)

        # Dessin du panneau de commandes
        self.controls_panel.draw(self.screen)

        # Dessin de la minimap
        self._draw_minimap()

        # Dessin des détails de l'organisme sélectionné
        self._draw_organism_details()

        # Dessin des boutons
        for button in self.buttons.values():
            button.draw(self.screen)

        # Dessin des panneaux avancés
        self.stats_panel.draw(self.screen)
        self.genome_panel.draw(self.screen)
        self.biome_panel.draw(self.screen)

        # Dessin des effets visuels
        self._draw_visual_effects()

    def run(self):
        """Exécute la boucle principale de la simulation."""
        while self.running:
            # Gestion des événements
            action = self.handle_events()
            if action:
                return action

            # Mise à jour de la simulation
            self.update()

            # Dessin de l'interface
            self.draw()

            # Mise à jour de l'affichage
            pygame.display.flip()
            self.clock.tick(FPS)

        return "main_menu"


class WorldCreator:
    """Interface améliorée pour créer un monde personnalisé avec des options avancées."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Paramètres par défaut - optimisés pour un écosystème stable
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.cell_size = CELL_SIZE
        self.initial_organisms = 200  # Augmenté pour un écosystème plus robuste

        # Ratios de biomes (pourcentages) - plus de zones habitables
        self.biome_ratios = {
            "ocean": 65,       # Réduit pour plus de terres
            "mountain": 7,
            "forest": 15,      # Augmenté pour plus d'habitats
            "desert": 5,       # Réduit car moins favorable
            "tundra": 2,
            "swamp": 3,        # Augmenté car riche en ressources
            "volcanic": 0.5,
            "grassland": 8.5   # Augmenté pour les herbivores
        }

        # Ratios d'organismes initiaux - équilibrés pour la chaîne alimentaire
        self.organism_ratios = [30, 40, 20, 5, 5]  # Unicellulaire, Plante, Herbivore, Carnivore, Omnivore
        # Plus de plantes pour soutenir les herbivores, moins de prédateurs

        # Paramètres climatiques - optimisés pour la biodiversité
        self.climate_params = {
            "temperature": 1.0,  # Multiplicateur de température (0.5 = plus froid, 1.5 = plus chaud)
            "humidity": 1.1,     # Légèrement plus humide pour favoriser la végétation
            "variability": 1.0,  # Variabilité du terrain (0.5 = plus lisse, 1.5 = plus accidenté)
            "sea_level": 0.0,    # Niveau de la mer (-0.2 = plus bas, +0.2 = plus haut)
            "resources": 1.2     # Augmenté pour plus de ressources disponibles
        }

        # Paramètres de simulation - optimisés pour la stabilité
        self.simulation_params = {
            "mutation_rate": 0.9,        # Légèrement réduit pour plus de stabilité génétique
            "selection_pressure": 0.8,   # Réduit pour une sélection naturelle moins sévère
            "competition": 0.8,          # Réduit pour moins de compétition entre organismes
            "predation": 0.7,            # Réduit pour une prédation moins intense
            "reproduction": 1.2          # Augmenté pour favoriser la reproduction
        }

        # Préréglages
        self.presets = {
            "équilibré": {
                "biome_ratios": self.biome_ratios.copy(),
                "organism_ratios": self.organism_ratios.copy(),
                "climate_params": self.climate_params.copy(),
                "simulation_params": self.simulation_params.copy()
            },
            "écosystème stable": {
                "biome_ratios": {"ocean": 60, "mountain": 6, "forest": 18, "desert": 4,
                                "tundra": 2, "swamp": 4, "volcanic": 0.5, "grassland": 10.5},
                "organism_ratios": [25, 45, 20, 5, 5],
                "climate_params": {"temperature": 1.0, "humidity": 1.2, "variability": 0.9,
                                  "sea_level": 0.0, "resources": 1.3},
                "simulation_params": {"mutation_rate": 0.8, "selection_pressure": 0.7,
                                     "competition": 0.7, "predation": 0.6, "reproduction": 1.3}
            },
            "monde aquatique": {
                "biome_ratios": {"ocean": 85, "mountain": 3, "forest": 5, "desert": 1,
                                "tundra": 1, "swamp": 3, "volcanic": 0.5, "grassland": 2.5},
                "organism_ratios": [50, 20, 15, 10, 5],
                "climate_params": {"temperature": 0.9, "humidity": 1.5, "variability": 0.8,
                                  "sea_level": 0.15, "resources": 1.2},
                "simulation_params": {"mutation_rate": 1.2, "selection_pressure": 1.1,
                                     "competition": 0.9, "predation": 0.8, "reproduction": 1.1}
            },
            "désert": {
                "biome_ratios": {"ocean": 40, "mountain": 10, "forest": 5, "desert": 35,
                                "tundra": 1, "swamp": 1, "volcanic": 2, "grassland": 7},
                "organism_ratios": [20, 25, 25, 20, 10],
                "climate_params": {"temperature": 1.4, "humidity": 0.6, "variability": 1.2,
                                  "sea_level": -0.1, "resources": 0.7},
                "simulation_params": {"mutation_rate": 1.3, "selection_pressure": 1.4,
                                     "competition": 1.3, "predation": 1.2, "reproduction": 0.8}
            },
            "forêt tropicale": {
                "biome_ratios": {"ocean": 60, "mountain": 5, "forest": 25, "desert": 1,
                                "tundra": 0, "swamp": 5, "volcanic": 1, "grassland": 4},
                "organism_ratios": [15, 40, 20, 15, 10],
                "climate_params": {"temperature": 1.2, "humidity": 1.4, "variability": 1.1,
                                  "sea_level": 0, "resources": 1.5},
                "simulation_params": {"mutation_rate": 1.1, "selection_pressure": 0.9,
                                     "competition": 1.2, "predation": 1.1, "reproduction": 1.3}
            },
            "monde glacial": {
                "biome_ratios": {"ocean": 65, "mountain": 12, "forest": 8, "desert": 0,
                                "tundra": 12, "swamp": 0, "volcanic": 1, "grassland": 3},
                "organism_ratios": [25, 20, 25, 20, 10],
                "climate_params": {"temperature": 0.6, "humidity": 0.8, "variability": 1.3,
                                  "sea_level": 0.05, "resources": 0.8},
                "simulation_params": {"mutation_rate": 0.9, "selection_pressure": 1.3,
                                     "competition": 1.4, "predation": 1.0, "reproduction": 0.7}
            },
            "archipel": {
                "biome_ratios": {"ocean": 80, "mountain": 5, "forest": 7, "desert": 2,
                                "tundra": 0, "swamp": 2, "volcanic": 2, "grassland": 3},
                "organism_ratios": [35, 25, 20, 15, 5],
                "climate_params": {"temperature": 1.1, "humidity": 1.2, "variability": 1.4,
                                  "sea_level": 0.1, "resources": 1.1},
                "simulation_params": {"mutation_rate": 1.2, "selection_pressure": 1.0,
                                     "competition": 0.8, "predation": 0.9, "reproduction": 1.2}
            }
        }

        # Interface
        self.sliders = {}
        self.current_tab = "biomes"  # Onglet actif: "biomes", "organismes", "climat", "simulation"
        self._init_sliders()

        # Boutons
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2

        self.create_button = Button(
            button_x, SCREEN_HEIGHT - 120, button_width, button_height,
            "Créer le Monde", (0, 100, 0), (0, 150, 0),
            border_radius=10, font_size=28
        )

        self.back_button = Button(
            button_x, SCREEN_HEIGHT - 60, button_width, button_height,
            "Retour", (100, 0, 0), (150, 0, 0),
            border_radius=10, font_size=28
        )

        # Boutons d'onglets
        tab_width = 150
        tab_height = 40
        tab_y = 90
        self.tab_buttons = {
            "biomes": Button(
                50, tab_y, tab_width, tab_height,
                "Biomes", (50, 50, 100), (80, 80, 150),
                border_radius=5, font_size=24
            ),
            "organismes": Button(
                50 + tab_width + 10, tab_y, tab_width, tab_height,
                "Organismes", (50, 100, 50), (80, 150, 80),
                border_radius=5, font_size=24
            ),
            "climat": Button(
                50 + (tab_width + 10) * 2, tab_y, tab_width, tab_height,
                "Climat", (100, 50, 50), (150, 80, 80),
                border_radius=5, font_size=24
            ),
            "simulation": Button(
                50 + (tab_width + 10) * 3, tab_y, tab_width, tab_height,
                "Simulation", (50, 50, 100), (80, 80, 150),
                border_radius=5, font_size=24
            )
        }

        # Boutons de préréglages
        preset_width = 120
        preset_height = 30
        preset_y = 150
        self.preset_buttons = {}

        for i, preset_name in enumerate(self.presets.keys()):
            self.preset_buttons[preset_name] = Button(
                SCREEN_WIDTH - 150, preset_y + i * (preset_height + 10), preset_width, preset_height,
                preset_name.capitalize(), (70, 70, 100), (100, 100, 150),
                border_radius=5, font_size=18
            )

        # Aperçu du monde
        self.preview_rect = pygame.Rect(SCREEN_WIDTH - 250, 350, 200, 200)
        self.preview_surface = None
        self.generate_preview()

        # Animation
        self.particles = []
        self.create_particles(50)

    def create_particles(self, count):
        """Crée des particules pour l'animation de fond."""
        for _ in range(count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.uniform(1, 3)
            speed = random.uniform(0.2, 1.0)
            color = (
                random.randint(30, 70),
                random.randint(50, 100),
                random.randint(100, 200)
            )
            self.particles.append({
                'pos': [x, y],
                'size': size,
                'speed': speed,
                'color': color,
                'angle': random.uniform(0, 2 * math.pi)
            })

    def update_particles(self):
        """Met à jour les particules pour l'animation de fond."""
        for particle in self.particles:
            # Mouvement sinusoïdal
            particle['angle'] += 0.01
            particle['pos'][0] += math.sin(particle['angle']) * 0.5
            particle['pos'][1] -= particle['speed']

            # Réinitialiser les particules qui sortent de l'écran
            if particle['pos'][1] < -10:
                particle['pos'][1] = SCREEN_HEIGHT + 10
                particle['pos'][0] = random.randint(0, SCREEN_WIDTH)

    def _init_sliders(self):
        """Initialise les sliders pour les paramètres."""
        self.sliders = {
            # Paramètres généraux
            "width": {"value": self.width, "min": 1600, "max": 12800, "text": "Largeur du monde", "tab": "biomes"},
            "height": {"value": self.height, "min": 900, "max": 7200, "text": "Hauteur du monde", "tab": "biomes"},
            "cell_size": {"value": self.cell_size, "min": 10, "max": 50, "text": "Taille des cellules", "tab": "biomes"},
            "initial_organisms": {"value": self.initial_organisms, "min": 10, "max": 500, "text": "Organismes initiaux", "tab": "organismes"},

            # Sliders pour les ratios de biomes
            "biome_ocean": {"value": self.biome_ratios["ocean"], "min": 0, "max": 100, "text": "Océan", "tab": "biomes"},
            "biome_mountain": {"value": self.biome_ratios["mountain"], "min": 0, "max": 100, "text": "Montagnes", "tab": "biomes"},
            "biome_forest": {"value": self.biome_ratios["forest"], "min": 0, "max": 100, "text": "Forêts", "tab": "biomes"},
            "biome_desert": {"value": self.biome_ratios["desert"], "min": 0, "max": 100, "text": "Déserts", "tab": "biomes"},
            "biome_tundra": {"value": self.biome_ratios["tundra"], "min": 0, "max": 100, "text": "Toundra", "tab": "biomes"},
            "biome_swamp": {"value": self.biome_ratios["swamp"], "min": 0, "max": 100, "text": "Marécages", "tab": "biomes"},
            "biome_volcanic": {"value": self.biome_ratios["volcanic"], "min": 0, "max": 100, "text": "Volcanique", "tab": "biomes"},
            "biome_grassland": {"value": self.biome_ratios["grassland"], "min": 0, "max": 100, "text": "Prairies", "tab": "biomes"},

            # Sliders pour les ratios d'organismes
            "org_0": {"value": self.organism_ratios[0], "min": 0, "max": 100, "text": "Unicellulaires", "tab": "organismes"},
            "org_1": {"value": self.organism_ratios[1], "min": 0, "max": 100, "text": "Plantes", "tab": "organismes"},
            "org_2": {"value": self.organism_ratios[2], "min": 0, "max": 100, "text": "Herbivores", "tab": "organismes"},
            "org_3": {"value": self.organism_ratios[3], "min": 0, "max": 100, "text": "Carnivores", "tab": "organismes"},
            "org_4": {"value": self.organism_ratios[4], "min": 0, "max": 100, "text": "Omnivores", "tab": "organismes"},

            # Sliders pour les paramètres climatiques
            "climate_temperature": {"value": self.climate_params["temperature"] * 100, "min": 50, "max": 150, "text": "Température", "tab": "climat"},
            "climate_humidity": {"value": self.climate_params["humidity"] * 100, "min": 50, "max": 150, "text": "Humidité", "tab": "climat"},
            "climate_variability": {"value": self.climate_params["variability"] * 100, "min": 50, "max": 150, "text": "Variabilité", "tab": "climat"},
            "climate_sea_level": {"value": (self.climate_params["sea_level"] + 0.2) * 250, "min": 0, "max": 100, "text": "Niveau de la mer", "tab": "climat"},
            "climate_resources": {"value": self.climate_params["resources"] * 100, "min": 50, "max": 150, "text": "Ressources", "tab": "climat"},

            # Sliders pour les paramètres de simulation
            "sim_mutation_rate": {"value": self.simulation_params["mutation_rate"] * 100, "min": 50, "max": 150, "text": "Taux de mutation", "tab": "simulation"},
            "sim_selection_pressure": {"value": self.simulation_params["selection_pressure"] * 100, "min": 50, "max": 150, "text": "Pression de sélection", "tab": "simulation"},
            "sim_competition": {"value": self.simulation_params["competition"] * 100, "min": 50, "max": 150, "text": "Compétition", "tab": "simulation"},
            "sim_predation": {"value": self.simulation_params["predation"] * 100, "min": 50, "max": 150, "text": "Prédation", "tab": "simulation"},
            "sim_reproduction": {"value": self.simulation_params["reproduction"] * 100, "min": 50, "max": 150, "text": "Reproduction", "tab": "simulation"}
        }

    def generate_preview(self):
        """Génère un aperçu du monde basé sur les paramètres actuels."""
        preview_width = self.preview_rect.width
        preview_height = self.preview_rect.height

        # Créer une surface pour l'aperçu
        self.preview_surface = pygame.Surface((preview_width, preview_height))

        # Paramètres pour la génération de bruit
        scale = 10.0
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0

        # Ajuster les paramètres en fonction des réglages climatiques
        variability = self.climate_params["variability"]
        sea_level = self.climate_params["sea_level"]

        # Générer une carte d'altitude simplifiée
        altitude_map = []
        for y in range(preview_height):
            row = []
            for x in range(preview_width):
                # Bruit de Perlin simplifié
                nx = x / preview_width * scale
                ny = y / preview_height * scale

                # Simuler le bruit de Perlin
                value = 0
                amplitude = 1.0
                frequency = 1.0

                for _ in range(octaves):
                    noise_val = (math.sin(nx * frequency * 12.9898 + ny * frequency * 78.233) * 43758.5453) % 1
                    noise_val += (math.cos(nx * frequency * 39.346 + ny * frequency * 11.135) * 53758.5453) % 1
                    noise_val = (noise_val - 0.5) * 2

                    value += noise_val * amplitude
                    amplitude *= persistence
                    frequency *= lacunarity

                # Normaliser et ajuster avec la variabilité
                value = (value + 1) / 2
                value = value ** (1 / variability)  # Ajuster la variabilité

                # Ajuster le niveau de la mer
                value = value + sea_level

                row.append(value)
            altitude_map.append(row)

        # Dessiner l'aperçu
        for y in range(preview_height):
            for x in range(preview_width):
                altitude = altitude_map[y][x]

                # Déterminer le biome en fonction de l'altitude
                if altitude < 0.4 + sea_level:  # Océan
                    color = (0, 50, 100)
                elif altitude < 0.45 + sea_level:  # Plage
                    color = (200, 200, 100)
                elif altitude < 0.55 + sea_level:  # Plaines/Prairies
                    color = (100, 150, 50)
                elif altitude < 0.7 + sea_level:  # Forêt
                    color = (0, 100, 0)
                elif altitude < 0.85 + sea_level:  # Montagne
                    color = (100, 100, 100)
                else:  # Sommet de montagne
                    color = (200, 200, 200)

                # Dessiner le pixel
                self.preview_surface.set_at((x, y), color)

        # Ajouter une bordure
        pygame.draw.rect(self.preview_surface, (100, 100, 150), (0, 0, preview_width, preview_height), 1)

    def apply_preset(self, preset_name):
        """Applique un préréglage prédéfini."""
        if preset_name in self.presets:
            preset = self.presets[preset_name]

            # Appliquer les ratios de biomes
            self.biome_ratios = preset["biome_ratios"].copy()
            for biome, ratio in self.biome_ratios.items():
                self.sliders[f"biome_{biome}"]["value"] = ratio

            # Appliquer les ratios d'organismes
            self.organism_ratios = preset["organism_ratios"].copy()
            for i, ratio in enumerate(self.organism_ratios):
                self.sliders[f"org_{i}"]["value"] = ratio

            # Appliquer les paramètres climatiques
            self.climate_params = preset["climate_params"].copy()
            self.sliders["climate_temperature"]["value"] = self.climate_params["temperature"] * 100
            self.sliders["climate_humidity"]["value"] = self.climate_params["humidity"] * 100
            self.sliders["climate_variability"]["value"] = self.climate_params["variability"] * 100
            self.sliders["climate_sea_level"]["value"] = (self.climate_params["sea_level"] + 0.2) * 250
            self.sliders["climate_resources"]["value"] = self.climate_params["resources"] * 100

            # Appliquer les paramètres de simulation
            self.simulation_params = preset["simulation_params"].copy()
            self.sliders["sim_mutation_rate"]["value"] = self.simulation_params["mutation_rate"] * 100
            self.sliders["sim_selection_pressure"]["value"] = self.simulation_params["selection_pressure"] * 100
            self.sliders["sim_competition"]["value"] = self.simulation_params["competition"] * 100
            self.sliders["sim_predation"]["value"] = self.simulation_params["predation"] * 100
            self.sliders["sim_reproduction"]["value"] = self.simulation_params["reproduction"] * 100

            # Régénérer l'aperçu
            self.generate_preview()

            return True
        return False

    def run(self):
        """Exécute l'interface de création de monde."""
        # Animation d'entrée
        fade_alpha = 255
        fade_speed = 5

        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        mouse_click = True

            # Animation de fondu en entrée
            if fade_alpha > 0:
                fade_alpha = max(0, fade_alpha - fade_speed)

            # Mise à jour des particules
            self.update_particles()

            # Mise à jour des boutons
            self.create_button.update(mouse_pos)
            self.back_button.update(mouse_pos)

            # Mise à jour des boutons d'onglets
            for tab_name, button in self.tab_buttons.items():
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click):
                    self.current_tab = tab_name

            # Mise à jour des boutons de préréglages
            for preset_name, button in self.preset_buttons.items():
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click):
                    self.apply_preset(preset_name)

            # Vérification des clics sur les boutons principaux
            if self.create_button.is_clicked(mouse_pos, mouse_click):
                # Effet de transition
                self.transition_effect()
                return self.create_world()

            if self.back_button.is_clicked(mouse_pos, mouse_click):
                # Effet de transition
                self.transition_effect()
                self.running = False
                return None

            # Mise à jour des sliders
            for key, slider in self.sliders.items():
                # Ne traiter que les sliders de l'onglet actif
                if slider["tab"] != self.current_tab:
                    continue

                slider_rect = pygame.Rect(300, 150 + self._get_slider_index(key) * 40, 400, 20)

                if mouse_click and slider_rect.collidepoint(mouse_pos):
                    # Calculer la nouvelle valeur en fonction de la position de la souris
                    ratio = (mouse_pos[0] - slider_rect.x) / slider_rect.width
                    slider["value"] = slider["min"] + ratio * (slider["max"] - slider["min"])
                    slider["value"] = max(slider["min"], min(slider["max"], slider["value"]))

                    # Mettre à jour les paramètres correspondants
                    if key == "width":
                        self.width = int(slider["value"])
                    elif key == "height":
                        self.height = int(slider["value"])
                    elif key == "cell_size":
                        self.cell_size = int(slider["value"])
                    elif key == "initial_organisms":
                        self.initial_organisms = int(slider["value"])
                    elif key.startswith("biome_"):
                        biome = key[6:]  # Extraire le nom du biome
                        self.biome_ratios[biome] = slider["value"]
                    elif key.startswith("org_"):
                        index = int(key[4:])  # Extraire l'index du type d'organisme
                        self.organism_ratios[index] = slider["value"]
                    elif key.startswith("climate_"):
                        param = key[8:]  # Extraire le nom du paramètre
                        if param == "temperature":
                            self.climate_params["temperature"] = slider["value"] / 100
                        elif param == "humidity":
                            self.climate_params["humidity"] = slider["value"] / 100
                        elif param == "variability":
                            self.climate_params["variability"] = slider["value"] / 100
                        elif param == "sea_level":
                            self.climate_params["sea_level"] = slider["value"] / 250 - 0.2
                        elif param == "resources":
                            self.climate_params["resources"] = slider["value"] / 100
                    elif key.startswith("sim_"):
                        param = key[4:]  # Extraire le nom du paramètre
                        self.simulation_params[param] = slider["value"] / 100

                    # Régénérer l'aperçu si nécessaire
                    if key.startswith("biome_") or key.startswith("climate_"):
                        self.generate_preview()

            # Normalisation des ratios de biomes
            if self.current_tab == "biomes":
                total_biome_ratio = sum(self.biome_ratios.values())
                if total_biome_ratio > 0:
                    for biome in self.biome_ratios:
                        self.biome_ratios[biome] = (self.biome_ratios[biome] / total_biome_ratio) * 100
                        self.sliders[f"biome_{biome}"]["value"] = self.biome_ratios[biome]

            # Normalisation des ratios d'organismes
            if self.current_tab == "organismes":
                total_org_ratio = sum(self.organism_ratios)
                if total_org_ratio > 0:
                    for i in range(len(self.organism_ratios)):
                        self.organism_ratios[i] = (self.organism_ratios[i] / total_org_ratio) * 100
                        self.sliders[f"org_{i}"]["value"] = self.organism_ratios[i]

            # Dessin de l'interface
            self.draw()

            # Superposition du fondu
            if fade_alpha > 0:
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(fade_alpha)
                self.screen.blit(fade_surface, (0, 0))

            # Mise à jour de l'affichage
            pygame.display.flip()
            self.clock.tick(60)

        return None

    def _get_slider_index(self, key):
        """Retourne l'index du slider dans l'onglet actuel."""
        index = 0
        for k, slider in self.sliders.items():
            if slider["tab"] == self.current_tab:
                if k == key:
                    return index
                index += 1
        return 0

    def transition_effect(self):
        """Effet de transition lors du clic sur un bouton."""
        for alpha in range(0, 256, 10):
            self.draw()
            fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(5)

    def draw(self):
        """Dessine l'interface de création de monde avec des effets visuels améliorés."""
        # Fond avec dégradé
        self.screen.fill((15, 15, 35))

        # Dessin des particules
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['pos'][0]), int(particle['pos'][1])),
                particle['size']
            )

        # Titre avec effet de lueur
        title_font = pygame.font.SysFont(None, 48)
        title_shadow = title_font.render("Création de Monde", True, (30, 100, 180))
        title_text = title_font.render("Création de Monde", True, (100, 200, 255))

        # Animation du titre
        title_offset = math.sin(pygame.time.get_ticks() / 1000) * 3

        # Ombre du titre
        shadow_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 2, 50 + 2))
        self.screen.blit(title_shadow, shadow_rect)

        # Titre principal
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50 + title_offset))
        self.screen.blit(title_text, title_rect)

        # Ligne décorative
        line_width = 400
        pygame.draw.line(
            self.screen,
            (80, 120, 200),
            (SCREEN_WIDTH // 2 - line_width // 2, 80),
            (SCREEN_WIDTH // 2 + line_width // 2, 80),
            2
        )

        # Dessiner les boutons d'onglets
        for tab_name, button in self.tab_buttons.items():
            # Mettre en évidence l'onglet actif
            if tab_name == self.current_tab:
                # Sauvegarder les couleurs originales
                original_color = button.base_color
                original_hover = button.hover_color

                # Définir des couleurs plus vives pour l'onglet actif
                button.base_color = tuple(min(255, c + 50) for c in original_color)
                button.hover_color = tuple(min(255, c + 50) for c in original_hover)
                button.current_color = button.base_color

                # Dessiner le bouton
                button.draw(self.screen)

                # Restaurer les couleurs originales
                button.base_color = original_color
                button.hover_color = original_hover
            else:
                button.draw(self.screen)

        # Dessiner les sliders de l'onglet actif
        slider_index = 0
        for key, slider in self.sliders.items():
            if slider["tab"] != self.current_tab:
                continue

            y_pos = 150 + slider_index * 40
            slider_index += 1

            # Texte du slider avec effet d'ombre
            text = self.small_font.render(f"{slider['text']}: {int(slider['value'])}", True, WHITE)
            text_shadow = self.small_font.render(f"{slider['text']}: {int(slider['value'])}", True, (50, 50, 80))

            # Ombre du texte
            self.screen.blit(text_shadow, (52, y_pos + 2))
            # Texte
            self.screen.blit(text, (50, y_pos))

            # Barre du slider avec effet 3D
            slider_rect = pygame.Rect(300, y_pos, 400, 20)

            # Ombre du slider
            shadow_rect = pygame.Rect(slider_rect.x + 2, slider_rect.y + 2, slider_rect.width, slider_rect.height)
            pygame.draw.rect(self.screen, (30, 30, 50), shadow_rect, border_radius=5)

            # Fond du slider
            pygame.draw.rect(self.screen, (50, 50, 70), slider_rect, border_radius=5)

            # Position actuelle du slider
            ratio = (slider["value"] - slider["min"]) / (slider["max"] - slider["min"])
            pos_x = slider_rect.x + ratio * slider_rect.width

            # Barre de progression avec dégradé
            if pos_x > slider_rect.x:
                progress_rect = pygame.Rect(slider_rect.x, slider_rect.y, pos_x - slider_rect.x, slider_rect.height)

                # Couleur basée sur le type de slider
                if key.startswith("biome_"):
                    color = (100, 150, 200)
                elif key.startswith("org_"):
                    color = (100, 200, 100)
                elif key.startswith("climate_"):
                    color = (200, 150, 100)
                elif key.startswith("sim_"):
                    color = (150, 100, 200)
                else:
                    color = (150, 150, 200)

                pygame.draw.rect(self.screen, color, progress_rect, border_radius=5)

            # Bordure du slider
            pygame.draw.rect(self.screen, (100, 100, 150), slider_rect, 2, border_radius=5)

            # Poignée du slider
            handle_radius = 10
            pygame.draw.circle(self.screen, (200, 200, 250), (int(pos_x), slider_rect.y + slider_rect.height // 2), handle_radius)
            pygame.draw.circle(self.screen, (150, 150, 200), (int(pos_x), slider_rect.y + slider_rect.height // 2), handle_radius, 2)

        # Dessiner l'aperçu du monde
        if self.preview_surface:
            # Titre de l'aperçu
            preview_title = self.small_font.render("Aperçu du Monde", True, (200, 200, 250))
            preview_title_rect = preview_title.get_rect(center=(self.preview_rect.centerx, self.preview_rect.y - 20))
            self.screen.blit(preview_title, preview_title_rect)

            # Cadre avec ombre
            shadow_rect = pygame.Rect(self.preview_rect.x + 4, self.preview_rect.y + 4, self.preview_rect.width, self.preview_rect.height)
            pygame.draw.rect(self.screen, (20, 20, 40), shadow_rect)

            # Aperçu
            self.screen.blit(self.preview_surface, self.preview_rect)

            # Bordure décorative
            pygame.draw.rect(self.screen, (100, 150, 200), self.preview_rect, 2)

        # Dessiner les boutons de préréglages
        preset_title = self.small_font.render("Préréglages", True, (200, 200, 250))
        preset_title_rect = preset_title.get_rect(center=(SCREEN_WIDTH - 150, 130))
        self.screen.blit(preset_title, preset_title_rect)

        for preset_name, button in self.preset_buttons.items():
            button.draw(self.screen)

        # Dessiner les boutons principaux avec effets
        self.create_button.draw(self.screen)
        self.back_button.draw(self.screen)

        # Informations supplémentaires
        if self.current_tab == "biomes":
            info_text = "Ajustez les proportions des différents biomes dans votre monde."
        elif self.current_tab == "organismes":
            info_text = "Définissez la population initiale et les types d'organismes."
        elif self.current_tab == "climat":
            info_text = "Configurez les conditions climatiques et environnementales."
        elif self.current_tab == "simulation":
            info_text = "Ajustez les paramètres qui influencent l'évolution des espèces."

        info_font = pygame.font.SysFont(None, 20)
        info_surface = info_font.render(info_text, True, (180, 180, 220))
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
        self.screen.blit(info_surface, info_rect)

    def create_world(self):
        """Crée un monde avec les paramètres spécifiés."""
        # Créer le monde avec les dimensions de base
        world = World(self.width, self.height, cell_size=self.cell_size)

        # Convertir les ratios de biomes en format décimal
        biome_ratios_decimal = {biome: ratio / 100 for biome, ratio in self.biome_ratios.items()}

        # Appliquer les ratios de biomes
        world.biome_ratios = biome_ratios_decimal

        # Appliquer les paramètres climatiques si la classe World les supporte
        if hasattr(world, 'climate_params'):
            world.climate_params = self.climate_params.copy()
        elif hasattr(world, 'global_temperature'):
            # Conversion approximative de notre échelle de température à celle du monde
            world.global_temperature = self.climate_params["temperature"] * 30  # Échelle approximative

        # Appliquer les paramètres de simulation si la classe World les supporte
        if hasattr(world, 'simulation_params'):
            world.simulation_params = self.simulation_params.copy()

        # Régénérer le monde avec les nouveaux paramètres
        if hasattr(world, '_generate_world'):
            world._generate_world()

        # Normaliser les ratios d'organismes
        total = sum(self.organism_ratios)
        weights = [ratio / total for ratio in self.organism_ratios]

        # Ajouter les organismes initiaux
        print(f"Génération de {self.initial_organisms} organismes initiaux...")
        world.spawn_random_organisms(self.initial_organisms, weights)

        return world


def main():
    """Fonction principale pour exécuter la simulation."""
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BioEvolve - Simulateur d'Évolution Biologique")
    clock = pygame.time.Clock()

    # Afficher le menu principal
    menu = MainMenu(screen)
    action = menu.run()

    while action != "quit":
        # Création du monde
        world = None

        if action == "new_game":
            # Création d'un monde par défaut avec un écosystème équilibré
            world = World(SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2, cell_size=20)

            # Distribution équilibrée des organismes pour un écosystème stable
            # Plus de plantes et d'unicellulaires pour soutenir la chaîne alimentaire
            balanced_weights = [0.3, 0.4, 0.2, 0.05, 0.05]  # Unicellulaires, Plantes, Herbivores, Carnivores, Omnivores

            # Augmenter le nombre initial d'organismes pour un écosystème plus robuste
            world.spawn_random_organisms(200, balanced_weights)
        elif action == "create_world":
            # Interface de création de monde
            creator = WorldCreator(screen)
            world = creator.run()

            if world is None:
                # Retour au menu principal
                action = "main_menu"
                continue
        elif action == "load_world":
            # TODO: Implémenter le chargement de monde
            # Pour l'instant, créer un monde par défaut avec un écosystème équilibré
            world = World(SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2, cell_size=20)

            # Distribution équilibrée des organismes pour un écosystème stable
            balanced_weights = [0.3, 0.4, 0.2, 0.05, 0.05]  # Unicellulaires, Plantes, Herbivores, Carnivores, Omnivores
            world.spawn_random_organisms(200, balanced_weights)

        elif action == "scenarios":
            # TODO: Implémenter les scénarios
            # Pour l'instant, créer un monde par défaut avec un écosystème équilibré
            world = World(SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2, cell_size=20)

            # Distribution équilibrée des organismes pour un écosystème stable
            balanced_weights = [0.3, 0.4, 0.2, 0.05, 0.05]  # Unicellulaires, Plantes, Herbivores, Carnivores, Omnivores
            world.spawn_random_organisms(200, balanced_weights)
        elif action == "settings":
            # Ouvrir le menu des paramètres
            settings_menu = SettingsMenu(screen)
            action = settings_menu.run()
            continue
        elif action == "main_menu":
            menu = MainMenu(screen)
            action = menu.run()
            continue
        else:
            # Action inconnue, retourner au menu principal
            menu = MainMenu(screen)
            action = menu.run()
            continue

        # Lancer la simulation
        if world:
            simulation = GameSimulation(screen, clock, world)
            action = simulation.run()
        else:
            action = "main_menu"

    # Nettoyage
    pygame.quit()


if __name__ == "__main__":
    main()