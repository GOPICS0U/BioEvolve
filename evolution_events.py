"""
Module d'événements évolutifs pour BioEvolve
Implémente des mécanismes évolutifs réalistes basés sur les principes scientifiques de l'évolution
"""

import random
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set, Any
import uuid

class EvolutionaryMechanism(Enum):
    """Mécanismes évolutifs fondamentaux selon la théorie synthétique de l'évolution."""
    MUTATION = 0                # Changements aléatoires dans le génome
    NATURAL_SELECTION = 1       # Sélection des individus les mieux adaptés
    GENETIC_DRIFT = 2           # Variations aléatoires des fréquences alléliques
    GENE_FLOW = 3               # Échange de gènes entre populations
    SEXUAL_SELECTION = 4        # Sélection basée sur l'accès aux partenaires
    COEVOLUTION = 5             # Évolution conjointe d'espèces en interaction
    SYMBIOGENESIS = 6           # Fusion d'organismes différents (endosymbiose)
    HORIZONTAL_GENE_TRANSFER = 7 # Transfert de gènes entre espèces différentes

class SpeciationMode(Enum):
    """Modes de spéciation selon la théorie de l'évolution."""
    ALLOPATRIC = 0      # Spéciation par isolement géographique
    SYMPATRIC = 1       # Spéciation sans isolement géographique
    PARAPATRIC = 2      # Spéciation avec isolement partiel
    PERIPATRIC = 3      # Spéciation par effet fondateur
    HYBRID = 4          # Spéciation par hybridation

class EvolutionaryEvent:
    """Représente un événement évolutif significatif dans la simulation."""
    
    def __init__(self, 
                 event_type: str,
                 year: int, 
                 day: int,
                 species_id: str,
                 mechanism: EvolutionaryMechanism,
                 description: str,
                 affected_organisms: List[str] = None,
                 parent_species: str = None,
                 new_species: str = None,
                 speciation_mode: SpeciationMode = None,
                 environmental_factors: Dict[str, float] = None,
                 genetic_changes: Dict[str, Any] = None):
        """
        Initialise un événement évolutif.
        
        Args:
            event_type: Type d'événement (spéciation, extinction, adaptation, etc.)
            year: Année de simulation où l'événement s'est produit
            day: Jour de l'année où l'événement s'est produit
            species_id: ID de l'espèce concernée
            mechanism: Mécanisme évolutif principal impliqué
            description: Description textuelle de l'événement
            affected_organisms: Liste des IDs des organismes affectés
            parent_species: ID de l'espèce parente (pour la spéciation)
            new_species: ID de la nouvelle espèce (pour la spéciation)
            speciation_mode: Mode de spéciation (pour la spéciation)
            environmental_factors: Facteurs environnementaux impliqués
            genetic_changes: Changements génétiques significatifs
        """
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.year = year
        self.day = day
        self.species_id = species_id
        self.mechanism = mechanism
        self.description = description
        self.affected_organisms = affected_organisms or []
        self.parent_species = parent_species
        self.new_species = new_species
        self.speciation_mode = speciation_mode
        self.environmental_factors = environmental_factors or {}
        self.genetic_changes = genetic_changes or {}
        self.timestamp = f"Année {year}, Jour {day}"

class EvolutionaryRegistry:
    """Registre des événements évolutifs et des espèces dans la simulation."""
    
    def __init__(self):
        """Initialise le registre évolutif."""
        self.events = []
        self.species_registry = {}  # {species_id: species_data}
        self.evolutionary_milestones = []
        self.extinct_species = set()
        self.speciation_events = []
        self.adaptation_events = []
        self.extinction_events = []
        
    def add_event(self, event: EvolutionaryEvent):
        """Ajoute un événement au registre."""
        self.events.append(event)
        
        # Catégoriser l'événement
        if event.event_type == "speciation":
            self.speciation_events.append(event)
        elif event.event_type == "adaptation":
            self.adaptation_events.append(event)
        elif event.event_type == "extinction":
            self.extinction_events.append(event)
            self.extinct_species.add(event.species_id)
            
        # Ajouter aux jalons évolutifs si c'est un événement significatif
        if self._is_milestone(event):
            self.evolutionary_milestones.append(event)
    
    def register_species(self, species_id: str, data: Dict):
        """Enregistre une nouvelle espèce dans le registre."""
        self.species_registry[species_id] = data
    
    def get_species_data(self, species_id: str) -> Optional[Dict]:
        """Récupère les données d'une espèce."""
        return self.species_registry.get(species_id)
    
    def get_events_by_type(self, event_type: str) -> List[EvolutionaryEvent]:
        """Récupère tous les événements d'un type spécifique."""
        return [event for event in self.events if event.event_type == event_type]
    
    def get_events_by_mechanism(self, mechanism: EvolutionaryMechanism) -> List[EvolutionaryEvent]:
        """Récupère tous les événements impliquant un mécanisme spécifique."""
        return [event for event in self.events if event.mechanism == mechanism]
    
    def get_events_by_species(self, species_id: str) -> List[EvolutionaryEvent]:
        """Récupère tous les événements concernant une espèce spécifique."""
        return [event for event in self.events if event.species_id == species_id]
    
    def get_species_lineage(self, species_id: str) -> List[str]:
        """Retrace la lignée d'une espèce jusqu'à son ancêtre le plus ancien."""
        lineage = [species_id]
        current_id = species_id
        
        while True:
            # Chercher l'événement de spéciation qui a créé cette espèce
            parent_event = next((e for e in self.speciation_events 
                               if e.new_species == current_id), None)
            
            if not parent_event or not parent_event.parent_species:
                break
                
            current_id = parent_event.parent_species
            lineage.append(current_id)
        
        return lineage
    
    def _is_milestone(self, event: EvolutionaryEvent) -> bool:
        """Détermine si un événement est un jalon évolutif significatif."""
        # Les événements de spéciation sont toujours des jalons
        if event.event_type == "speciation":
            return True
            
        # Les extinctions d'espèces établies sont des jalons
        if event.event_type == "extinction" and len(self.get_events_by_species(event.species_id)) > 5:
            return True
            
        # Les adaptations majeures sont des jalons
        if event.event_type == "adaptation" and event.genetic_changes and len(event.genetic_changes) > 3:
            return True
            
        return False

class EvolutionaryPressure:
    """Représente une pression évolutive agissant sur les organismes."""
    
    def __init__(self, 
                 name: str,
                 intensity: float,
                 target_traits: List[str],
                 direction: float,  # -1.0 à 1.0, négatif = sélection contre, positif = sélection pour
                 environmental_source: str = None,
                 description: str = None):
        """
        Initialise une pression évolutive.
        
        Args:
            name: Nom de la pression évolutive
            intensity: Intensité de la pression (0.0 à 1.0)
            target_traits: Liste des traits affectés par cette pression
            direction: Direction de la sélection (-1.0 à 1.0)
            environmental_source: Source environnementale de cette pression
            description: Description textuelle de la pression
        """
        self.name = name
        self.intensity = max(0.0, min(1.0, intensity))
        self.target_traits = target_traits
        self.direction = max(-1.0, min(1.0, direction))
        self.environmental_source = environmental_source
        self.description = description or f"Pression évolutive {name}"
        
    def calculate_effect(self, trait_value: float, trait_optimum: float = 0.5) -> float:
        """
        Calcule l'effet de cette pression sur un trait spécifique.
        
        Args:
            trait_value: Valeur actuelle du trait (0.0 à 1.0)
            trait_optimum: Valeur optimale du trait sous cette pression (0.0 à 1.0)
            
        Returns:
            float: Coefficient de sélection (-1.0 à 1.0)
        """
        # Distance à l'optimum
        distance = abs(trait_value - trait_optimum)
        
        # L'effet dépend de la distance à l'optimum et de l'intensité de la pression
        effect = (1.0 - distance) * self.intensity * self.direction
        
        return effect

class EvolutionaryPressureSystem:
    """Système gérant l'ensemble des pressions évolutives dans l'environnement."""
    
    def __init__(self):
        """Initialise le système de pressions évolutives."""
        self.pressures = {}  # {pressure_name: EvolutionaryPressure}
        self.regional_pressures = {}  # {region_id: {pressure_name: EvolutionaryPressure}}
        self.temporal_pressures = {}  # {(year, season): {pressure_name: EvolutionaryPressure}}
        
    def add_pressure(self, pressure: EvolutionaryPressure, region_id: str = None, 
                    temporal_key: Tuple[int, int] = None):
        """
        Ajoute une pression évolutive au système.
        
        Args:
            pressure: La pression évolutive à ajouter
            region_id: ID de la région où cette pression s'applique (None = globale)
            temporal_key: Tuple (année, saison) où cette pression s'applique (None = permanente)
        """
        # Ajouter aux pressions globales
        self.pressures[pressure.name] = pressure
        
        # Ajouter aux pressions régionales si spécifié
        if region_id:
            if region_id not in self.regional_pressures:
                self.regional_pressures[region_id] = {}
            self.regional_pressures[region_id][pressure.name] = pressure
            
        # Ajouter aux pressions temporelles si spécifié
        if temporal_key:
            if temporal_key not in self.temporal_pressures:
                self.temporal_pressures[temporal_key] = {}
            self.temporal_pressures[temporal_key][pressure.name] = pressure
    
    def get_active_pressures(self, region_id: str = None, year: int = None, 
                           season: int = None) -> Dict[str, EvolutionaryPressure]:
        """
        Récupère toutes les pressions actives pour une région et un moment donnés.
        
        Args:
            region_id: ID de la région (None = toutes les régions)
            year: Année de simulation (None = toutes les années)
            season: Saison (None = toutes les saisons)
            
        Returns:
            Dict[str, EvolutionaryPressure]: Dictionnaire des pressions actives
        """
        # Commencer avec les pressions globales
        active_pressures = self.pressures.copy()
        
        # Ajouter les pressions régionales si une région est spécifiée
        if region_id and region_id in self.regional_pressures:
            active_pressures.update(self.regional_pressures[region_id])
            
        # Ajouter les pressions temporelles si un moment est spécifié
        if year is not None and season is not None:
            temporal_key = (year, season)
            if temporal_key in self.temporal_pressures:
                active_pressures.update(self.temporal_pressures[temporal_key])
                
        return active_pressures
    
    def calculate_selection_coefficient(self, organism, region_id: str = None, 
                                      year: int = None, season: int = None) -> float:
        """
        Calcule le coefficient de sélection global pour un organisme.
        
        Args:
            organism: L'organisme à évaluer
            region_id: ID de la région où se trouve l'organisme
            year: Année de simulation actuelle
            season: Saison actuelle
            
        Returns:
            float: Coefficient de sélection global (-1.0 à 1.0)
        """
        active_pressures = self.get_active_pressures(region_id, year, season)
        
        if not active_pressures:
            return 0.0  # Pas de pression, pas d'effet
            
        total_effect = 0.0
        pressure_count = 0
        
        for pressure in active_pressures.values():
            # Vérifier si l'organisme possède les traits ciblés par cette pression
            for trait in pressure.target_traits:
                if hasattr(organism.phenotype, trait):
                    trait_value = getattr(organism.phenotype, trait)
                    # Normaliser la valeur du trait si nécessaire
                    if isinstance(trait_value, (int, float)) and trait_value > 1.0:
                        # Supposer que les traits sont normalisés entre 0 et 1
                        # Si ce n'est pas le cas, il faudrait connaître les bornes pour chaque trait
                        trait_value = trait_value / 10.0  # Valeur arbitraire, à ajuster
                        
                    effect = pressure.calculate_effect(trait_value)
                    total_effect += effect
                    pressure_count += 1
        
        # Calculer l'effet moyen
        if pressure_count > 0:
            return total_effect / pressure_count
        else:
            return 0.0

# Exemples de pressions évolutives prédéfinies
def create_climate_change_pressure(intensity: float = 0.7, direction: float = -0.8) -> EvolutionaryPressure:
    """Crée une pression évolutive liée au changement climatique."""
    return EvolutionaryPressure(
        name="climate_change",
        intensity=intensity,
        target_traits=["temperature_tolerance", "water_efficiency", "metabolism_rate"],
        direction=direction,
        environmental_source="global_temperature",
        description="Pression due au changement climatique global"
    )

def create_predation_pressure(intensity: float = 0.8, direction: float = 0.9) -> EvolutionaryPressure:
    """Crée une pression évolutive liée à la prédation."""
    return EvolutionaryPressure(
        name="predation",
        intensity=intensity,
        target_traits=["speed", "camouflage", "defense_power", "sensory_acuity"],
        direction=direction,
        environmental_source="predator_density",
        description="Pression due à la présence de prédateurs"
    )

def create_resource_competition_pressure(intensity: float = 0.6, direction: float = 0.7) -> EvolutionaryPressure:
    """Crée une pression évolutive liée à la compétition pour les ressources."""
    return EvolutionaryPressure(
        name="resource_competition",
        intensity=intensity,
        target_traits=["metabolism_efficiency", "foraging_ability", "growth_rate"],
        direction=direction,
        environmental_source="resource_scarcity",
        description="Pression due à la compétition pour les ressources limitées"
    )

def create_disease_pressure(intensity: float = 0.5, direction: float = 0.6) -> EvolutionaryPressure:
    """Crée une pression évolutive liée aux maladies."""
    return EvolutionaryPressure(
        name="disease",
        intensity=intensity,
        target_traits=["immune_system", "toxin_resistance", "metabolism_rate"],
        direction=direction,
        environmental_source="pathogen_prevalence",
        description="Pression due à la présence de pathogènes"
    )

def create_sexual_selection_pressure(intensity: float = 0.7, direction: float = 0.9) -> EvolutionaryPressure:
    """Crée une pression évolutive liée à la sélection sexuelle."""
    return EvolutionaryPressure(
        name="sexual_selection",
        intensity=intensity,
        target_traits=["display_traits", "size", "strength", "fertility"],
        direction=direction,
        environmental_source="mate_competition",
        description="Pression due à la compétition pour les partenaires sexuels"
    )

# Fonctions utilitaires pour l'analyse évolutive
def calculate_genetic_distance(genome1, genome2) -> float:
    """
    Calcule la distance génétique entre deux génomes.
    
    Args:
        genome1: Premier génome
        genome2: Deuxième génome
        
    Returns:
        float: Distance génétique (0.0 = identiques, 1.0 = complètement différents)
    """
    if not hasattr(genome1, 'chromosomes') or not hasattr(genome2, 'chromosomes'):
        return 1.0  # Distance maximale si les génomes n'ont pas de chromosomes
        
    total_genes = 0
    different_genes = 0
    
    # Pour chaque chromosome présent dans les deux génomes
    for i in range(min(len(genome1.chromosomes), len(genome2.chromosomes))):
        chrom1 = genome1.chromosomes[i]
        chrom2 = genome2.chromosomes[i]
        
        # Ensemble des gènes présents dans l'un ou l'autre des chromosomes
        all_genes = set(chrom1.genes.keys()) | set(chrom2.genes.keys())
        total_genes += len(all_genes)
        
        for gene_id in all_genes:
            # Si le gène est présent dans un seul chromosome, c'est une différence
            if (gene_id in chrom1.genes) != (gene_id in chrom2.genes):
                different_genes += 1
            # Si le gène est présent dans les deux, comparer les valeurs
            elif gene_id in chrom1.genes and gene_id in chrom2.genes:
                gene1 = chrom1.genes[gene_id]
                gene2 = chrom2.genes[gene_id]
                
                # Si la différence de valeur est significative, c'est une différence
                if abs(gene1.value - gene2.value) > 0.2:  # Seuil arbitraire
                    different_genes += 1
    
    # Si aucun gène n'a été comparé, retourner la distance maximale
    if total_genes == 0:
        return 1.0
        
    return different_genes / total_genes

def detect_speciation_event(parent_species, offspring_genome, genetic_distance_threshold: float = 0.3) -> bool:
    """
    Détecte si un événement de spéciation s'est produit.
    
    Args:
        parent_species: Espèce parente
        offspring_genome: Génome de la descendance
        genetic_distance_threshold: Seuil de distance génétique pour la spéciation
        
    Returns:
        bool: True si une spéciation s'est produite, False sinon
    """
    # Calculer la distance génétique
    distance = calculate_genetic_distance(parent_species.genome, offspring_genome)
    
    # Si la distance est supérieure au seuil, c'est une spéciation
    return distance > genetic_distance_threshold

def determine_speciation_mode(parent_species, offspring, world) -> SpeciationMode:
    """
    Détermine le mode de spéciation le plus probable.
    
    Args:
        parent_species: Espèce parente
        offspring: Organisme descendant
        world: Monde de simulation
        
    Returns:
        SpeciationMode: Mode de spéciation le plus probable
    """
    # Vérifier si les populations sont géographiquement isolées
    if hasattr(world, 'get_species_distribution'):
        parent_regions = world.get_species_distribution(parent_species.species_id)
        offspring_region = world.get_region_at_position(offspring.position)
        
        # Si le descendant est dans une région où le parent n'est pas présent
        if offspring_region not in parent_regions:
            # Si la population du descendant est petite, c'est probablement péripatrique
            if len(world.get_organisms_by_species(offspring.species_id)) < 5:
                return SpeciationMode.PERIPATRIC
            else:
                return SpeciationMode.ALLOPATRIC
    
    # Si les deux espèces coexistent dans la même région
    if hasattr(offspring, 'is_hybrid') and offspring.is_hybrid:
        return SpeciationMode.HYBRID
    
    # Par défaut, considérer comme sympatrique
    return SpeciationMode.SYMPATRIC

def analyze_adaptation(species, previous_generation, current_generation, environment) -> Dict[str, Any]:
    """
    Analyse les adaptations d'une espèce entre deux générations.
    
    Args:
        species: Espèce à analyser
        previous_generation: Organismes de la génération précédente
        current_generation: Organismes de la génération actuelle
        environment: Environnement actuel
        
    Returns:
        Dict[str, Any]: Informations sur les adaptations détectées
    """
    if not previous_generation or not current_generation:
        return {}
        
    adaptations = {}
    
    # Calculer les valeurs moyennes des traits pour chaque génération
    prev_traits = {}
    curr_traits = {}
    
    for organism in previous_generation:
        for trait_name in dir(organism.phenotype):
            if not trait_name.startswith('_') and isinstance(getattr(organism.phenotype, trait_name), (int, float)):
                if trait_name not in prev_traits:
                    prev_traits[trait_name] = []
                prev_traits[trait_name].append(getattr(organism.phenotype, trait_name))
    
    for organism in current_generation:
        for trait_name in dir(organism.phenotype):
            if not trait_name.startswith('_') and isinstance(getattr(organism.phenotype, trait_name), (int, float)):
                if trait_name not in curr_traits:
                    curr_traits[trait_name] = []
                curr_traits[trait_name].append(getattr(organism.phenotype, trait_name))
    
    # Calculer les moyennes
    prev_means = {trait: sum(values)/len(values) for trait, values in prev_traits.items() if values}
    curr_means = {trait: sum(values)/len(values) for trait, values in curr_traits.items() if values}
    
    # Détecter les changements significatifs
    for trait in set(prev_means.keys()) & set(curr_means.keys()):
        change = curr_means[trait] - prev_means[trait]
        
        # Si le changement est significatif (seuil arbitraire)
        if abs(change) > 0.1 * prev_means[trait]:
            adaptations[trait] = {
                "previous_value": prev_means[trait],
                "current_value": curr_means[trait],
                "change": change,
                "percent_change": (change / prev_means[trait]) * 100
            }
    
    return adaptations