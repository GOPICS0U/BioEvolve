"""
Module de régulation génétique pour BioEvolve
Implémente des mécanismes de régulation génétique et de gènes architectes
basés sur les principes scientifiques de l'évolution
"""

import random
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set, Any, Callable
import uuid

class GeneType(Enum):
    """Types de gènes selon leur fonction dans le génome."""
    STRUCTURAL = 0      # Gènes codant pour des protéines structurales
    REGULATORY = 1      # Gènes régulateurs (facteurs de transcription)
    ARCHITECT = 2       # Gènes architectes (contrôlent le développement)
    METABOLIC = 3       # Gènes métaboliques (enzymes)
    SIGNALING = 4       # Gènes de signalisation (hormones, neurotransmetteurs)
    IMMUNE = 5          # Gènes du système immunitaire
    TRANSPOSON = 6      # Éléments génétiques mobiles
    PSEUDOGENE = 7      # Gènes non fonctionnels
    NONCODING = 8       # ADN non codant avec fonction régulatrice

class RegulatoryElement:
    """Élément régulateur contrôlant l'expression des gènes."""
    
    def __init__(self, 
                 element_id: str,
                 target_genes: List[str],
                 activation_threshold: float,
                 effect_strength: float,
                 is_enhancer: bool = True,
                 environmental_sensitivity: Dict[str, float] = None):
        """
        Initialise un élément régulateur.
        
        Args:
            element_id: Identifiant unique de l'élément
            target_genes: Liste des IDs des gènes ciblés
            activation_threshold: Seuil d'activation (0.0 à 1.0)
            effect_strength: Force de l'effet (0.0 à 1.0)
            is_enhancer: True si c'est un activateur, False si c'est un répresseur
            environmental_sensitivity: Sensibilité aux facteurs environnementaux
        """
        self.id = element_id
        self.target_genes = target_genes
        self.activation_threshold = activation_threshold
        self.effect_strength = effect_strength
        self.is_enhancer = is_enhancer
        self.environmental_sensitivity = environmental_sensitivity or {}
        self.current_activity = 0.0
        
    def calculate_activity(self, environmental_factors: Dict[str, float]) -> float:
        """
        Calcule le niveau d'activité de l'élément régulateur en fonction des facteurs environnementaux.
        
        Args:
            environmental_factors: Dictionnaire des facteurs environnementaux
            
        Returns:
            float: Niveau d'activité (0.0 à 1.0)
        """
        base_activity = 0.5  # Activité de base
        
        # Ajuster l'activité en fonction des facteurs environnementaux
        for factor, sensitivity in self.environmental_sensitivity.items():
            if factor in environmental_factors:
                # L'effet dépend de la sensibilité et de l'intensité du facteur
                effect = sensitivity * environmental_factors[factor]
                base_activity += effect
        
        # Limiter l'activité entre 0 et 1
        self.current_activity = max(0.0, min(1.0, base_activity))
        return self.current_activity
    
    def is_active(self, environmental_factors: Dict[str, float]) -> bool:
        """
        Détermine si l'élément régulateur est actif.
        
        Args:
            environmental_factors: Dictionnaire des facteurs environnementaux
            
        Returns:
            bool: True si l'élément est actif, False sinon
        """
        activity = self.calculate_activity(environmental_factors)
        return activity >= self.activation_threshold
    
    def get_effect_on_gene(self, gene_id: str, environmental_factors: Dict[str, float]) -> float:
        """
        Calcule l'effet de l'élément régulateur sur un gène spécifique.
        
        Args:
            gene_id: ID du gène cible
            environmental_factors: Dictionnaire des facteurs environnementaux
            
        Returns:
            float: Effet sur l'expression du gène (-1.0 à 1.0)
        """
        if gene_id not in self.target_genes:
            return 0.0
            
        activity = self.calculate_activity(environmental_factors)
        
        # Si l'activité est inférieure au seuil, pas d'effet
        if activity < self.activation_threshold:
            return 0.0
            
        # Calculer l'effet en fonction de l'activité et de la force
        effect = (activity - self.activation_threshold) / (1.0 - self.activation_threshold) * self.effect_strength
        
        # Si c'est un répresseur, inverser l'effet
        if not self.is_enhancer:
            effect = -effect
            
        return effect

class ArchitectGene:
    """Gène architecte contrôlant le développement et la morphologie."""
    
    def __init__(self, 
                 gene_id: str,
                 target_traits: List[str],
                 expression_pattern: Dict[str, float],
                 effect_functions: Dict[str, Callable],
                 regulatory_elements: List[RegulatoryElement] = None,
                 pleiotropy_map: Dict[str, float] = None):
        """
        Initialise un gène architecte.
        
        Args:
            gene_id: Identifiant unique du gène
            target_traits: Liste des traits phénotypiques ciblés
            expression_pattern: Motif d'expression selon les stades de développement
            effect_functions: Fonctions calculant l'effet sur chaque trait
            regulatory_elements: Éléments régulateurs contrôlant ce gène
            pleiotropy_map: Carte des effets pléiotropiques sur d'autres traits
        """
        self.id = gene_id
        self.target_traits = target_traits
        self.expression_pattern = expression_pattern
        self.effect_functions = effect_functions
        self.regulatory_elements = regulatory_elements or []
        self.pleiotropy_map = pleiotropy_map or {}
        self.current_expression = 0.0
        self.is_mutated = False
        self.mutation_effect = 0.0
        
    def calculate_expression(self, developmental_stage: str, environmental_factors: Dict[str, float]) -> float:
        """
        Calcule le niveau d'expression du gène architecte.
        
        Args:
            developmental_stage: Stade de développement actuel
            environmental_factors: Facteurs environnementaux
            
        Returns:
            float: Niveau d'expression (0.0 à 1.0)
        """
        # Expression de base selon le stade de développement
        base_expression = self.expression_pattern.get(developmental_stage, 0.0)
        
        # Ajuster l'expression en fonction des éléments régulateurs
        regulatory_effect = 0.0
        for element in self.regulatory_elements:
            effect = element.get_effect_on_gene(self.id, environmental_factors)
            regulatory_effect += effect
        
        # Limiter l'effet régulateur
        regulatory_effect = max(-0.8, min(0.8, regulatory_effect))
        
        # Calculer l'expression finale
        final_expression = base_expression * (1.0 + regulatory_effect)
        
        # Appliquer l'effet des mutations si présentes
        if self.is_mutated:
            final_expression *= (1.0 + self.mutation_effect)
        
        # Limiter l'expression entre 0 et 1
        self.current_expression = max(0.0, min(1.0, final_expression))
        return self.current_expression
    
    def calculate_effect_on_trait(self, trait_name: str, developmental_stage: str, 
                                environmental_factors: Dict[str, float]) -> float:
        """
        Calcule l'effet du gène sur un trait spécifique.
        
        Args:
            trait_name: Nom du trait
            developmental_stage: Stade de développement actuel
            environmental_factors: Facteurs environnementaux
            
        Returns:
            float: Effet sur le trait
        """
        # Si le trait n'est pas ciblé par ce gène, vérifier les effets pléiotropiques
        if trait_name not in self.target_traits:
            return self.pleiotropy_map.get(trait_name, 0.0) * self.current_expression
            
        # Calculer l'expression du gène
        expression = self.calculate_expression(developmental_stage, environmental_factors)
        
        # Si le gène n'est pas exprimé, pas d'effet
        if expression <= 0.0:
            return 0.0
            
        # Utiliser la fonction d'effet spécifique au trait si disponible
        if trait_name in self.effect_functions:
            return self.effect_functions[trait_name](expression, environmental_factors)
            
        # Sinon, effet proportionnel à l'expression
        return expression
    
    def mutate(self, mutation_rate: float) -> bool:
        """
        Applique une mutation aléatoire au gène architecte.
        
        Args:
            mutation_rate: Taux de mutation (0.0 à 1.0)
            
        Returns:
            bool: True si une mutation s'est produite, False sinon
        """
        if random.random() < mutation_rate:
            # Déterminer le type de mutation
            mutation_type = random.choices(
                ["expression", "target", "regulation", "pleiotropy"],
                weights=[0.5, 0.2, 0.2, 0.1]
            )[0]
            
            if mutation_type == "expression":
                # Mutation affectant le niveau d'expression
                self.is_mutated = True
                self.mutation_effect = random.gauss(0, 0.2)
                
            elif mutation_type == "target":
                # Mutation affectant les traits ciblés
                if random.random() < 0.5 and self.target_traits:
                    # Perdre un trait cible
                    trait_to_remove = random.choice(self.target_traits)
                    self.target_traits.remove(trait_to_remove)
                    # Ajouter comme effet pléiotropique avec effet réduit
                    self.pleiotropy_map[trait_to_remove] = random.uniform(0.1, 0.3)
                else:
                    # Gagner un nouveau trait cible (simulé)
                    new_trait = f"trait_{random.randint(1, 20)}"
                    if new_trait not in self.target_traits:
                        self.target_traits.append(new_trait)
                        
            elif mutation_type == "regulation":
                # Mutation affectant la régulation
                if self.regulatory_elements:
                    element = random.choice(self.regulatory_elements)
                    # Modifier le seuil d'activation ou la force
                    if random.random() < 0.5:
                        element.activation_threshold += random.gauss(0, 0.1)
                        element.activation_threshold = max(0.1, min(0.9, element.activation_threshold))
                    else:
                        element.effect_strength += random.gauss(0, 0.1)
                        element.effect_strength = max(0.1, min(1.0, element.effect_strength))
                        
            elif mutation_type == "pleiotropy":
                # Mutation affectant les effets pléiotropiques
                if random.random() < 0.7 and self.pleiotropy_map:
                    # Modifier un effet existant
                    trait = random.choice(list(self.pleiotropy_map.keys()))
                    self.pleiotropy_map[trait] += random.gauss(0, 0.1)
                    self.pleiotropy_map[trait] = max(-0.5, min(0.5, self.pleiotropy_map[trait]))
                else:
                    # Ajouter un nouvel effet
                    new_trait = f"trait_{random.randint(1, 20)}"
                    if new_trait not in self.pleiotropy_map:
                        self.pleiotropy_map[new_trait] = random.uniform(-0.3, 0.3)
            
            return True
        
        return False

class GeneRegulatoryNetwork:
    """Réseau de régulation génétique contrôlant l'expression des gènes."""
    
    def __init__(self):
        """Initialise un réseau de régulation génétique."""
        self.architect_genes = {}  # {gene_id: ArchitectGene}
        self.regulatory_elements = {}  # {element_id: RegulatoryElement}
        self.gene_interactions = {}  # {gene_id: [gene_id]}
        self.developmental_stages = ["zygote", "embryo", "juvenile", "adult", "senescent"]
        
    def add_architect_gene(self, gene: ArchitectGene):
        """Ajoute un gène architecte au réseau."""
        self.architect_genes[gene.id] = gene
        
        # Mettre à jour les interactions
        self.gene_interactions[gene.id] = []
        
        # Ajouter les éléments régulateurs
        for element in gene.regulatory_elements:
            if element.id not in self.regulatory_elements:
                self.regulatory_elements[element.id] = element
            
            # Ajouter les interactions avec les gènes ciblés
            for target_id in element.target_genes:
                if target_id in self.architect_genes and target_id != gene.id:
                    self.gene_interactions[gene.id].append(target_id)
    
    def add_regulatory_element(self, element: RegulatoryElement):
        """Ajoute un élément régulateur au réseau."""
        self.regulatory_elements[element.id] = element
        
        # Mettre à jour les interactions
        for gene_id in element.target_genes:
            if gene_id in self.architect_genes:
                gene = self.architect_genes[gene_id]
                if element not in gene.regulatory_elements:
                    gene.regulatory_elements.append(element)
    
    def calculate_phenotype(self, developmental_stage: str, 
                          environmental_factors: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule le phénotype résultant de l'expression des gènes architectes.
        
        Args:
            developmental_stage: Stade de développement actuel
            environmental_factors: Facteurs environnementaux
            
        Returns:
            Dict[str, float]: Valeurs des traits phénotypiques
        """
        if developmental_stage not in self.developmental_stages:
            developmental_stage = "adult"  # Par défaut
            
        # Initialiser le phénotype
        phenotype = {}
        
        # Calculer l'effet de chaque gène architecte
        for gene in self.architect_genes.values():
            # Calculer l'expression du gène
            expression = gene.calculate_expression(developmental_stage, environmental_factors)
            
            # Calculer l'effet sur chaque trait ciblé
            for trait in gene.target_traits:
                effect = gene.calculate_effect_on_trait(trait, developmental_stage, environmental_factors)
                
                if trait not in phenotype:
                    phenotype[trait] = 0.0
                    
                phenotype[trait] += effect
            
            # Calculer les effets pléiotropiques
            for trait, effect_strength in gene.pleiotropy_map.items():
                if trait not in phenotype:
                    phenotype[trait] = 0.0
                    
                phenotype[trait] += effect_strength * expression
        
        # Normaliser les valeurs des traits
        for trait in phenotype:
            phenotype[trait] = max(0.0, min(1.0, phenotype[trait]))
            
        return phenotype
    
    def mutate_network(self, mutation_rate: float) -> int:
        """
        Applique des mutations aléatoires au réseau.
        
        Args:
            mutation_rate: Taux de mutation (0.0 à 1.0)
            
        Returns:
            int: Nombre de mutations produites
        """
        mutation_count = 0
        
        # Muter les gènes architectes
        for gene in self.architect_genes.values():
            if gene.mutate(mutation_rate):
                mutation_count += 1
                
        # Muter les éléments régulateurs
        for element in self.regulatory_elements.values():
            if random.random() < mutation_rate:
                mutation_count += 1
                
                # Déterminer le type de mutation
                mutation_type = random.choices(
                    ["threshold", "strength", "target", "sensitivity"],
                    weights=[0.3, 0.3, 0.2, 0.2]
                )[0]
                
                if mutation_type == "threshold":
                    # Modifier le seuil d'activation
                    element.activation_threshold += random.gauss(0, 0.1)
                    element.activation_threshold = max(0.1, min(0.9, element.activation_threshold))
                    
                elif mutation_type == "strength":
                    # Modifier la force de l'effet
                    element.effect_strength += random.gauss(0, 0.1)
                    element.effect_strength = max(0.1, min(1.0, element.effect_strength))
                    
                elif mutation_type == "target":
                    # Modifier les gènes ciblés
                    if random.random() < 0.5 and element.target_genes:
                        # Perdre un gène cible
                        gene_to_remove = random.choice(element.target_genes)
                        element.target_genes.remove(gene_to_remove)
                    else:
                        # Gagner un nouveau gène cible
                        available_genes = [g for g in self.architect_genes.keys() 
                                         if g not in element.target_genes]
                        if available_genes:
                            new_target = random.choice(available_genes)
                            element.target_genes.append(new_target)
                            
                elif mutation_type == "sensitivity":
                    # Modifier la sensibilité environnementale
                    if random.random() < 0.7 and element.environmental_sensitivity:
                        # Modifier une sensibilité existante
                        factor = random.choice(list(element.environmental_sensitivity.keys()))
                        element.environmental_sensitivity[factor] += random.gauss(0, 0.1)
                        element.environmental_sensitivity[factor] = max(-0.5, min(0.5, element.environmental_sensitivity[factor]))
                    else:
                        # Ajouter une nouvelle sensibilité
                        new_factor = f"factor_{random.randint(1, 10)}"
                        if new_factor not in element.environmental_sensitivity:
                            element.environmental_sensitivity[new_factor] = random.uniform(-0.3, 0.3)
        
        # Possibilité d'ajouter un nouveau gène architecte (duplication)
        if random.random() < mutation_rate * 0.1 and self.architect_genes:
            mutation_count += 1
            
            # Dupliquer un gène existant
            source_gene = random.choice(list(self.architect_genes.values()))
            new_id = f"{source_gene.id}_dup_{random.randint(1000, 9999)}"
            
            # Créer une copie avec quelques modifications
            new_gene = ArchitectGene(
                gene_id=new_id,
                target_traits=source_gene.target_traits.copy(),
                expression_pattern={k: v * random.uniform(0.8, 1.2) for k, v in source_gene.expression_pattern.items()},
                effect_functions=source_gene.effect_functions.copy(),
                regulatory_elements=source_gene.regulatory_elements.copy(),
                pleiotropy_map={k: v * random.uniform(0.8, 1.2) for k, v in source_gene.pleiotropy_map.items()}
            )
            
            # Ajouter le nouveau gène au réseau
            self.add_architect_gene(new_gene)
            
        return mutation_count
    
    def get_gene_expression_profile(self, developmental_stage: str, 
                                  environmental_factors: Dict[str, float]) -> Dict[str, float]:
        """
        Obtient le profil d'expression de tous les gènes architectes.
        
        Args:
            developmental_stage: Stade de développement actuel
            environmental_factors: Facteurs environnementaux
            
        Returns:
            Dict[str, float]: Niveaux d'expression des gènes
        """
        expression_profile = {}
        
        for gene_id, gene in self.architect_genes.items():
            expression = gene.calculate_expression(developmental_stage, environmental_factors)
            expression_profile[gene_id] = expression
            
        return expression_profile

# Fonctions utilitaires pour créer des gènes architectes et des éléments régulateurs
def create_hox_gene(gene_id: str, target_traits: List[str]) -> ArchitectGene:
    """
    Crée un gène Hox (gène architecte contrôlant le développement spatial).
    
    Args:
        gene_id: Identifiant du gène
        target_traits: Traits ciblés par ce gène
        
    Returns:
        ArchitectGene: Gène Hox
    """
    # Motif d'expression typique d'un gène Hox
    expression_pattern = {
        "zygote": 0.0,
        "embryo": 0.8,
        "juvenile": 0.4,
        "adult": 0.1,
        "senescent": 0.05
    }
    
    # Fonctions d'effet sur les traits
    effect_functions = {}
    for trait in target_traits:
        # Fonction générique pour les gènes Hox
        effect_functions[trait] = lambda expr, env: expr * (1.0 + 0.2 * env.get("morphogen_gradient", 0.0))
    
    # Effets pléiotropiques
    pleiotropy_map = {
        "growth_rate": 0.2,
        "metabolism_efficiency": 0.1,
        "development_speed": 0.3
    }
    
    # Élément régulateur contrôlant ce gène
    regulatory_element = RegulatoryElement(
        element_id=f"{gene_id}_enhancer",
        target_genes=[gene_id],
        activation_threshold=0.3,
        effect_strength=0.7,
        is_enhancer=True,
        environmental_sensitivity={
            "temperature": 0.2,
            "morphogen_gradient": 0.5
        }
    )
    
    return ArchitectGene(
        gene_id=gene_id,
        target_traits=target_traits,
        expression_pattern=expression_pattern,
        effect_functions=effect_functions,
        regulatory_elements=[regulatory_element],
        pleiotropy_map=pleiotropy_map
    )

def create_developmental_gene(gene_id: str, developmental_stage: str, target_traits: List[str]) -> ArchitectGene:
    """
    Crée un gène de développement spécifique à un stade.
    
    Args:
        gene_id: Identifiant du gène
        developmental_stage: Stade de développement principal
        target_traits: Traits ciblés par ce gène
        
    Returns:
        ArchitectGene: Gène de développement
    """
    # Motif d'expression concentré sur un stade spécifique
    expression_pattern = {
        "zygote": 0.1,
        "embryo": 0.1,
        "juvenile": 0.1,
        "adult": 0.1,
        "senescent": 0.1
    }
    expression_pattern[developmental_stage] = 0.9
    
    # Fonctions d'effet sur les traits
    effect_functions = {}
    for trait in target_traits:
        # Fonction spécifique au stade de développement
        effect_functions[trait] = lambda expr, env: expr * (1.0 + 0.3 * env.get("nutrient_availability", 0.0))
    
    # Élément régulateur contrôlant ce gène
    regulatory_element = RegulatoryElement(
        element_id=f"{gene_id}_regulator",
        target_genes=[gene_id],
        activation_threshold=0.4,
        effect_strength=0.6,
        is_enhancer=True,
        environmental_sensitivity={
            "nutrient_availability": 0.4,
            "stress_level": -0.3
        }
    )
    
    return ArchitectGene(
        gene_id=gene_id,
        target_traits=target_traits,
        expression_pattern=expression_pattern,
        effect_functions=effect_functions,
        regulatory_elements=[regulatory_element],
        pleiotropy_map={}
    )

def create_environmental_response_gene(gene_id: str, environmental_factor: str, 
                                     target_traits: List[str]) -> ArchitectGene:
    """
    Crée un gène de réponse environnementale.
    
    Args:
        gene_id: Identifiant du gène
        environmental_factor: Facteur environnemental auquel le gène répond
        target_traits: Traits ciblés par ce gène
        
    Returns:
        ArchitectGene: Gène de réponse environnementale
    """
    # Motif d'expression uniforme
    expression_pattern = {
        "zygote": 0.3,
        "embryo": 0.4,
        "juvenile": 0.6,
        "adult": 0.7,
        "senescent": 0.5
    }
    
    # Fonctions d'effet sur les traits
    effect_functions = {}
    for trait in target_traits:
        # Fonction répondant au facteur environnemental
        effect_functions[trait] = lambda expr, env: expr * (1.0 + 0.5 * env.get(environmental_factor, 0.0))
    
    # Élément régulateur très sensible à l'environnement
    regulatory_element = RegulatoryElement(
        element_id=f"{gene_id}_sensor",
        target_genes=[gene_id],
        activation_threshold=0.2,
        effect_strength=0.8,
        is_enhancer=True,
        environmental_sensitivity={
            environmental_factor: 0.8
        }
    )
    
    return ArchitectGene(
        gene_id=gene_id,
        target_traits=target_traits,
        expression_pattern=expression_pattern,
        effect_functions=effect_functions,
        regulatory_elements=[regulatory_element],
        pleiotropy_map={}
    )

def create_gene_regulatory_network() -> GeneRegulatoryNetwork:
    """
    Crée un réseau de régulation génétique de base.
    
    Returns:
        GeneRegulatoryNetwork: Réseau de régulation génétique
    """
    network = GeneRegulatoryNetwork()
    
    # Ajouter quelques gènes Hox
    hox_a = create_hox_gene("hox_a", ["body_plan", "segment_identity", "appendage_development"])
    hox_b = create_hox_gene("hox_b", ["neural_development", "segment_identity"])
    hox_c = create_hox_gene("hox_c", ["skeletal_development", "organ_positioning"])
    
    # Ajouter des gènes de développement spécifiques aux stades
    embryo_gene = create_developmental_gene("embryo_dev", "embryo", ["growth_rate", "cell_differentiation"])
    juvenile_gene = create_developmental_gene("juvenile_dev", "juvenile", ["growth_rate", "metabolism_rate"])
    adult_gene = create_developmental_gene("adult_dev", "adult", ["reproduction", "metabolism_efficiency"])
    
    # Ajouter des gènes de réponse environnementale
    temp_response = create_environmental_response_gene("temp_response", "temperature", 
                                                    ["metabolism_rate", "temperature_tolerance"])
    stress_response = create_environmental_response_gene("stress_response", "stress_level",
                                                      ["immune_system", "energy_efficiency"])
    
    # Ajouter tous les gènes au réseau
    network.add_architect_gene(hox_a)
    network.add_architect_gene(hox_b)
    network.add_architect_gene(hox_c)
    network.add_architect_gene(embryo_gene)
    network.add_architect_gene(juvenile_gene)
    network.add_architect_gene(adult_gene)
    network.add_architect_gene(temp_response)
    network.add_architect_gene(stress_response)
    
    # Ajouter des interactions entre gènes
    # Élément régulateur qui connecte hox_a et hox_b
    hox_interaction = RegulatoryElement(
        element_id="hox_ab_interaction",
        target_genes=["hox_b"],
        activation_threshold=0.4,
        effect_strength=0.5,
        is_enhancer=True,
        environmental_sensitivity={}
    )
    
    # Ajouter l'élément à hox_a
    hox_a.regulatory_elements.append(hox_interaction)
    
    # Mettre à jour le réseau
    network.add_regulatory_element(hox_interaction)
    
    return network