"""
Module d'évolution avancée pour BioEvolve
Implémente des mécanismes d'évolution complexes comme la multicellularité et le développement neuronal
basés sur les principes scientifiques de l'évolution
"""

import random
import math
import numpy as np
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Set, Any, Callable
import uuid

class EvolutionaryTransition(Enum):
    """Transitions majeures dans l'histoire de l'évolution."""
    REPLICATION_TO_POPULATIONS = auto()  # Des réplicateurs aux populations
    INDEPENDENT_REPLICATORS_TO_CHROMOSOMES = auto()  # Des réplicateurs indépendants aux chromosomes
    RNA_TO_DNA_PROTEINS = auto()  # De l'ARN à l'ADN et aux protéines
    PROKARYOTES_TO_EUKARYOTES = auto()  # Des procaryotes aux eucaryotes
    ASEXUAL_TO_SEXUAL = auto()  # De la reproduction asexuée à la reproduction sexuée
    UNICELLULAR_TO_MULTICELLULAR = auto()  # De l'unicellularité à la multicellularité
    SOLITARY_TO_COLONIAL = auto()  # Des individus solitaires aux colonies
    PROTOORGANISMS_TO_ORGANISMS = auto()  # Des proto-organismes aux organismes avec différenciation cellulaire
    NONSOCIAL_TO_EUSOCIAL = auto()  # Des organismes non sociaux aux organismes eusociaux
    PRIMATE_TO_HUMAN = auto()  # Des primates aux humains (langage, culture)

class MulticellularityType(Enum):
    """Types de multicellularité selon leur origine évolutive."""
    NONE = 0  # Unicellulaire
    AGGREGATIVE = 1  # Agrégation de cellules (ex: Dictyostelium)
    CLONAL = 2  # Division cellulaire sans séparation (ex: algues)
    SYNCYTIAL = 3  # Cellules multinucléées (ex: champignons)
    COLONIAL = 4  # Colonies de cellules (ex: Volvox)
    COMPLEX = 5  # Organismes multicellulaires complexes avec différenciation cellulaire

class CellType(Enum):
    """Types de cellules dans un organisme multicellulaire."""
    STEM = 0  # Cellules souches
    EPITHELIAL = 1  # Cellules épithéliales (peau, muqueuses)
    CONNECTIVE = 2  # Cellules du tissu conjonctif
    MUSCLE = 3  # Cellules musculaires
    NERVE = 4  # Cellules nerveuses
    BLOOD = 5  # Cellules sanguines
    IMMUNE = 6  # Cellules immunitaires
    REPRODUCTIVE = 7  # Cellules reproductrices
    SENSORY = 8  # Cellules sensorielles
    SECRETORY = 9  # Cellules sécrétoires

class NeuralComplexity(Enum):
    """Niveaux de complexité des systèmes nerveux."""
    NONE = 0  # Pas de système nerveux
    NERVE_NET = 1  # Réseau nerveux diffus (ex: cnidaires)
    GANGLIA = 2  # Ganglions nerveux (ex: vers plats)
    LADDER = 3  # Système nerveux en échelle (ex: annélides)
    CENTRAL_NERVOUS_SYSTEM = 4  # Système nerveux central (ex: arthropodes)
    BRAIN_SPINAL_CORD = 5  # Cerveau et moelle épinière (ex: vertébrés)
    COMPLEX_BRAIN = 6  # Cerveau complexe avec cortex (ex: mammifères)
    NEOCORTEX = 7  # Néocortex développé (ex: primates)
    PREFRONTAL_CORTEX = 8  # Cortex préfrontal développé (ex: humains)

class MulticellularityMechanism:
    """Mécanismes permettant l'évolution de la multicellularité."""
    
    def __init__(self):
        """Initialise les mécanismes de multicellularité."""
        # Facteurs favorisant l'évolution de la multicellularité
        self.predation_pressure = 0.0  # Pression de prédation
        self.resource_availability = 0.0  # Disponibilité des ressources
        self.environmental_stability = 0.0  # Stabilité environnementale
        self.spatial_structure = 0.0  # Structure spatiale de l'environnement
        
        # Mécanismes moléculaires
        self.adhesion_molecules = {}  # Molécules d'adhésion cellulaire
        self.signaling_pathways = {}  # Voies de signalisation intercellulaire
        self.gene_regulatory_networks = {}  # Réseaux de régulation génique
        
        # Avantages sélectifs
        self.size_advantage = 0.0  # Avantage de taille (protection contre les prédateurs)
        self.division_of_labor = 0.0  # Division du travail entre cellules
        self.increased_efficiency = 0.0  # Efficacité métabolique accrue
        self.environmental_buffering = 0.0  # Protection contre les fluctuations environnementales
    
    def calculate_multicellularity_potential(self, organism_data: Dict[str, Any]) -> float:
        """
        Calcule le potentiel d'évolution vers la multicellularité pour un organisme.
        
        Args:
            organism_data: Données sur l'organisme
            
        Returns:
            float: Potentiel d'évolution vers la multicellularité (0.0 à 1.0)
        """
        # Vérifier si l'organisme est déjà multicellulaire
        if organism_data.get("multicellularity_type", MulticellularityType.NONE) != MulticellularityType.NONE:
            return 0.0  # Déjà multicellulaire
            
        # Facteurs génomiques
        genome_factors = 0.0
        if "genome" in organism_data:
            genome = organism_data["genome"]
            
            # Présence de gènes d'adhésion cellulaire
            if "adhesion_genes" in genome:
                genome_factors += 0.3 * len(genome["adhesion_genes"]) / 10.0
                
            # Présence de gènes de signalisation
            if "signaling_genes" in genome:
                genome_factors += 0.3 * len(genome["signaling_genes"]) / 10.0
                
            # Présence de gènes de régulation
            if "regulatory_genes" in genome:
                genome_factors += 0.2 * len(genome["regulatory_genes"]) / 10.0
                
            # Taille du génome
            if "size" in genome:
                genome_factors += 0.2 * min(1.0, genome["size"] / 1000.0)
                
        # Facteurs environnementaux
        env_factors = 0.0
        if "environment" in organism_data:
            env = organism_data["environment"]
            
            # Pression de prédation
            if "predation_pressure" in env:
                env_factors += 0.3 * env["predation_pressure"]
                
            # Stabilité environnementale
            if "stability" in env:
                env_factors += 0.2 * env["stability"]
                
            # Richesse en ressources
            if "resource_abundance" in env:
                env_factors += 0.2 * env["resource_abundance"]
                
            # Structure spatiale
            if "spatial_structure" in env:
                env_factors += 0.3 * env["spatial_structure"]
                
        # Facteurs démographiques
        demo_factors = 0.0
        if "population" in organism_data:
            pop = organism_data["population"]
            
            # Densité de population
            if "density" in pop:
                demo_factors += 0.5 * min(1.0, pop["density"] / 100.0)
                
            # Taux de reproduction
            if "reproduction_rate" in pop:
                demo_factors += 0.3 * pop["reproduction_rate"]
                
            # Compétition intraspécifique
            if "competition" in pop:
                demo_factors += 0.2 * pop["competition"]
                
        # Combiner tous les facteurs
        potential = (
            0.4 * genome_factors +
            0.4 * env_factors +
            0.2 * demo_factors
        )
        
        return min(1.0, potential)
    
    def determine_multicellularity_type(self, organism_data: Dict[str, Any]) -> MulticellularityType:
        """
        Détermine le type de multicellularité le plus probable pour un organisme.
        
        Args:
            organism_data: Données sur l'organisme
            
        Returns:
            MulticellularityType: Type de multicellularité
        """
        # Facteurs favorisant chaque type de multicellularité
        type_scores = {
            MulticellularityType.AGGREGATIVE: 0.0,
            MulticellularityType.CLONAL: 0.0,
            MulticellularityType.SYNCYTIAL: 0.0,
            MulticellularityType.COLONIAL: 0.0,
            MulticellularityType.COMPLEX: 0.0
        }
        
        # Facteurs génomiques
        if "genome" in organism_data:
            genome = organism_data["genome"]
            
            # Gènes d'adhésion favorisent l'agrégation et les colonies
            if "adhesion_genes" in genome:
                adhesion_score = len(genome["adhesion_genes"]) / 10.0
                type_scores[MulticellularityType.AGGREGATIVE] += 0.3 * adhesion_score
                type_scores[MulticellularityType.COLONIAL] += 0.2 * adhesion_score
                
            # Gènes de division cellulaire favorisent le type clonal
            if "division_genes" in genome:
                division_score = len(genome["division_genes"]) / 10.0
                type_scores[MulticellularityType.CLONAL] += 0.4 * division_score
                
            # Gènes de fusion cellulaire favorisent le type syncytial
            if "fusion_genes" in genome:
                fusion_score = len(genome["fusion_genes"]) / 5.0
                type_scores[MulticellularityType.SYNCYTIAL] += 0.5 * fusion_score
                
            # Gènes de différenciation favorisent le type complexe
            if "differentiation_genes" in genome:
                diff_score = len(genome["differentiation_genes"]) / 15.0
                type_scores[MulticellularityType.COMPLEX] += 0.6 * diff_score
                
        # Facteurs environnementaux
        if "environment" in organism_data:
            env = organism_data["environment"]
            
            # Environnements instables favorisent l'agrégation (réversible)
            if "stability" in env:
                stability = env["stability"]
                type_scores[MulticellularityType.AGGREGATIVE] += 0.3 * (1.0 - stability)
                type_scores[MulticellularityType.COMPLEX] += 0.3 * stability
                
            # Environnements aquatiques favorisent les colonies
            if "aquatic" in env and env["aquatic"]:
                type_scores[MulticellularityType.COLONIAL] += 0.3
                
            # Environnements avec forte pression de prédation favorisent les types complexes
            if "predation_pressure" in env:
                predation = env["predation_pressure"]
                type_scores[MulticellularityType.COMPLEX] += 0.4 * predation
                
        # Facteurs métaboliques
        if "metabolism" in organism_data:
            metabolism = organism_data["metabolism"]
            
            # Photosynthèse favorise les colonies et le type clonal
            if "photosynthetic" in metabolism and metabolism["photosynthetic"]:
                type_scores[MulticellularityType.COLONIAL] += 0.3
                type_scores[MulticellularityType.CLONAL] += 0.2
                
            # Métabolisme aérobie favorise les types complexes
            if "aerobic" in metabolism and metabolism["aerobic"]:
                type_scores[MulticellularityType.COMPLEX] += 0.3
                
        # Déterminer le type le plus probable
        most_likely_type = max(type_scores.items(), key=lambda x: x[1])[0]
        
        # Si le score est trop faible, rester unicellulaire
        if type_scores[most_likely_type] < 0.3:
            return MulticellularityType.NONE
            
        return most_likely_type
    
    def evolve_multicellularity(self, organism_data: Dict[str, Any], generations: int = 100) -> Dict[str, Any]:
        """
        Simule l'évolution de la multicellularité sur plusieurs générations.
        
        Args:
            organism_data: Données initiales sur l'organisme
            generations: Nombre de générations à simuler
            
        Returns:
            Dict[str, Any]: Données sur l'organisme après évolution
        """
        # Copier les données initiales
        evolved_data = organism_data.copy()
        
        # Historique d'évolution
        evolution_history = []
        
        # Simuler l'évolution sur plusieurs générations
        for gen in range(generations):
            # Calculer le potentiel de multicellularité
            potential = self.calculate_multicellularity_potential(evolved_data)
            
            # Probabilité d'évolution vers la multicellularité
            if random.random() < potential * 0.1:  # Transition rare
                # Déterminer le type de multicellularité
                new_type = self.determine_multicellularity_type(evolved_data)
                
                if new_type != MulticellularityType.NONE:
                    # Transition vers la multicellularité
                    evolved_data["multicellularity_type"] = new_type
                    
                    # Ajouter des cellules différenciées selon le type
                    if new_type == MulticellularityType.COMPLEX:
                        evolved_data["cell_types"] = [CellType.STEM, CellType.EPITHELIAL]
                    elif new_type == MulticellularityType.COLONIAL:
                        evolved_data["cell_types"] = [CellType.STEM]
                    
                    # Enregistrer l'événement évolutif
                    evolution_history.append({
                        "generation": gen,
                        "event": "multicellularity_transition",
                        "type": new_type.name
                    })
                    
                    # Arrêter la simulation après la transition
                    break
            
            # Évolution des gènes liés à la multicellularité
            if "genome" in evolved_data:
                genome = evolved_data["genome"]
                
                # Évolution des gènes d'adhésion
                if "adhesion_genes" not in genome:
                    genome["adhesion_genes"] = []
                if random.random() < 0.05:
                    genome["adhesion_genes"].append(f"adh_{len(genome['adhesion_genes']) + 1}")
                
                # Évolution des gènes de signalisation
                if "signaling_genes" not in genome:
                    genome["signaling_genes"] = []
                if random.random() < 0.05:
                    genome["signaling_genes"].append(f"sig_{len(genome['signaling_genes']) + 1}")
                
                # Évolution des gènes de régulation
                if "regulatory_genes" not in genome:
                    genome["regulatory_genes"] = []
                if random.random() < 0.03:
                    genome["regulatory_genes"].append(f"reg_{len(genome['regulatory_genes']) + 1}")
                
                # Évolution des gènes de différenciation
                if "differentiation_genes" not in genome:
                    genome["differentiation_genes"] = []
                if random.random() < 0.02:
                    genome["differentiation_genes"].append(f"diff_{len(genome['differentiation_genes']) + 1}")
        
        # Ajouter l'historique d'évolution
        evolved_data["evolution_history"] = evolution_history
        
        return evolved_data

class NeuralEvolution:
    """Mécanismes d'évolution des systèmes nerveux et du cerveau."""
    
    def __init__(self):
        """Initialise les mécanismes d'évolution neurale."""
        # Facteurs favorisant l'évolution du système nerveux
        self.predation_pressure = 0.0  # Pression de prédation
        self.environmental_complexity = 0.0  # Complexité de l'environnement
        self.social_complexity = 0.0  # Complexité sociale
        self.locomotion_complexity = 0.0  # Complexité de la locomotion
        
        # Mécanismes moléculaires
        self.neural_genes = {}  # Gènes impliqués dans le développement neural
        self.signaling_pathways = {}  # Voies de signalisation neurale
        self.neurotransmitters = {}  # Neurotransmetteurs
        
        # Structures cérébrales
        self.brain_regions = {}  # Régions cérébrales
        self.neural_circuits = {}  # Circuits neuronaux
        self.connectivity_patterns = {}  # Motifs de connectivité
    
    def calculate_neural_complexity_potential(self, organism_data: Dict[str, Any]) -> float:
        """
        Calcule le potentiel d'évolution de la complexité neurale pour un organisme.
        
        Args:
            organism_data: Données sur l'organisme
            
        Returns:
            float: Potentiel d'évolution neurale (0.0 à 1.0)
        """
        # Vérifier si l'organisme est multicellulaire
        if not organism_data.get("multicellularity_type", MulticellularityType.NONE) in [
            MulticellularityType.COMPLEX, MulticellularityType.COLONIAL
        ]:
            return 0.0  # Doit être multicellulaire
            
        # Vérifier le niveau actuel de complexité neurale
        current_complexity = organism_data.get("neural_complexity", NeuralComplexity.NONE)
        if current_complexity == NeuralComplexity.PREFRONTAL_CORTEX:
            return 0.0  # Déjà au niveau maximal
            
        # Facteurs génomiques
        genome_factors = 0.0
        if "genome" in organism_data:
            genome = organism_data["genome"]
            
            # Présence de gènes neuronaux
            if "neural_genes" in genome:
                genome_factors += 0.4 * min(1.0, len(genome["neural_genes"]) / 20.0)
                
            # Présence de gènes de signalisation
            if "signaling_genes" in genome:
                genome_factors += 0.3 * min(1.0, len(genome["signaling_genes"]) / 15.0)
                
            # Présence de gènes de développement
            if "development_genes" in genome:
                genome_factors += 0.3 * min(1.0, len(genome["development_genes"]) / 15.0)
                
        # Facteurs environnementaux
        env_factors = 0.0
        if "environment" in organism_data:
            env = organism_data["environment"]
            
            # Complexité environnementale
            if "complexity" in env:
                env_factors += 0.3 * env["complexity"]
                
            # Pression de prédation
            if "predation_pressure" in env:
                env_factors += 0.3 * env["predation_pressure"]
                
            # Variabilité environnementale
            if "variability" in env:
                env_factors += 0.2 * env["variability"]
                
            # Richesse en ressources
            if "resource_abundance" in env:
                env_factors += 0.2 * env["resource_abundance"]
                
        # Facteurs comportementaux
        behavior_factors = 0.0
        if "behavior" in organism_data:
            behavior = organism_data["behavior"]
            
            # Complexité locomotrice
            if "locomotion_complexity" in behavior:
                behavior_factors += 0.3 * behavior["locomotion_complexity"]
                
            # Complexité sociale
            if "social_complexity" in behavior:
                behavior_factors += 0.3 * behavior["social_complexity"]
                
            # Complexité alimentaire
            if "feeding_complexity" in behavior:
                behavior_factors += 0.2 * behavior["feeding_complexity"]
                
            # Capacité d'apprentissage
            if "learning_capacity" in behavior:
                behavior_factors += 0.2 * behavior["learning_capacity"]
                
        # Combiner tous les facteurs
        potential = (
            0.3 * genome_factors +
            0.3 * env_factors +
            0.4 * behavior_factors
        )
        
        # Ajuster en fonction du niveau actuel (plus difficile d'évoluer à des niveaux supérieurs)
        level_adjustment = 1.0 - (current_complexity.value / NeuralComplexity.PREFRONTAL_CORTEX.value * 0.7)
        
        return min(1.0, potential * level_adjustment)
    
    def determine_next_neural_complexity(self, organism_data: Dict[str, Any]) -> NeuralComplexity:
        """
        Détermine le prochain niveau de complexité neurale pour un organisme.
        
        Args:
            organism_data: Données sur l'organisme
            
        Returns:
            NeuralComplexity: Prochain niveau de complexité neurale
        """
        # Niveau actuel
        current_level = organism_data.get("neural_complexity", NeuralComplexity.NONE)
        
        # Progression naturelle
        progression = {
            NeuralComplexity.NONE: NeuralComplexity.NERVE_NET,
            NeuralComplexity.NERVE_NET: NeuralComplexity.GANGLIA,
            NeuralComplexity.GANGLIA: NeuralComplexity.LADDER,
            NeuralComplexity.LADDER: NeuralComplexity.CENTRAL_NERVOUS_SYSTEM,
            NeuralComplexity.CENTRAL_NERVOUS_SYSTEM: NeuralComplexity.BRAIN_SPINAL_CORD,
            NeuralComplexity.BRAIN_SPINAL_CORD: NeuralComplexity.COMPLEX_BRAIN,
            NeuralComplexity.COMPLEX_BRAIN: NeuralComplexity.NEOCORTEX,
            NeuralComplexity.NEOCORTEX: NeuralComplexity.PREFRONTAL_CORTEX
        }
        
        # Prochain niveau dans la progression
        next_level = progression.get(current_level, current_level)
        
        # Vérifier si l'organisme a les prérequis pour ce niveau
        if next_level == NeuralComplexity.NERVE_NET:
            # Vérifier la multicellularité
            if organism_data.get("multicellularity_type", MulticellularityType.NONE) == MulticellularityType.NONE:
                return current_level
                
        elif next_level == NeuralComplexity.CENTRAL_NERVOUS_SYSTEM:
            # Vérifier la présence de cellules nerveuses spécialisées
            if "cell_types" in organism_data and CellType.NERVE not in organism_data["cell_types"]:
                return current_level
                
        elif next_level == NeuralComplexity.COMPLEX_BRAIN:
            # Vérifier la complexité comportementale
            if "behavior" in organism_data:
                behavior = organism_data["behavior"]
                if behavior.get("locomotion_complexity", 0.0) < 0.5:
                    return current_level
                    
        elif next_level == NeuralComplexity.NEOCORTEX:
            # Vérifier la complexité sociale
            if "behavior" in organism_data:
                behavior = organism_data["behavior"]
                if behavior.get("social_complexity", 0.0) < 0.6:
                    return current_level
                    
        elif next_level == NeuralComplexity.PREFRONTAL_CORTEX:
            # Vérifier la capacité d'apprentissage
            if "behavior" in organism_data:
                behavior = organism_data["behavior"]
                if behavior.get("learning_capacity", 0.0) < 0.8:
                    return current_level
        
        return next_level
    
    def evolve_neural_complexity(self, organism_data: Dict[str, Any], generations: int = 100) -> Dict[str, Any]:
        """
        Simule l'évolution de la complexité neurale sur plusieurs générations.
        
        Args:
            organism_data: Données initiales sur l'organisme
            generations: Nombre de générations à simuler
            
        Returns:
            Dict[str, Any]: Données sur l'organisme après évolution
        """
        # Copier les données initiales
        evolved_data = organism_data.copy()
        
        # Historique d'évolution
        evolution_history = []
        
        # Simuler l'évolution sur plusieurs générations
        for gen in range(generations):
            # Calculer le potentiel d'évolution neurale
            potential = self.calculate_neural_complexity_potential(evolved_data)
            
            # Probabilité d'évolution vers une complexité neurale supérieure
            if random.random() < potential * 0.05:  # Transition rare
                # Déterminer le prochain niveau de complexité
                next_level = self.determine_next_neural_complexity(evolved_data)
                
                if next_level != evolved_data.get("neural_complexity", NeuralComplexity.NONE):
                    # Transition vers une complexité neurale supérieure
                    evolved_data["neural_complexity"] = next_level
                    
                    # Ajouter des cellules nerveuses si nécessaire
                    if "cell_types" in evolved_data and CellType.NERVE not in evolved_data["cell_types"]:
                        evolved_data["cell_types"].append(CellType.NERVE)
                    
                    # Ajouter des cellules sensorielles pour les niveaux supérieurs
                    if next_level.value >= NeuralComplexity.CENTRAL_NERVOUS_SYSTEM.value:
                        if "cell_types" in evolved_data and CellType.SENSORY not in evolved_data["cell_types"]:
                            evolved_data["cell_types"].append(CellType.SENSORY)
                    
                    # Enregistrer l'événement évolutif
                    evolution_history.append({
                        "generation": gen,
                        "event": "neural_complexity_transition",
                        "level": next_level.name
                    })
            
            # Évolution des gènes liés au système nerveux
            if "genome" in evolved_data:
                genome = evolved_data["genome"]
                
                # Évolution des gènes neuronaux
                if "neural_genes" not in genome:
                    genome["neural_genes"] = []
                if random.random() < 0.05:
                    genome["neural_genes"].append(f"neur_{len(genome['neural_genes']) + 1}")
                
                # Évolution des gènes de développement
                if "development_genes" not in genome:
                    genome["development_genes"] = []
                if random.random() < 0.03:
                    genome["development_genes"].append(f"dev_{len(genome['development_genes']) + 1}")
                
                # Évolution des gènes de neurotransmetteurs
                if "neurotransmitter_genes" not in genome:
                    genome["neurotransmitter_genes"] = []
                if random.random() < 0.02:
                    genome["neurotransmitter_genes"].append(f"nt_{len(genome['neurotransmitter_genes']) + 1}")
            
            # Évolution du comportement
            if "behavior" not in evolved_data:
                evolved_data["behavior"] = {}
            
            behavior = evolved_data["behavior"]
            
            # Évolution de la complexité locomotrice
            if "locomotion_complexity" not in behavior:
                behavior["locomotion_complexity"] = 0.1
            if random.random() < 0.1:
                behavior["locomotion_complexity"] = min(1.0, behavior["locomotion_complexity"] + random.uniform(0.0, 0.1))
            
            # Évolution de la complexité sociale
            if "social_complexity" not in behavior:
                behavior["social_complexity"] = 0.05
            if random.random() < 0.1:
                behavior["social_complexity"] = min(1.0, behavior["social_complexity"] + random.uniform(0.0, 0.1))
            
            # Évolution de la capacité d'apprentissage
            if "learning_capacity" not in behavior:
                behavior["learning_capacity"] = 0.0
            if random.random() < 0.05:
                behavior["learning_capacity"] = min(1.0, behavior["learning_capacity"] + random.uniform(0.0, 0.1))
        
        # Ajouter l'historique d'évolution
        if "evolution_history" not in evolved_data:
            evolved_data["evolution_history"] = []
        evolved_data["evolution_history"].extend(evolution_history)
        
        return evolved_data

class BrainRegion:
    """Représente une région cérébrale avec ses fonctions et connexions."""
    
    def __init__(self, 
                 region_id: str,
                 name: str,
                 functions: List[str],
                 size: float = 1.0,
                 connections: Dict[str, float] = None,
                 neurotransmitters: List[str] = None):
        """
        Initialise une région cérébrale.
        
        Args:
            region_id: Identifiant unique de la région
            name: Nom de la région
            functions: Fonctions de la région
            size: Taille relative de la région
            connections: Connexions avec d'autres régions {region_id: force}
            neurotransmitters: Neurotransmetteurs utilisés par cette région
        """
        self.id = region_id
        self.name = name
        self.functions = functions
        self.size = size
        self.connections = connections or {}
        self.neurotransmitters = neurotransmitters or []
        self.activity = 0.0
        self.plasticity = 0.5  # Capacité à se modifier (0.0 à 1.0)
        self.development_stage = 0.0  # Stade de développement (0.0 à 1.0)
    
    def calculate_activity(self, inputs: Dict[str, float], other_regions: Dict[str, 'BrainRegion']) -> float:
        """
        Calcule l'activité de la région en fonction des entrées et des connexions.
        
        Args:
            inputs: Entrées sensorielles ou cognitives
            other_regions: Autres régions cérébrales
            
        Returns:
            float: Niveau d'activité (0.0 à 1.0)
        """
        # Activité de base
        base_activity = 0.1
        
        # Contribution des entrées directes
        input_contribution = 0.0
        for input_name, input_value in inputs.items():
            if input_name in self.functions:
                input_contribution += input_value * 0.5
        
        # Contribution des connexions avec d'autres régions
        connection_contribution = 0.0
        for region_id, connection_strength in self.connections.items():
            if region_id in other_regions:
                connection_contribution += other_regions[region_id].activity * connection_strength
        
        # Calculer l'activité finale
        self.activity = min(1.0, base_activity + input_contribution + connection_contribution)
        return self.activity
    
    def adapt(self, learning_rate: float = 0.1) -> None:
        """
        Adapte la région en fonction de son activité (plasticité neuronale).
        
        Args:
            learning_rate: Taux d'apprentissage
        """
        # Ajuster la taille en fonction de l'activité
        if self.activity > 0.7:  # Forte activité
            self.size = min(2.0, self.size + learning_rate * self.plasticity * 0.1)
        elif self.activity < 0.3:  # Faible activité
            self.size = max(0.5, self.size - learning_rate * self.plasticity * 0.05)
        
        # Ajuster la plasticité (diminue avec le temps)
        self.plasticity = max(0.1, self.plasticity - 0.001)

class Brain:
    """Représente un cerveau avec ses régions et fonctions."""
    
    def __init__(self, complexity: NeuralComplexity = NeuralComplexity.NONE):
        """
        Initialise un cerveau.
        
        Args:
            complexity: Niveau de complexité neurale
        """
        self.complexity = complexity
        self.regions = {}  # {region_id: BrainRegion}
        self.total_size = 0.0
        self.energy_consumption = 0.0
        self.cognitive_abilities = {}  # {ability_name: level}
        
        # Initialiser les régions selon la complexité
        self._initialize_regions()
    
    def _initialize_regions(self) -> None:
        """Initialise les régions cérébrales selon le niveau de complexité."""
        if self.complexity == NeuralComplexity.NONE:
            return
            
        elif self.complexity == NeuralComplexity.NERVE_NET:
            # Réseau nerveux simple
            self.regions["sensory"] = BrainRegion(
                "sensory",
                "Réseau sensoriel",
                ["sensation"],
                1.0,
                {"motor": 0.8},
                ["acetylcholine"]
            )
            
            self.regions["motor"] = BrainRegion(
                "motor",
                "Réseau moteur",
                ["movement"],
                1.0,
                {},
                ["acetylcholine"]
            )
            
        elif self.complexity == NeuralComplexity.GANGLIA:
            # Ganglions cérébraux
            self.regions["cephalic_ganglion"] = BrainRegion(
                "cephalic_ganglion",
                "Ganglion céphalique",
                ["sensation", "integration"],
                1.2,
                {"motor_ganglion": 0.7},
                ["acetylcholine", "dopamine"]
            )
            
            self.regions["motor_ganglion"] = BrainRegion(
                "motor_ganglion",
                "Ganglion moteur",
                ["movement", "coordination"],
                1.0,
                {},
                ["acetylcholine"]
            )
            
        elif self.complexity == NeuralComplexity.CENTRAL_NERVOUS_SYSTEM:
            # Système nerveux central simple
            self.regions["brain"] = BrainRegion(
                "brain",
                "Cerveau primitif",
                ["sensation", "integration", "decision"],
                1.5,
                {"spinal_cord": 0.9},
                ["acetylcholine", "dopamine", "serotonin"]
            )
            
            self.regions["spinal_cord"] = BrainRegion(
                "spinal_cord",
                "Moelle épinière",
                ["reflexes", "movement"],
                1.0,
                {},
                ["acetylcholine", "GABA"]
            )
            
        elif self.complexity == NeuralComplexity.BRAIN_SPINAL_CORD:
            # Cerveau et moelle épinière
            self.regions["forebrain"] = BrainRegion(
                "forebrain",
                "Prosencéphale",
                ["sensation", "integration", "memory"],
                1.8,
                {"midbrain": 0.8, "hindbrain": 0.6},
                ["acetylcholine", "dopamine", "serotonin", "GABA"]
            )
            
            self.regions["midbrain"] = BrainRegion(
                "midbrain",
                "Mésencéphale",
                ["vision", "hearing", "motor_coordination"],
                1.2,
                {"hindbrain": 0.7, "spinal_cord": 0.8},
                ["acetylcholine", "dopamine"]
            )
            
            self.regions["hindbrain"] = BrainRegion(
                "hindbrain",
                "Rhombencéphale",
                ["balance", "basic_functions"],
                1.0,
                {"spinal_cord": 0.9},
                ["acetylcholine", "GABA"]
            )
            
            self.regions["spinal_cord"] = BrainRegion(
                "spinal_cord",
                "Moelle épinière",
                ["reflexes", "movement"],
                1.0,
                {},
                ["acetylcholine", "GABA"]
            )
            
        elif self.complexity == NeuralComplexity.COMPLEX_BRAIN:
            # Cerveau complexe
            self.regions["cerebrum"] = BrainRegion(
                "cerebrum",
                "Cerveau",
                ["cognition", "sensation", "movement", "memory"],
                2.5,
                {"thalamus": 0.9, "cerebellum": 0.7, "brainstem": 0.6},
                ["glutamate", "GABA", "dopamine", "serotonin"]
            )
            
            self.regions["thalamus"] = BrainRegion(
                "thalamus",
                "Thalamus",
                ["sensory_relay", "motor_relay"],
                1.0,
                {"cerebrum": 0.9, "brainstem": 0.8},
                ["glutamate", "GABA"]
            )
            
            self.regions["cerebellum"] = BrainRegion(
                "cerebellum",
                "Cervelet",
                ["motor_coordination", "balance", "timing"],
                1.5,
                {"brainstem": 0.8},
                ["GABA", "glutamate"]
            )
            
            self.regions["brainstem"] = BrainRegion(
                "brainstem",
                "Tronc cérébral",
                ["basic_functions", "reflexes"],
                1.0,
                {"spinal_cord": 0.9},
                ["acetylcholine", "norepinephrine"]
            )
            
            self.regions["spinal_cord"] = BrainRegion(
                "spinal_cord",
                "Moelle épinière",
                ["reflexes", "movement"],
                1.0,
                {},
                ["acetylcholine", "GABA"]
            )
            
        elif self.complexity == NeuralComplexity.NEOCORTEX:
            # Cerveau avec néocortex
            self.regions["frontal_lobe"] = BrainRegion(
                "frontal_lobe",
                "Lobe frontal",
                ["executive_function", "planning", "personality"],
                2.0,
                {"parietal_lobe": 0.8, "temporal_lobe": 0.7, "limbic_system": 0.9},
                ["glutamate", "GABA", "dopamine"]
            )
            
            self.regions["parietal_lobe"] = BrainRegion(
                "parietal_lobe",
                "Lobe pariétal",
                ["sensory_integration", "spatial_awareness"],
                1.5,
                {"occipital_lobe": 0.8, "temporal_lobe": 0.7},
                ["glutamate", "GABA"]
            )
            
            self.regions["temporal_lobe"] = BrainRegion(
                "temporal_lobe",
                "Lobe temporal",
                ["auditory_processing", "memory", "language"],
                1.5,
                {"occipital_lobe": 0.6, "limbic_system": 0.8},
                ["glutamate", "GABA"]
            )
            
            self.regions["occipital_lobe"] = BrainRegion(
                "occipital_lobe",
                "Lobe occipital",
                ["visual_processing"],
                1.2,
                {},
                ["glutamate", "GABA"]
            )
            
            self.regions["limbic_system"] = BrainRegion(
                "limbic_system",
                "Système limbique",
                ["emotion", "memory", "motivation"],
                1.0,
                {"brainstem": 0.7},
                ["dopamine", "serotonin", "norepinephrine"]
            )
            
            self.regions["cerebellum"] = BrainRegion(
                "cerebellum",
                "Cervelet",
                ["motor_coordination", "balance", "timing"],
                1.5,
                {"brainstem": 0.8},
                ["GABA", "glutamate"]
            )
            
            self.regions["brainstem"] = BrainRegion(
                "brainstem",
                "Tronc cérébral",
                ["basic_functions", "reflexes"],
                1.0,
                {"spinal_cord": 0.9},
                ["acetylcholine", "norepinephrine"]
            )
            
        elif self.complexity == NeuralComplexity.PREFRONTAL_CORTEX:
            # Cerveau avec cortex préfrontal développé
            self.regions["prefrontal_cortex"] = BrainRegion(
                "prefrontal_cortex",
                "Cortex préfrontal",
                ["executive_function", "decision_making", "social_behavior", "working_memory"],
                2.5,
                {"frontal_lobe": 0.9, "limbic_system": 0.8},
                ["glutamate", "GABA", "dopamine"]
            )
            
            self.regions["frontal_lobe"] = BrainRegion(
                "frontal_lobe",
                "Lobe frontal",
                ["motor_control", "planning", "personality"],
                2.0,
                {"parietal_lobe": 0.8, "temporal_lobe": 0.7},
                ["glutamate", "GABA", "dopamine"]
            )
            
            self.regions["parietal_lobe"] = BrainRegion(
                "parietal_lobe",
                "Lobe pariétal",
                ["sensory_integration", "spatial_awareness"],
                1.5,
                {"occipital_lobe": 0.8, "temporal_lobe": 0.7},
                ["glutamate", "GABA"]
            )
            
            self.regions["temporal_lobe"] = BrainRegion(
                "temporal_lobe",
                "Lobe temporal",
                ["auditory_processing", "memory", "language"],
                1.5,
                {"occipital_lobe": 0.6, "limbic_system": 0.8},
                ["glutamate", "GABA"]
            )
            
            self.regions["occipital_lobe"] = BrainRegion(
                "occipital_lobe",
                "Lobe occipital",
                ["visual_processing"],
                1.2,
                {},
                ["glutamate", "GABA"]
            )
            
            self.regions["limbic_system"] = BrainRegion(
                "limbic_system",
                "Système limbique",
                ["emotion", "memory", "motivation"],
                1.0,
                {"brainstem": 0.7},
                ["dopamine", "serotonin", "norepinephrine"]
            )
            
            self.regions["basal_ganglia"] = BrainRegion(
                "basal_ganglia",
                "Ganglions de la base",
                ["motor_control", "procedural_learning"],
                1.2,
                {"thalamus": 0.8, "brainstem": 0.6},
                ["dopamine", "GABA", "glutamate"]
            )
            
            self.regions["cerebellum"] = BrainRegion(
                "cerebellum",
                "Cervelet",
                ["motor_coordination", "balance", "cognitive_functions"],
                1.5,
                {"brainstem": 0.8},
                ["GABA", "glutamate"]
            )
            
            self.regions["brainstem"] = BrainRegion(
                "brainstem",
                "Tronc cérébral",
                ["basic_functions", "reflexes"],
                1.0,
                {"spinal_cord": 0.9},
                ["acetylcholine", "norepinephrine"]
            )
        
        # Calculer la taille totale et la consommation d'énergie
        self._update_metrics()
    
    def _update_metrics(self) -> None:
        """Met à jour les métriques du cerveau."""
        self.total_size = sum(region.size for region in self.regions.values())
        
        # La consommation d'énergie augmente avec la complexité
        base_consumption = {
            NeuralComplexity.NONE: 0.0,
            NeuralComplexity.NERVE_NET: 0.1,
            NeuralComplexity.GANGLIA: 0.2,
            NeuralComplexity.LADDER: 0.3,
            NeuralComplexity.CENTRAL_NERVOUS_SYSTEM: 0.5,
            NeuralComplexity.BRAIN_SPINAL_CORD: 0.8,
            NeuralComplexity.COMPLEX_BRAIN: 1.2,
            NeuralComplexity.NEOCORTEX: 1.8,
            NeuralComplexity.PREFRONTAL_CORTEX: 2.5
        }
        
        self.energy_consumption = base_consumption.get(self.complexity, 0.0) * self.total_size / 10.0
        
        # Mettre à jour les capacités cognitives
        self._update_cognitive_abilities()
    
    def _update_cognitive_abilities(self) -> None:
        """Met à jour les capacités cognitives en fonction des régions cérébrales."""
        # Réinitialiser les capacités
        self.cognitive_abilities = {
            "perception": 0.0,
            "motor_control": 0.0,
            "learning": 0.0,
            "memory": 0.0,
            "decision_making": 0.0,
            "social_cognition": 0.0,
            "language": 0.0,
            "tool_use": 0.0,
            "consciousness": 0.0
        }
        
        # Capacités de base selon la complexité
        base_abilities = {
            NeuralComplexity.NONE: {},
            NeuralComplexity.NERVE_NET: {
                "perception": 0.2,
                "motor_control": 0.1
            },
            NeuralComplexity.GANGLIA: {
                "perception": 0.3,
                "motor_control": 0.2,
                "learning": 0.1
            },
            NeuralComplexity.LADDER: {
                "perception": 0.4,
                "motor_control": 0.3,
                "learning": 0.2,
                "memory": 0.1
            },
            NeuralComplexity.CENTRAL_NERVOUS_SYSTEM: {
                "perception": 0.5,
                "motor_control": 0.4,
                "learning": 0.3,
                "memory": 0.2,
                "decision_making": 0.1
            },
            NeuralComplexity.BRAIN_SPINAL_CORD: {
                "perception": 0.6,
                "motor_control": 0.5,
                "learning": 0.4,
                "memory": 0.3,
                "decision_making": 0.2,
                "social_cognition": 0.1
            },
            NeuralComplexity.COMPLEX_BRAIN: {
                "perception": 0.7,
                "motor_control": 0.6,
                "learning": 0.5,
                "memory": 0.5,
                "decision_making": 0.4,
                "social_cognition": 0.3,
                "tool_use": 0.1,
                "consciousness": 0.1
            },
            NeuralComplexity.NEOCORTEX: {
                "perception": 0.8,
                "motor_control": 0.7,
                "learning": 0.7,
                "memory": 0.7,
                "decision_making": 0.6,
                "social_cognition": 0.5,
                "language": 0.3,
                "tool_use": 0.4,
                "consciousness": 0.3
            },
            NeuralComplexity.PREFRONTAL_CORTEX: {
                "perception": 0.9,
                "motor_control": 0.8,
                "learning": 0.9,
                "memory": 0.8,
                "decision_making": 0.9,
                "social_cognition": 0.8,
                "language": 0.7,
                "tool_use": 0.8,
                "consciousness": 0.7
            }
        }
        
        # Appliquer les capacités de base
        for ability, level in base_abilities.get(self.complexity, {}).items():
            self.cognitive_abilities[ability] = level
        
        # Ajuster en fonction des régions spécifiques
        for region in self.regions.values():
            # Perception
            if any(f in ["sensation", "sensory_integration", "visual_processing", "auditory_processing"] 
                  for f in region.functions):
                self.cognitive_abilities["perception"] += 0.1 * region.size
                
            # Contrôle moteur
            if any(f in ["movement", "motor_coordination", "motor_control"] 
                  for f in region.functions):
                self.cognitive_abilities["motor_control"] += 0.1 * region.size
                
            # Apprentissage
            if any(f in ["learning", "procedural_learning"] 
                  for f in region.functions):
                self.cognitive_abilities["learning"] += 0.1 * region.size
                
            # Mémoire
            if "memory" in region.functions:
                self.cognitive_abilities["memory"] += 0.1 * region.size
                
            # Prise de décision
            if any(f in ["decision_making", "executive_function", "planning"] 
                  for f in region.functions):
                self.cognitive_abilities["decision_making"] += 0.1 * region.size
                
            # Cognition sociale
            if any(f in ["social_behavior", "emotion"] 
                  for f in region.functions):
                self.cognitive_abilities["social_cognition"] += 0.1 * region.size
                
            # Langage
            if "language" in region.functions:
                self.cognitive_abilities["language"] += 0.1 * region.size
                
            # Utilisation d'outils
            if any(f in ["tool_use", "planning", "spatial_awareness"] 
                  for f in region.functions):
                self.cognitive_abilities["tool_use"] += 0.1 * region.size
                
            # Conscience
            if any(f in ["consciousness", "executive_function", "working_memory"] 
                  for f in region.functions):
                self.cognitive_abilities["consciousness"] += 0.1 * region.size
        
        # Limiter les valeurs entre 0 et 1
        for ability in self.cognitive_abilities:
            self.cognitive_abilities[ability] = min(1.0, self.cognitive_abilities[ability])
    
    def process_inputs(self, sensory_inputs: Dict[str, float]) -> Dict[str, float]:
        """
        Traite les entrées sensorielles et génère des sorties comportementales.
        
        Args:
            sensory_inputs: Entrées sensorielles {type: intensité}
            
        Returns:
            Dict[str, float]: Sorties comportementales {comportement: intensité}
        """
        # Si pas de cerveau, réponses réflexes simples
        if self.complexity == NeuralComplexity.NONE:
            return {
                "reflex_response": max(0.0, min(1.0, sum(sensory_inputs.values()) / len(sensory_inputs)))
            }
        
        # Propager l'activité à travers les régions
        for region_id, region in self.regions.items():
            region.calculate_activity(sensory_inputs, self.regions)
        
        # Générer des sorties comportementales en fonction des capacités cognitives
        behavioral_outputs = {}
        
        # Réponses motrices de base
        if "motor_control" in self.cognitive_abilities:
            motor_regions = [r for r in self.regions.values() 
                           if any(f in ["movement", "motor_control", "motor_coordination"] 
                                for f in r.functions)]
            
            if motor_regions:
                motor_activity = sum(r.activity for r in motor_regions) / len(motor_regions)
                behavioral_outputs["movement"] = motor_activity * self.cognitive_abilities["motor_control"]
        
        # Réponses émotionnelles
        if "social_cognition" in self.cognitive_abilities and self.cognitive_abilities["social_cognition"] > 0.2:
            emotional_regions = [r for r in self.regions.values() 
                               if "emotion" in r.functions]
            
            if emotional_regions:
                emotional_activity = sum(r.activity for r in emotional_regions) / len(emotional_regions)
                behavioral_outputs["emotional_response"] = emotional_activity * self.cognitive_abilities["social_cognition"]
        
        # Prise de décision
        if "decision_making" in self.cognitive_abilities and self.cognitive_abilities["decision_making"] > 0.3:
            decision_regions = [r for r in self.regions.values() 
                              if any(f in ["decision_making", "executive_function"] 
                                   for f in r.functions)]
            
            if decision_regions:
                decision_activity = sum(r.activity for r in decision_regions) / len(decision_regions)
                behavioral_outputs["decision"] = decision_activity * self.cognitive_abilities["decision_making"]
        
        # Apprentissage
        if "learning" in self.cognitive_abilities and self.cognitive_abilities["learning"] > 0.4:
            # Adapter les régions en fonction de leur activité
            learning_rate = 0.05 * self.cognitive_abilities["learning"]
            for region in self.regions.values():
                region.adapt(learning_rate)
            
            behavioral_outputs["learning"] = self.cognitive_abilities["learning"] * 0.5
        
        # Utilisation d'outils (pour les niveaux supérieurs)
        if "tool_use" in self.cognitive_abilities and self.cognitive_abilities["tool_use"] > 0.3:
            tool_regions = [r for r in self.regions.values() 
                          if any(f in ["planning", "spatial_awareness", "tool_use"] 
                               for f in r.functions)]
            
            if tool_regions:
                tool_activity = sum(r.activity for r in tool_regions) / len(tool_regions)
                behavioral_outputs["tool_use"] = tool_activity * self.cognitive_abilities["tool_use"]
        
        # Communication (pour les niveaux supérieurs)
        if "language" in self.cognitive_abilities and self.cognitive_abilities["language"] > 0.2:
            language_regions = [r for r in self.regions.values() 
                              if "language" in r.functions]
            
            if language_regions:
                language_activity = sum(r.activity for r in language_regions) / len(language_regions)
                behavioral_outputs["communication"] = language_activity * self.cognitive_abilities["language"]
        
        # Mettre à jour les métriques
        self._update_metrics()
        
        return behavioral_outputs
    
    def evolve(self, generations: int = 10, learning_experiences: int = 5) -> None:
        """
        Fait évoluer le cerveau sur plusieurs générations avec apprentissage.
        
        Args:
            generations: Nombre de générations
            learning_experiences: Nombre d'expériences d'apprentissage par génération
        """
        for gen in range(generations):
            # Simuler des expériences d'apprentissage
            for _ in range(learning_experiences):
                # Générer des entrées sensorielles aléatoires
                sensory_inputs = {
                    "visual": random.uniform(0.0, 1.0),
                    "auditory": random.uniform(0.0, 1.0),
                    "tactile": random.uniform(0.0, 1.0),
                    "olfactory": random.uniform(0.0, 1.0)
                }
                
                # Traiter les entrées
                self.process_inputs(sensory_inputs)
            
            # Évolution structurelle (rare)
            if random.random() < 0.2:
                # Possibilité d'ajouter une nouvelle région
                if self.complexity.value >= NeuralComplexity.CENTRAL_NERVOUS_SYSTEM.value:
                    if random.random() < 0.1:
                        # Créer une nouvelle région spécialisée
                        region_id = f"specialized_region_{len(self.regions) + 1}"
                        functions = random.sample(
                            ["sensory_processing", "motor_control", "memory", "emotion", 
                             "decision_making", "attention", "spatial_awareness"],
                            k=random.randint(1, 3)
                        )
                        
                        # Connexions avec les régions existantes
                        connections = {}
                        for existing_id in self.regions:
                            if random.random() < 0.3:
                                connections[existing_id] = random.uniform(0.1, 0.9)
                        
                        # Créer la région
                        new_region = BrainRegion(
                            region_id,
                            f"Région spécialisée {len(self.regions) + 1}",
                            functions,
                            0.5,  # Taille initiale réduite
                            connections,
                            random.sample(["glutamate", "GABA", "dopamine", "serotonin"], k=2)
                        )
                        
                        # Ajouter la région
                        self.regions[region_id] = new_region
                
                # Renforcer les connexions les plus utilisées
                for region in self.regions.values():
                    for target_id in list(region.connections.keys()):
                        if target_id in self.regions:
                            target = self.regions[target_id]
                            
                            # Si les deux régions sont actives ensemble, renforcer la connexion
                            if region.activity > 0.5 and target.activity > 0.5:
                                region.connections[target_id] = min(1.0, region.connections[target_id] + 0.1)
                            # Si elles sont rarement actives ensemble, affaiblir la connexion
                            elif region.activity < 0.2 and target.activity < 0.2:
                                region.connections[target_id] = max(0.1, region.connections[target_id] - 0.05)
            
            # Mettre à jour les métriques
            self._update_metrics()

# Fonctions utilitaires pour créer des organismes avec différents niveaux d'évolution
def create_unicellular_organism() -> Dict[str, Any]:
    """
    Crée un organisme unicellulaire de base.
    
    Returns:
        Dict[str, Any]: Données de l'organisme
    """
    return {
        "id": str(uuid.uuid4()),
        "type": "unicellular",
        "multicellularity_type": MulticellularityType.NONE,
        "neural_complexity": NeuralComplexity.NONE,
        "genome": {
            "size": 100,
            "genes": [f"gene_{i}" for i in range(10)],
            "regulatory_genes": [f"reg_{i}" for i in range(2)]
        },
        "metabolism": {
            "efficiency": 0.5,
            "photosynthetic": random.choice([True, False]),
            "aerobic": True
        },
        "environment": {
            "temperature": 25.0,
            "stability": 0.7,
            "predation_pressure": 0.3,
            "resource_abundance": 0.6,
            "spatial_structure": 0.4,
            "aquatic": True
        },
        "population": {
            "size": 1000,
            "density": 50.0,
            "reproduction_rate": 0.8,
            "competition": 0.4
        },
        "behavior": {
            "locomotion_complexity": 0.1,
            "social_complexity": 0.0,
            "feeding_complexity": 0.1,
            "learning_capacity": 0.0
        }
    }

def create_simple_multicellular_organism() -> Dict[str, Any]:
    """
    Crée un organisme multicellulaire simple.
    
    Returns:
        Dict[str, Any]: Données de l'organisme
    """
    organism = create_unicellular_organism()
    
    # Modifier pour en faire un organisme multicellulaire simple
    organism["type"] = "simple_multicellular"
    organism["multicellularity_type"] = MulticellularityType.COLONIAL
    organism["cell_types"] = [CellType.STEM]
    
    # Génome plus complexe
    organism["genome"]["size"] = 500
    organism["genome"]["genes"] = [f"gene_{i}" for i in range(50)]
    organism["genome"]["regulatory_genes"] = [f"reg_{i}" for i in range(10)]
    organism["genome"]["adhesion_genes"] = [f"adh_{i}" for i in range(5)]
    organism["genome"]["signaling_genes"] = [f"sig_{i}" for i in range(3)]
    
    # Comportement légèrement plus complexe
    organism["behavior"]["locomotion_complexity"] = 0.2
    organism["behavior"]["social_complexity"] = 0.1
    organism["behavior"]["feeding_complexity"] = 0.2
    
    return organism

def create_complex_multicellular_organism() -> Dict[str, Any]:
    """
    Crée un organisme multicellulaire complexe.
    
    Returns:
        Dict[str, Any]: Données de l'organisme
    """
    organism = create_simple_multicellular_organism()
    
    # Modifier pour en faire un organisme multicellulaire complexe
    organism["type"] = "complex_multicellular"
    organism["multicellularity_type"] = MulticellularityType.COMPLEX
    organism["cell_types"] = [CellType.STEM, CellType.EPITHELIAL, CellType.CONNECTIVE, CellType.MUSCLE, CellType.NERVE]
    organism["neural_complexity"] = NeuralComplexity.CENTRAL_NERVOUS_SYSTEM
    
    # Génome encore plus complexe
    organism["genome"]["size"] = 2000
    organism["genome"]["genes"] = [f"gene_{i}" for i in range(200)]
    organism["genome"]["regulatory_genes"] = [f"reg_{i}" for i in range(30)]
    organism["genome"]["adhesion_genes"] = [f"adh_{i}" for i in range(15)]
    organism["genome"]["signaling_genes"] = [f"sig_{i}" for i in range(20)]
    organism["genome"]["differentiation_genes"] = [f"diff_{i}" for i in range(10)]
    organism["genome"]["neural_genes"] = [f"neur_{i}" for i in range(15)]
    organism["genome"]["development_genes"] = [f"dev_{i}" for i in range(10)]
    
    # Comportement plus complexe
    organism["behavior"]["locomotion_complexity"] = 0.6
    organism["behavior"]["social_complexity"] = 0.4
    organism["behavior"]["feeding_complexity"] = 0.5
    organism["behavior"]["learning_capacity"] = 0.3
    
    # Ajouter un cerveau simple
    organism["brain"] = {
        "regions": ["brain", "spinal_cord"],
        "size": 1.0,
        "energy_consumption": 0.2,
        "cognitive_abilities": {
            "perception": 0.5,
            "motor_control": 0.4,
            "learning": 0.3,
            "memory": 0.2,
            "decision_making": 0.1
        }
    }
    
    return organism

def create_advanced_organism() -> Dict[str, Any]:
    """
    Crée un organisme avancé avec un cerveau complexe.
    
    Returns:
        Dict[str, Any]: Données de l'organisme
    """
    organism = create_complex_multicellular_organism()
    
    # Modifier pour en faire un organisme avancé
    organism["type"] = "advanced_organism"
    organism["neural_complexity"] = NeuralComplexity.NEOCORTEX
    organism["cell_types"] = [CellType.STEM, CellType.EPITHELIAL, CellType.CONNECTIVE, 
                            CellType.MUSCLE, CellType.NERVE, CellType.BLOOD, 
                            CellType.IMMUNE, CellType.REPRODUCTIVE, CellType.SENSORY]
    
    # Génome très complexe
    organism["genome"]["size"] = 10000
    organism["genome"]["neural_genes"] = [f"neur_{i}" for i in range(50)]
    organism["genome"]["development_genes"] = [f"dev_{i}" for i in range(30)]
    organism["genome"]["neurotransmitter_genes"] = [f"nt_{i}" for i in range(10)]
    
    # Comportement avancé
    organism["behavior"]["locomotion_complexity"] = 0.8
    organism["behavior"]["social_complexity"] = 0.7
    organism["behavior"]["feeding_complexity"] = 0.7
    organism["behavior"]["learning_capacity"] = 0.6
    organism["behavior"]["tool_use"] = 0.4
    organism["behavior"]["communication"] = 0.5
    
    # Cerveau complexe
    organism["brain"] = {
        "regions": ["frontal_lobe", "parietal_lobe", "temporal_lobe", "occipital_lobe", 
                   "limbic_system", "cerebellum", "brainstem", "spinal_cord"],
        "size": 2.0,
        "energy_consumption": 0.8,
        "cognitive_abilities": {
            "perception": 0.8,
            "motor_control": 0.7,
            "learning": 0.7,
            "memory": 0.7,
            "decision_making": 0.6,
            "social_cognition": 0.5,
            "language": 0.3,
            "tool_use": 0.4,
            "consciousness": 0.3
        }
    }
    
    return organism

# Fonction pour simuler l'évolution d'un organisme
def simulate_evolution(organism_data: Dict[str, Any], generations: int = 1000) -> Dict[str, Any]:
    """
    Simule l'évolution d'un organisme sur plusieurs générations.
    
    Args:
        organism_data: Données initiales de l'organisme
        generations: Nombre de générations à simuler
        
    Returns:
        Dict[str, Any]: Données de l'organisme après évolution
    """
    # Copier les données initiales
    evolved_data = organism_data.copy()
    
    # Créer les mécanismes d'évolution
    multicellularity_mechanism = MulticellularityMechanism()
    neural_evolution = NeuralEvolution()
    
    # Historique d'évolution
    evolution_history = []
    
    # Simuler l'évolution sur plusieurs générations
    for gen in range(generations):
        # Étape 1: Évolution de la multicellularité
        if evolved_data.get("multicellularity_type", MulticellularityType.NONE) == MulticellularityType.NONE:
            # Calculer le potentiel de multicellularité
            potential = multicellularity_mechanism.calculate_multicellularity_potential(evolved_data)
            
            # Probabilité d'évolution vers la multicellularité
            if random.random() < potential * 0.01:  # Transition rare
                # Faire évoluer vers la multicellularité
                evolved_data = multicellularity_mechanism.evolve_multicellularity(evolved_data, 100)
                
                # Enregistrer l'événement évolutif
                evolution_history.append({
                    "generation": gen,
                    "event": "multicellularity_evolution",
                    "type": evolved_data.get("multicellularity_type", MulticellularityType.NONE).name
                })
        
        # Étape 2: Évolution neurale (si multicellulaire)
        if evolved_data.get("multicellularity_type", MulticellularityType.NONE) != MulticellularityType.NONE:
            # Calculer le potentiel d'évolution neurale
            potential = neural_evolution.calculate_neural_complexity_potential(evolved_data)
            
            # Probabilité d'évolution vers une complexité neurale supérieure
            if random.random() < potential * 0.005:  # Transition très rare
                # Faire évoluer vers une complexité neurale supérieure
                old_complexity = evolved_data.get("neural_complexity", NeuralComplexity.NONE)
                evolved_data = neural_evolution.evolve_neural_complexity(evolved_data, 100)
                new_complexity = evolved_data.get("neural_complexity", NeuralComplexity.NONE)
                
                if old_complexity != new_complexity:
                    # Enregistrer l'événement évolutif
                    evolution_history.append({
                        "generation": gen,
                        "event": "neural_evolution",
                        "from": old_complexity.name,
                        "to": new_complexity.name
                    })
        
        # Étape 3: Évolution génomique
        if "genome" in evolved_data:
            genome = evolved_data["genome"]
            
            # Mutation aléatoire des gènes
            mutation_rate = 0.01  # Taux de mutation de base
            
            # Augmenter la taille du génome (rarement)
            if random.random() < mutation_rate * 0.1:
                genome["size"] = int(genome["size"] * (1.0 + random.uniform(0.01, 0.05)))
            
            # Ajouter de nouveaux gènes (rarement)
            for gene_type in ["genes", "regulatory_genes", "adhesion_genes", "signaling_genes", 
                             "differentiation_genes", "neural_genes", "development_genes"]:
                if gene_type in genome:
                    if random.random() < mutation_rate:
                        genome[gene_type].append(f"{gene_type[:-1]}_{len(genome[gene_type]) + 1}")
        
        # Étape 4: Évolution comportementale
        if "behavior" in evolved_data:
            behavior = evolved_data["behavior"]
            
            # Évolution graduelle des comportements
            for trait in ["locomotion_complexity", "social_complexity", "feeding_complexity", "learning_capacity"]:
                if trait in behavior:
                    # Probabilité d'augmentation dépendant de la complexité neurale
                    neural_factor = 0.1
                    if "neural_complexity" in evolved_data:
                        neural_factor = evolved_data["neural_complexity"].value / NeuralComplexity.PREFRONTAL_CORTEX.value
                    
                    if random.random() < 0.05 * neural_factor:
                        behavior[trait] = min(1.0, behavior[trait] + random.uniform(0.01, 0.05))
            
            # Ajouter de nouveaux comportements avec l'évolution neurale
            if "neural_complexity" in evolved_data:
                if evolved_data["neural_complexity"].value >= NeuralComplexity.COMPLEX_BRAIN.value:
                    if "tool_use" not in behavior:
                        behavior["tool_use"] = 0.1
                    elif random.random() < 0.05:
                        behavior["tool_use"] = min(1.0, behavior["tool_use"] + random.uniform(0.01, 0.05))
                
                if evolved_data["neural_complexity"].value >= NeuralComplexity.NEOCORTEX.value:
                    if "communication" not in behavior:
                        behavior["communication"] = 0.2
                    elif random.random() < 0.05:
                        behavior["communication"] = min(1.0, behavior["communication"] + random.uniform(0.01, 0.05))
                
                if evolved_data["neural_complexity"].value >= NeuralComplexity.PREFRONTAL_CORTEX.value:
                    if "abstract_thinking" not in behavior:
                        behavior["abstract_thinking"] = 0.3
                    elif random.random() < 0.05:
                        behavior["abstract_thinking"] = min(1.0, behavior["abstract_thinking"] + random.uniform(0.01, 0.05))
    
    # Ajouter l'historique d'évolution
    if "evolution_history" not in evolved_data:
        evolved_data["evolution_history"] = []
    evolved_data["evolution_history"].extend(evolution_history)
    
    return evolved_data