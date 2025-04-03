"""
Module de gestion des espèces pour BioEvolve
Permet de suivre, enregistrer et charger les informations sur les espèces découvertes
"""

import os
import json
import uuid
import random
import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

# Définition des types d'organismes (importé depuis main.py)
class OrganismType(Enum):
    UNICELLULAR = 0
    PLANT = 1
    HERBIVORE = 2
    CARNIVORE = 3
    OMNIVORE = 4

class SpeciesTraits:
    """Classe représentant les traits distinctifs d'une espèce"""
    
    # Traits physiques possibles par type d'organisme
    PHYSICAL_TRAITS = {
        OrganismType.UNICELLULAR: [
            "sphérique", "en bâtonnet", "spiralé", "filamenteux", "étoilé", 
            "cubique", "conique", "amorphe", "flagellé", "cilié",
            "colonial", "encapsulé", "segmenté", "ramifié", "granuleux"
        ],
        OrganismType.PLANT: [
            "à feuilles larges", "à feuilles étroites", "à feuilles composées", "à feuilles simples",
            "à fleurs colorées", "à fleurs discrètes", "sans fleurs", "à fruits charnus", "à fruits secs",
            "à écorce rugueuse", "à écorce lisse", "épineux", "grimpant", "rampant", "dressé",
            "à racines profondes", "à racines superficielles", "à rhizomes", "à bulbes", "à tubercules"
        ],
        OrganismType.HERBIVORE: [
            "à longues pattes", "à pattes courtes", "à sabots", "à griffes", "à coussinets",
            "à fourrure épaisse", "à fourrure fine", "à peau nue", "à écailles", "à plumes",
            "à longue queue", "à queue courte", "sans queue", "à grandes oreilles", "à petites oreilles",
            "à cornes", "à bois", "à défenses", "à bec", "à museau allongé"
        ],
        OrganismType.CARNIVORE: [
            "à dents acérées", "à mâchoires puissantes", "à griffes rétractiles", "à griffes fixes",
            "à fourrure tachetée", "à fourrure rayée", "à fourrure unie", "à peau épaisse", "à écailles",
            "à queue préhensile", "à queue touffue", "à queue fine", "à oreilles pointues", "à oreilles rondes",
            "à vision nocturne", "à odorat développé", "à ouïe fine", "à crocs venimeux", "à coloration vive"
        ],
        OrganismType.OMNIVORE: [
            "à dentition mixte", "à membres préhensiles", "à doigts agiles", "à ongles plats",
            "à fourrure dense", "à fourrure clairsemée", "à peau pigmentée", "à peau claire",
            "à queue mobile", "sans queue", "à oreilles mobiles", "à oreilles fixes",
            "à vision binoculaire", "à vision périphérique", "à odorat moyen", "à ouïe moyenne",
            "à posture bipède", "à posture quadrupède", "à posture variable", "à mimétisme"
        ]
    }
    
    # Couleurs possibles par type d'organisme
    COLORS = {
        OrganismType.UNICELLULAR: [
            "transparent", "blanc", "crème", "jaune pâle", "rose pâle", "bleu pâle", "vert pâle",
            "gris", "doré", "argenté", "ambré", "iridescent", "fluorescent", "luminescent"
        ],
        OrganismType.PLANT: [
            "vert foncé", "vert clair", "vert bleuté", "vert jaunâtre", "rouge", "pourpre",
            "jaune", "orange", "blanc", "rose", "violet", "bicolore", "marbré", "panaché", "strié"
        ],
        OrganismType.HERBIVORE: [
            "brun", "beige", "gris", "blanc", "noir", "roux", "fauve", "crème", "doré",
            "tacheté", "rayé", "moucheté", "bicolore", "tricolore", "camouflé"
        ],
        OrganismType.CARNIVORE: [
            "noir", "brun foncé", "roux", "fauve", "gris", "blanc", "rayé", "tacheté",
            "moucheté", "à rosettes", "à bandes", "uniforme", "bicolore", "à masque", "à collerette"
        ],
        OrganismType.OMNIVORE: [
            "brun", "noir", "gris", "beige", "roux", "blanc", "tacheté", "rayé",
            "bicolore", "à masque", "à marques faciales", "à ventre clair", "à dos foncé", "uniforme"
        ]
    }
    
    # Habitats préférés par type d'organisme
    HABITATS = {
        OrganismType.UNICELLULAR: [
            "aquatique", "terrestre humide", "aérien", "extrêmophile", "symbiotique",
            "parasitique", "commensaliste", "thermophile", "psychrophile", "halophile"
        ],
        OrganismType.PLANT: [
            "forestier", "prairial", "désertique", "montagneux", "côtier", "marécageux",
            "aquatique", "tropical", "tempéré", "boréal", "alpin", "rupestre", "épiphyte"
        ],
        OrganismType.HERBIVORE: [
            "forestier", "prairial", "désertique", "montagneux", "côtier", "marécageux",
            "aquatique", "arboricole", "fouisseur", "nocturne", "diurne", "migrateur", "territorial"
        ],
        OrganismType.CARNIVORE: [
            "forestier", "prairial", "désertique", "montagneux", "côtier", "marécageux",
            "aquatique", "arboricole", "fouisseur", "nocturne", "diurne", "territorial", "nomade"
        ],
        OrganismType.OMNIVORE: [
            "forestier", "prairial", "désertique", "montagneux", "côtier", "marécageux",
            "aquatique", "arboricole", "fouisseur", "nocturne", "diurne", "adaptable", "opportuniste"
        ]
    }
    
    # Comportements spécifiques par type d'organisme
    BEHAVIORS = {
        OrganismType.UNICELLULAR: [
            "mobile", "sessile", "colonial", "phototrope", "chimiotrope", "symbiotique",
            "parasitique", "saprophyte", "aérobie", "anaérobie", "sporulant", "enkysté"
        ],
        OrganismType.PLANT: [
            "à croissance rapide", "à croissance lente", "à floraison printanière", "à floraison estivale",
            "à floraison automnale", "à floraison hivernale", "à floraison nocturne", "à pollinisation par insectes",
            "à pollinisation par le vent", "à dispersion par animaux", "à dispersion par le vent", "à dispersion explosive"
        ],
        OrganismType.HERBIVORE: [
            "grégaire", "solitaire", "territorial", "migrateur", "diurne", "nocturne", "crépusculaire",
            "brouteur", "fouisseur", "arboricole", "coureur", "sauteur", "nageur", "hibernant", "estivant"
        ],
        OrganismType.CARNIVORE: [
            "chasseur solitaire", "chasseur en meute", "embusqué", "poursuiveur", "charognard",
            "territorial", "nomade", "diurne", "nocturne", "crépusculaire", "arboricole", "terrestre",
            "aquatique", "hibernant", "migrateur", "opportuniste", "spécialiste"
        ],
        OrganismType.OMNIVORE: [
            "opportuniste", "collecteur", "stockeur", "social", "solitaire", "territorial",
            "nomade", "diurne", "nocturne", "arboricole", "terrestre", "fouisseur", "grimpeur",
            "adaptable", "innovateur", "imitateur", "utilisateur d'outils"
        ]
    }
    
    # Adaptations spéciales par type d'organisme
    SPECIAL_ADAPTATIONS = {
        OrganismType.UNICELLULAR: [
            "résistant à la chaleur", "résistant au froid", "résistant à la dessiccation", "résistant aux UV",
            "résistant aux antibiotiques", "bioluminescent", "magnétotactique", "fixateur d'azote",
            "producteur de toxines", "formant des biofilms", "à métabolisme versatile", "à reproduction rapide"
        ],
        OrganismType.PLANT: [
            "résistant à la sécheresse", "résistant au gel", "résistant aux inondations", "résistant aux incendies",
            "carnivore", "parasite", "épiphyte", "à symbiose mycorhizienne", "à symbiose bactérienne",
            "à latex toxique", "à alcaloïdes défensifs", "à épines", "à crochets", "à poils urticants"
        ],
        OrganismType.HERBIVORE: [
            "résistant aux toxines", "digesteur efficace", "ruminant", "à estomacs multiples",
            "à camouflage", "à mimétisme", "à coloration aposématique", "à défense chimique",
            "à défense mécanique", "à hibernation", "à estivation", "à migration saisonnière",
            "à pelage/plumage changeant", "à communication complexe", "à soins parentaux"
        ],
        OrganismType.CARNIVORE: [
            "à venin", "à salive antiseptique", "à vision nocturne", "à écholocation",
            "à électroréception", "à thermoréception", "à camouflage", "à mimétisme",
            "à coloration aposématique", "à défense chimique", "à défense mécanique",
            "à hibernation", "à estivation", "à migration saisonnière", "à stratégie de chasse spécialisée"
        ],
        OrganismType.OMNIVORE: [
            "à digestion polyvalente", "à dentition variée", "à manipulation précise",
            "à apprentissage rapide", "à mémoire développée", "à communication complexe",
            "à fabrication d'outils", "à résolution de problèmes", "à adaptation culturelle",
            "à soins parentaux prolongés", "à structure sociale complexe", "à transmission de connaissances"
        ]
    }
    
    def __init__(self, organism_type: OrganismType):
        """Initialise des traits aléatoires pour une espèce"""
        self.physical_traits = random.sample(self.PHYSICAL_TRAITS[organism_type], 
                                           k=random.randint(1, 3))
        self.color = random.choice(self.COLORS[organism_type])
        self.habitat = random.choice(self.HABITATS[organism_type])
        self.behavior = random.sample(self.BEHAVIORS[organism_type], 
                                     k=random.randint(1, 2))
        self.special_adaptation = random.choice(self.SPECIAL_ADAPTATIONS[organism_type])
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit les traits en dictionnaire pour la sérialisation"""
        return {
            'physical_traits': self.physical_traits,
            'color': self.color,
            'habitat': self.habitat,
            'behavior': self.behavior,
            'special_adaptation': self.special_adaptation
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], organism_type: OrganismType) -> 'SpeciesTraits':
        """Crée une instance à partir d'un dictionnaire"""
        traits = cls(organism_type)
        traits.physical_traits = data.get('physical_traits', traits.physical_traits)
        traits.color = data.get('color', traits.color)
        traits.habitat = data.get('habitat', traits.habitat)
        traits.behavior = data.get('behavior', traits.behavior)
        traits.special_adaptation = data.get('special_adaptation', traits.special_adaptation)
        return traits
        
    def get_description(self) -> str:
        """Génère une description textuelle des traits de l'espèce"""
        physical = ", ".join(self.physical_traits)
        behavior = ", ".join(self.behavior)
        
        return f"Organisme {self.color}, {physical}. Habite en milieu {self.habitat}. " \
               f"Comportement: {behavior}. Adaptation spéciale: {self.special_adaptation}."


class SpeciesRecord:
    """Classe représentant les informations complètes sur une espèce"""
    
    def __init__(self, species_id: str, scientific_name: str, common_name: str, 
                 organism_type: OrganismType, parent_species_id: Optional[str] = None):
        self.species_id = species_id
        self.scientific_name = scientific_name
        self.common_name = common_name
        self.organism_type = organism_type
        self.parent_species_id = parent_species_id
        self.discovery_date = datetime.datetime.now().isoformat()
        self.traits = SpeciesTraits(organism_type)
        self.population_count = 1
        self.max_population = 1
        self.extinct = False
        self.extinction_date = None
        self.generation = 1
        self.max_generation = 1
        self.mutation_count = 0
        self.child_species = []
        self.notable_adaptations = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'enregistrement en dictionnaire pour la sérialisation"""
        return {
            'species_id': self.species_id,
            'scientific_name': self.scientific_name,
            'common_name': self.common_name,
            'organism_type': self.organism_type.value,
            'parent_species_id': self.parent_species_id,
            'discovery_date': self.discovery_date,
            'traits': self.traits.to_dict(),
            'population_count': self.population_count,
            'max_population': self.max_population,
            'extinct': self.extinct,
            'extinction_date': self.extinction_date,
            'generation': self.generation,
            'max_generation': self.max_generation,
            'mutation_count': self.mutation_count,
            'child_species': self.child_species,
            'notable_adaptations': self.notable_adaptations
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SpeciesRecord':
        """Crée une instance à partir d'un dictionnaire"""
        organism_type = OrganismType(data['organism_type'])
        
        record = cls(
            species_id=data['species_id'],
            scientific_name=data['scientific_name'],
            common_name=data['common_name'],
            organism_type=organism_type,
            parent_species_id=data.get('parent_species_id')
        )
        
        record.discovery_date = data.get('discovery_date', record.discovery_date)
        record.traits = SpeciesTraits.from_dict(data.get('traits', {}), organism_type)
        record.population_count = data.get('population_count', 1)
        record.max_population = data.get('max_population', 1)
        record.extinct = data.get('extinct', False)
        record.extinction_date = data.get('extinction_date')
        record.generation = data.get('generation', 1)
        record.max_generation = data.get('max_generation', 1)
        record.mutation_count = data.get('mutation_count', 0)
        record.child_species = data.get('child_species', [])
        record.notable_adaptations = data.get('notable_adaptations', [])
        
        return record
    
    def update_population(self, count: int) -> None:
        """Met à jour le compteur de population"""
        self.population_count = count
        if count > self.max_population:
            self.max_population = count
        if count == 0 and not self.extinct:
            self.extinct = True
            self.extinction_date = datetime.datetime.now().isoformat()
            
    def update_generation(self, generation: int) -> None:
        """Met à jour la génération actuelle"""
        self.generation = generation
        if generation > self.max_generation:
            self.max_generation = generation
            
    def add_child_species(self, child_id: str) -> None:
        """Ajoute une espèce enfant à la liste"""
        if child_id not in self.child_species:
            self.child_species.append(child_id)
            
    def add_notable_adaptation(self, adaptation: str) -> None:
        """Ajoute une adaptation notable à l'espèce"""
        if adaptation not in self.notable_adaptations:
            self.notable_adaptations.append(adaptation)
            
    def get_full_description(self) -> str:
        """Génère une description complète de l'espèce"""
        status = "Éteinte" if self.extinct else "Vivante"
        population = f"Population actuelle: {self.population_count}, Maximum: {self.max_population}"
        generation = f"Génération actuelle: {self.generation}, Maximum: {self.max_generation}"
        
        description = [
            f"Nom scientifique: {self.scientific_name}",
            f"Nom commun: {self.common_name}",
            f"Statut: {status}",
            f"Type: {self.get_organism_type_name()}",
            f"Découverte: {self.format_date(self.discovery_date)}",
            population,
            generation,
            f"Description: {self.traits.get_description()}"
        ]
        
        if self.parent_species_id:
            description.append(f"Espèce parente: {self.parent_species_id}")
            
        if self.child_species:
            description.append(f"Espèces dérivées: {len(self.child_species)}")
            
        if self.notable_adaptations:
            adaptations = ", ".join(self.notable_adaptations)
            description.append(f"Adaptations notables: {adaptations}")
            
        if self.extinct and self.extinction_date:
            description.append(f"Date d'extinction: {self.format_date(self.extinction_date)}")
            
        return "\n".join(description)
    
    def get_organism_type_name(self) -> str:
        """Retourne le nom du type d'organisme"""
        names = {
            OrganismType.UNICELLULAR: "Unicellulaire",
            OrganismType.PLANT: "Plante",
            OrganismType.HERBIVORE: "Herbivore",
            OrganismType.CARNIVORE: "Carnivore",
            OrganismType.OMNIVORE: "Omnivore"
        }
        return names.get(self.organism_type, "Inconnu")
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Formate une date ISO en format lisible"""
        try:
            date = datetime.datetime.fromisoformat(date_str)
            return date.strftime("%d/%m/%Y %H:%M:%S")
        except:
            return date_str


class SpeciesRegistry:
    """Classe principale pour gérer le registre des espèces"""
    
    def __init__(self, save_file: str = "species_registry.json"):
        self.species = {}  # Dict[species_id, SpeciesRecord]
        self.save_file = save_file
        self.load_registry()
        
    def register_species(self, species_id: str, scientific_name: str, common_name: str, 
                        organism_type: OrganismType, parent_species_id: Optional[str] = None) -> SpeciesRecord:
        """Enregistre une nouvelle espèce dans le registre"""
        # Vérifier si l'espèce existe déjà
        if species_id in self.species:
            # Mettre à jour la population
            self.species[species_id].update_population(self.species[species_id].population_count + 1)
            return self.species[species_id]
            
        # Créer un nouvel enregistrement
        record = SpeciesRecord(
            species_id=species_id,
            scientific_name=scientific_name,
            common_name=common_name,
            organism_type=organism_type,
            parent_species_id=parent_species_id
        )
        
        # Ajouter au registre
        self.species[species_id] = record
        
        # Mettre à jour l'espèce parente si elle existe
        if parent_species_id and parent_species_id in self.species:
            self.species[parent_species_id].add_child_species(species_id)
            
        # Sauvegarder le registre
        self.save_registry()
        
        return record
    
    def update_species(self, species_id: str, population: int = None, 
                      generation: int = None, adaptation: str = None) -> None:
        """Met à jour les informations d'une espèce existante"""
        if species_id not in self.species:
            return
            
        record = self.species[species_id]
        
        if population is not None:
            record.update_population(population)
            
        if generation is not None:
            record.update_generation(generation)
            
        if adaptation is not None:
            record.add_notable_adaptation(adaptation)
            
        # Sauvegarder le registre après des modifications importantes
        if population == 0 or adaptation is not None:
            self.save_registry()
    
    def get_species(self, species_id: str) -> Optional[SpeciesRecord]:
        """Récupère les informations d'une espèce par son ID"""
        return self.species.get(species_id)
    
    def get_all_species(self) -> List[SpeciesRecord]:
        """Récupère toutes les espèces enregistrées"""
        return list(self.species.values())
    
    def get_living_species(self) -> List[SpeciesRecord]:
        """Récupère toutes les espèces vivantes"""
        return [s for s in self.species.values() if not s.extinct]
    
    def get_extinct_species(self) -> List[SpeciesRecord]:
        """Récupère toutes les espèces éteintes"""
        return [s for s in self.species.values() if s.extinct]
    
    def get_species_by_type(self, organism_type: OrganismType) -> List[SpeciesRecord]:
        """Récupère toutes les espèces d'un type donné"""
        return [s for s in self.species.values() if s.organism_type == organism_type]
    
    def get_species_count(self) -> Dict[str, int]:
        """Récupère le nombre d'espèces par type et statut"""
        counts = {
            "total": len(self.species),
            "living": len(self.get_living_species()),
            "extinct": len(self.get_extinct_species())
        }
        
        # Compter par type d'organisme
        for org_type in OrganismType:
            type_name = org_type.name.lower()
            counts[type_name] = len(self.get_species_by_type(org_type))
            counts[f"{type_name}_living"] = len([s for s in self.species.values() 
                                              if s.organism_type == org_type and not s.extinct])
            
        return counts
    
    def get_evolutionary_tree(self, root_species_id: Optional[str] = None) -> Dict[str, Any]:
        """Génère un arbre évolutif à partir d'une espèce racine ou de toutes les espèces sans parent"""
        if root_species_id:
            if root_species_id not in self.species:
                return {}
            roots = [root_species_id]
        else:
            # Trouver toutes les espèces sans parent
            roots = [s.species_id for s in self.species.values() if not s.parent_species_id]
            
        tree = {}
        for root in roots:
            tree[root] = self._build_tree_branch(root)
            
        return tree
    
    def _build_tree_branch(self, species_id: str) -> Dict[str, Any]:
        """Construit récursivement une branche de l'arbre évolutif"""
        if species_id not in self.species:
            return {}
            
        species = self.species[species_id]
        branch = {
            "name": species.scientific_name,
            "common_name": species.common_name,
            "extinct": species.extinct,
            "type": species.organism_type.name,
            "children": {}
        }
        
        for child_id in species.child_species:
            if child_id in self.species and child_id != species_id:  # Éviter les boucles
                branch["children"][child_id] = self._build_tree_branch(child_id)
                
        return branch
    
    def save_registry(self) -> bool:
        """Sauvegarde le registre des espèces dans un fichier JSON"""
        try:
            data = {species_id: record.to_dict() for species_id, record in self.species.items()}
            
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du registre des espèces: {e}")
            return False
    
    def load_registry(self) -> bool:
        """Charge le registre des espèces depuis un fichier JSON"""
        if not os.path.exists(self.save_file):
            return False
            
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.species = {species_id: SpeciesRecord.from_dict(record_data) 
                           for species_id, record_data in data.items()}
                
            return True
        except Exception as e:
            print(f"Erreur lors du chargement du registre des espèces: {e}")
            return False
    
    def generate_report(self) -> str:
        """Génère un rapport textuel sur l'état des espèces"""
        counts = self.get_species_count()
        
        report = [
            "=== RAPPORT DU REGISTRE DES ESPÈCES ===",
            f"Total des espèces: {counts['total']}",
            f"Espèces vivantes: {counts['living']}",
            f"Espèces éteintes: {counts['extinct']}",
            "",
            "--- Par type d'organisme ---"
        ]
        
        for org_type in OrganismType:
            type_name = org_type.name.lower()
            type_display = org_type.name.capitalize()
            report.append(f"{type_display}: {counts[type_name]} (Vivantes: {counts[f'{type_name}_living']})")
            
        report.append("")
        report.append("--- Espèces récemment découvertes ---")
        
        # Trier par date de découverte (les plus récentes d'abord)
        recent_species = sorted(
            self.get_living_species(), 
            key=lambda s: s.discovery_date, 
            reverse=True
        )[:5]
        
        for species in recent_species:
            report.append(f"{species.scientific_name} ({species.common_name})")
            
        report.append("")
        report.append("--- Espèces récemment éteintes ---")
        
        # Trier par date d'extinction (les plus récentes d'abord)
        recent_extinct = sorted(
            self.get_extinct_species(),
            key=lambda s: s.extinction_date if s.extinction_date else "",
            reverse=True
        )[:5]
        
        for species in recent_extinct:
            report.append(f"{species.scientific_name} ({species.common_name})")
            
        return "\n".join(report)


# Registre global des espèces
global_species_registry = SpeciesRegistry()