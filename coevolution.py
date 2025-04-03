"""
Module de coévolution pour BioEvolve
Implémente des mécanismes de coévolution et d'interactions écologiques
basés sur les principes scientifiques de l'évolution
"""

import random
import math
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set, Any, Callable
import uuid

class InteractionType(Enum):
    """Types d'interactions écologiques entre espèces."""
    PREDATION = 0        # Une espèce se nourrit de l'autre
    COMPETITION = 1      # Compétition pour les ressources
    MUTUALISM = 2        # Bénéfice mutuel
    COMMENSALISM = 3     # Une espèce bénéficie sans affecter l'autre
    PARASITISM = 4       # Une espèce bénéficie au détriment de l'autre
    AMENSALISM = 5       # Une espèce est affectée négativement sans bénéfice pour l'autre
    NEUTRALISM = 6       # Pas d'interaction significative

class CoevolutionaryRelationship:
    """Représente une relation coévolutive entre deux espèces."""
    
    def __init__(self, 
                 species_a_id: str,
                 species_b_id: str,
                 interaction_type: InteractionType,
                 strength: float,
                 trait_couplings: Dict[str, Dict[str, float]],
                 description: str = None):
        """
        Initialise une relation coévolutive.
        
        Args:
            species_a_id: ID de la première espèce
            species_b_id: ID de la deuxième espèce
            interaction_type: Type d'interaction écologique
            strength: Force de l'interaction (0.0 à 1.0)
            trait_couplings: Couplages entre traits des deux espèces
            description: Description textuelle de la relation
        """
        self.id = str(uuid.uuid4())
        self.species_a_id = species_a_id
        self.species_b_id = species_b_id
        self.interaction_type = interaction_type
        self.strength = strength
        self.trait_couplings = trait_couplings
        self.description = description or f"Relation coévolutive {interaction_type.name}"
        self.establishment_time = 0
        self.evolutionary_history = []
        
    def calculate_fitness_effect(self, species_id: str, traits: Dict[str, float]) -> float:
        """
        Calcule l'effet de cette relation sur la fitness d'une espèce.
        
        Args:
            species_id: ID de l'espèce à évaluer
            traits: Traits phénotypiques de l'espèce
            
        Returns:
            float: Effet sur la fitness (-1.0 à 1.0)
        """
        # Déterminer si c'est l'espèce A ou B
        is_species_a = species_id == self.species_a_id
        
        # Effet de base selon le type d'interaction
        base_effect = self._get_base_effect(is_species_a)
        
        # Ajuster l'effet en fonction des traits
        trait_effect = 0.0
        trait_count = 0
        
        for trait_name, trait_value in traits.items():
            # Vérifier si ce trait est impliqué dans un couplage
            if trait_name in self.trait_couplings:
                trait_count += 1
                
                # L'effet dépend de la valeur du trait et du couplage
                coupling_effect = 0.0
                
                for coupled_trait, coupling_strength in self.trait_couplings[trait_name].items():
                    # Pour simplifier, on suppose que la valeur optimale est 0.5
                    # Dans un système réel, cela dépendrait des traits de l'autre espèce
                    optimal_value = 0.5
                    
                    # L'effet est maximal quand le trait est à sa valeur optimale
                    trait_match = 1.0 - abs(trait_value - optimal_value) * 2.0
                    coupling_effect += trait_match * coupling_strength
                
                trait_effect += coupling_effect
        
        # Calculer l'effet moyen des traits
        if trait_count > 0:
            trait_effect /= trait_count
        
        # Effet final combinant l'effet de base et l'effet des traits
        final_effect = base_effect * self.strength * (0.5 + 0.5 * trait_effect)
        
        return final_effect
    
    def _get_base_effect(self, is_species_a: bool) -> float:
        """
        Obtient l'effet de base selon le type d'interaction.
        
        Args:
            is_species_a: True si c'est l'espèce A, False si c'est l'espèce B
            
        Returns:
            float: Effet de base (-1.0 à 1.0)
        """
        if self.interaction_type == InteractionType.PREDATION:
            return 0.8 if is_species_a else -0.8
        elif self.interaction_type == InteractionType.COMPETITION:
            return -0.5  # Négatif pour les deux espèces
        elif self.interaction_type == InteractionType.MUTUALISM:
            return 0.6  # Positif pour les deux espèces
        elif self.interaction_type == InteractionType.COMMENSALISM:
            return 0.5 if is_species_a else 0.0
        elif self.interaction_type == InteractionType.PARASITISM:
            return 0.7 if is_species_a else -0.6
        elif self.interaction_type == InteractionType.AMENSALISM:
            return 0.0 if is_species_a else -0.4
        else:  # NEUTRALISM
            return 0.0
    
    def update_evolutionary_history(self, year: int, species_a_traits: Dict[str, float], 
                                  species_b_traits: Dict[str, float]):
        """
        Met à jour l'historique évolutif de cette relation.
        
        Args:
            year: Année de simulation
            species_a_traits: Traits de l'espèce A
            species_b_traits: Traits de l'espèce B
        """
        # Calculer la "distance" évolutive entre les traits couplés
        evolutionary_distance = 0.0
        coupling_count = 0
        
        for trait_a, couplings in self.trait_couplings.items():
            if trait_a in species_a_traits:
                for trait_b, strength in couplings.items():
                    if trait_b in species_b_traits:
                        # Distance entre les traits couplés
                        trait_distance = abs(species_a_traits[trait_a] - species_b_traits[trait_b])
                        evolutionary_distance += trait_distance * strength
                        coupling_count += 1
        
        if coupling_count > 0:
            evolutionary_distance /= coupling_count
        
        # Enregistrer l'état évolutif
        self.evolutionary_history.append({
            "year": year,
            "evolutionary_distance": evolutionary_distance,
            "species_a_traits": species_a_traits.copy(),
            "species_b_traits": species_b_traits.copy()
        })
    
    def get_coevolutionary_pressure(self, species_id: str, other_species_traits: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule la pression coévolutive exercée sur une espèce.
        
        Args:
            species_id: ID de l'espèce à évaluer
            other_species_traits: Traits de l'autre espèce
            
        Returns:
            Dict[str, float]: Pression sur chaque trait (-1.0 à 1.0)
        """
        # Déterminer si c'est l'espèce A ou B
        is_species_a = species_id == self.species_a_id
        
        # Traits de cette espèce impliqués dans des couplages
        if is_species_a:
            species_traits = self.trait_couplings.keys()
        else:
            # Pour l'espèce B, il faut inverser les couplages
            species_traits = set()
            for couplings in self.trait_couplings.values():
                species_traits.update(couplings.keys())
        
        # Calculer la pression sur chaque trait
        pressures = {}
        
        for trait in species_traits:
            # Trouver les couplages impliquant ce trait
            if is_species_a:
                # Pour l'espèce A, le trait est la clé principale
                if trait in self.trait_couplings:
                    pressure = 0.0
                    
                    for other_trait, strength in self.trait_couplings[trait].items():
                        if other_trait in other_species_traits:
                            # La pression dépend de la valeur du trait de l'autre espèce
                            other_value = other_species_traits[other_trait]
                            
                            # Calculer la direction de la pression
                            # Si other_value > 0.5, pression positive, sinon négative
                            direction = (other_value - 0.5) * 2.0
                            
                            pressure += direction * strength
                    
                    pressures[trait] = pressure * self.strength
            else:
                # Pour l'espèce B, le trait est dans les sous-dictionnaires
                pressure = 0.0
                count = 0
                
                for a_trait, couplings in self.trait_couplings.items():
                    if trait in couplings and a_trait in other_species_traits:
                        strength = couplings[trait]
                        a_value = other_species_traits[a_trait]
                        
                        # Calculer la direction de la pression
                        direction = (a_value - 0.5) * 2.0
                        
                        pressure += direction * strength
                        count += 1
                
                if count > 0:
                    pressures[trait] = pressure * self.strength / count
        
        return pressures

class CoevolutionSystem:
    """Système gérant les relations coévolutives entre espèces."""
    
    def __init__(self):
        """Initialise le système de coévolution."""
        self.relationships = {}  # {relationship_id: CoevolutionaryRelationship}
        self.species_relationships = {}  # {species_id: [relationship_id]}
        self.interaction_network = {}  # {(species_a_id, species_b_id): relationship_id}
        
    def add_relationship(self, relationship: CoevolutionaryRelationship):
        """
        Ajoute une relation coévolutive au système.
        
        Args:
            relationship: Relation coévolutive à ajouter
        """
        self.relationships[relationship.id] = relationship
        
        # Mettre à jour les relations par espèce
        if relationship.species_a_id not in self.species_relationships:
            self.species_relationships[relationship.species_a_id] = []
        self.species_relationships[relationship.species_a_id].append(relationship.id)
        
        if relationship.species_b_id not in self.species_relationships:
            self.species_relationships[relationship.species_b_id] = []
        self.species_relationships[relationship.species_b_id].append(relationship.id)
        
        # Mettre à jour le réseau d'interactions
        self.interaction_network[(relationship.species_a_id, relationship.species_b_id)] = relationship.id
        self.interaction_network[(relationship.species_b_id, relationship.species_a_id)] = relationship.id
    
    def get_species_relationships(self, species_id: str) -> List[CoevolutionaryRelationship]:
        """
        Récupère toutes les relations coévolutives impliquant une espèce.
        
        Args:
            species_id: ID de l'espèce
            
        Returns:
            List[CoevolutionaryRelationship]: Liste des relations
        """
        if species_id not in self.species_relationships:
            return []
            
        return [self.relationships[rel_id] for rel_id in self.species_relationships[species_id]]
    
    def get_relationship(self, species_a_id: str, species_b_id: str) -> Optional[CoevolutionaryRelationship]:
        """
        Récupère la relation coévolutive entre deux espèces.
        
        Args:
            species_a_id: ID de la première espèce
            species_b_id: ID de la deuxième espèce
            
        Returns:
            Optional[CoevolutionaryRelationship]: Relation coévolutive ou None
        """
        rel_id = self.interaction_network.get((species_a_id, species_b_id))
        
        if rel_id:
            return self.relationships[rel_id]
            
        return None
    
    def calculate_fitness_effects(self, species_id: str, traits: Dict[str, float], 
                                other_species: Dict[str, Dict[str, float]]) -> float:
        """
        Calcule l'effet combiné de toutes les relations sur la fitness d'une espèce.
        
        Args:
            species_id: ID de l'espèce à évaluer
            traits: Traits phénotypiques de l'espèce
            other_species: Traits des autres espèces {species_id: {trait: value}}
            
        Returns:
            float: Effet combiné sur la fitness
        """
        if species_id not in self.species_relationships:
            return 0.0
            
        total_effect = 0.0
        relationship_count = 0
        
        for rel_id in self.species_relationships[species_id]:
            relationship = self.relationships[rel_id]
            
            # Déterminer l'autre espèce
            other_id = relationship.species_b_id if species_id == relationship.species_a_id else relationship.species_a_id
            
            # Vérifier si les traits de l'autre espèce sont disponibles
            if other_id in other_species:
                effect = relationship.calculate_fitness_effect(species_id, traits)
                total_effect += effect
                relationship_count += 1
        
        # Calculer l'effet moyen
        if relationship_count > 0:
            return total_effect / relationship_count
        else:
            return 0.0
    
    def get_coevolutionary_pressures(self, species_id: str, 
                                   other_species: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calcule les pressions coévolutives combinées sur une espèce.
        
        Args:
            species_id: ID de l'espèce à évaluer
            other_species: Traits des autres espèces {species_id: {trait: value}}
            
        Returns:
            Dict[str, float]: Pressions combinées sur chaque trait
        """
        if species_id not in self.species_relationships:
            return {}
            
        combined_pressures = {}
        
        for rel_id in self.species_relationships[species_id]:
            relationship = self.relationships[rel_id]
            
            # Déterminer l'autre espèce
            other_id = relationship.species_b_id if species_id == relationship.species_a_id else relationship.species_a_id
            
            # Vérifier si les traits de l'autre espèce sont disponibles
            if other_id in other_species:
                pressures = relationship.get_coevolutionary_pressure(species_id, other_species[other_id])
                
                # Combiner les pressions
                for trait, pressure in pressures.items():
                    if trait not in combined_pressures:
                        combined_pressures[trait] = 0.0
                    combined_pressures[trait] += pressure
        
        return combined_pressures
    
    def update_relationships(self, year: int, all_species_traits: Dict[str, Dict[str, float]]):
        """
        Met à jour toutes les relations coévolutives.
        
        Args:
            year: Année de simulation
            all_species_traits: Traits de toutes les espèces {species_id: {trait: value}}
        """
        for relationship in self.relationships.values():
            # Vérifier si les deux espèces existent toujours
            if (relationship.species_a_id in all_species_traits and 
                relationship.species_b_id in all_species_traits):
                
                # Mettre à jour l'historique évolutif
                relationship.update_evolutionary_history(
                    year,
                    all_species_traits[relationship.species_a_id],
                    all_species_traits[relationship.species_b_id]
                )
    
    def detect_new_relationships(self, species_data: Dict[str, Any], 
                               interaction_threshold: float = 0.3) -> List[CoevolutionaryRelationship]:
        """
        Détecte de nouvelles relations coévolutives potentielles.
        
        Args:
            species_data: Données sur les espèces
            interaction_threshold: Seuil d'interaction pour établir une relation
            
        Returns:
            List[CoevolutionaryRelationship]: Nouvelles relations détectées
        """
        new_relationships = []
        
        # Toutes les paires d'espèces possibles
        species_ids = list(species_data.keys())
        
        for i in range(len(species_ids)):
            for j in range(i + 1, len(species_ids)):
                species_a_id = species_ids[i]
                species_b_id = species_ids[j]
                
                # Vérifier si une relation existe déjà
                if (species_a_id, species_b_id) in self.interaction_network:
                    continue
                
                # Calculer le potentiel d'interaction
                interaction_potential = self._calculate_interaction_potential(
                    species_data[species_a_id],
                    species_data[species_b_id]
                )
                
                # Si le potentiel est suffisant, créer une nouvelle relation
                if interaction_potential >= interaction_threshold:
                    # Déterminer le type d'interaction le plus probable
                    interaction_type = self._determine_interaction_type(
                        species_data[species_a_id],
                        species_data[species_b_id]
                    )
                    
                    # Créer les couplages de traits
                    trait_couplings = self._create_trait_couplings(
                        species_data[species_a_id],
                        species_data[species_b_id]
                    )
                    
                    # Créer la relation
                    relationship = CoevolutionaryRelationship(
                        species_a_id=species_a_id,
                        species_b_id=species_b_id,
                        interaction_type=interaction_type,
                        strength=interaction_potential,
                        trait_couplings=trait_couplings,
                        description=f"Relation {interaction_type.name} entre {species_a_id} et {species_b_id}"
                    )
                    
                    new_relationships.append(relationship)
        
        return new_relationships
    
    def _calculate_interaction_potential(self, species_a_data: Dict[str, Any], 
                                       species_b_data: Dict[str, Any]) -> float:
        """
        Calcule le potentiel d'interaction entre deux espèces.
        
        Args:
            species_a_data: Données de la première espèce
            species_b_data: Données de la deuxième espèce
            
        Returns:
            float: Potentiel d'interaction (0.0 à 1.0)
        """
        # Facteurs influençant le potentiel d'interaction
        
        # 1. Chevauchement d'habitat
        habitat_overlap = 0.5  # Valeur par défaut
        if "habitat" in species_a_data and "habitat" in species_b_data:
            # Calculer le chevauchement réel
            habitat_a = set(species_a_data["habitat"])
            habitat_b = set(species_b_data["habitat"])
            
            if habitat_a and habitat_b:
                habitat_overlap = len(habitat_a & habitat_b) / len(habitat_a | habitat_b)
        
        # 2. Complémentarité écologique
        ecological_complementarity = 0.0
        if "traits" in species_a_data and "traits" in species_b_data:
            # Calculer la complémentarité des traits
            traits_a = species_a_data["traits"]
            traits_b = species_b_data["traits"]
            
            # Traits complémentaires (exemple simplifié)
            complementary_pairs = [
                ("predator", "prey"),
                ("pollinator", "flower"),
                ("host", "symbiont")
            ]
            
            for trait_a, trait_b in complementary_pairs:
                if trait_a in traits_a and trait_b in traits_b:
                    ecological_complementarity += 0.3
                elif trait_b in traits_a and trait_a in traits_b:
                    ecological_complementarity += 0.3
            
            ecological_complementarity = min(1.0, ecological_complementarity)
        
        # 3. Proximité phylogénétique
        phylogenetic_proximity = 0.5  # Valeur par défaut
        if "taxonomy" in species_a_data and "taxonomy" in species_b_data:
            # Calculer la proximité phylogénétique
            taxonomy_a = species_a_data["taxonomy"]
            taxonomy_b = species_b_data["taxonomy"]
            
            # Compter les niveaux taxonomiques communs
            common_levels = 0
            total_levels = 0
            
            for level in taxonomy_a:
                if level in taxonomy_b and taxonomy_a[level] == taxonomy_b[level]:
                    common_levels += 1
                total_levels += 1
            
            if total_levels > 0:
                phylogenetic_proximity = common_levels / total_levels
        
        # Combiner les facteurs
        interaction_potential = (
            habitat_overlap * 0.4 +
            ecological_complementarity * 0.4 +
            (1.0 - phylogenetic_proximity) * 0.2  # Les espèces plus éloignées ont plus de potentiel d'interaction
        )
        
        return interaction_potential
    
    def _determine_interaction_type(self, species_a_data: Dict[str, Any], 
                                  species_b_data: Dict[str, Any]) -> InteractionType:
        """
        Détermine le type d'interaction le plus probable entre deux espèces.
        
        Args:
            species_a_data: Données de la première espèce
            species_b_data: Données de la deuxième espèce
            
        Returns:
            InteractionType: Type d'interaction le plus probable
        """
        # Extraire les traits pertinents
        traits_a = species_a_data.get("traits", {})
        traits_b = species_b_data.get("traits", {})
        
        # Calculer les probabilités pour chaque type d'interaction
        probabilities = {
            InteractionType.PREDATION: 0.0,
            InteractionType.COMPETITION: 0.2,  # Probabilité de base
            InteractionType.MUTUALISM: 0.1,
            InteractionType.COMMENSALISM: 0.1,
            InteractionType.PARASITISM: 0.1,
            InteractionType.AMENSALISM: 0.1,
            InteractionType.NEUTRALISM: 0.4  # Probabilité de base élevée
        }
        
        # Ajuster les probabilités en fonction des traits
        
        # Prédation
        if ("carnivore" in traits_a and "herbivore" in traits_b) or ("carnivore" in traits_b and "herbivore" in traits_a):
            probabilities[InteractionType.PREDATION] += 0.4
        
        # Compétition
        if "diet" in species_a_data and "diet" in species_b_data:
            diet_a = set(species_a_data["diet"])
            diet_b = set(species_b_data["diet"])
            
            if diet_a and diet_b:
                diet_overlap = len(diet_a & diet_b) / len(diet_a | diet_b)
                probabilities[InteractionType.COMPETITION] += diet_overlap * 0.4
        
        # Mutualisme
        if ("pollinator" in traits_a and "flower" in traits_b) or ("pollinator" in traits_b and "flower" in traits_a):
            probabilities[InteractionType.MUTUALISM] += 0.4
        
        # Parasitisme
        if ("parasite" in traits_a) or ("parasite" in traits_b):
            probabilities[InteractionType.PARASITISM] += 0.4
        
        # Commensalisme
        if ("commensal" in traits_a) or ("commensal" in traits_b):
            probabilities[InteractionType.COMMENSALISM] += 0.3
        
        # Normaliser les probabilités
        total = sum(probabilities.values())
        if total > 0:
            probabilities = {k: v / total for k, v in probabilities.items()}
        
        # Choisir le type d'interaction le plus probable
        return max(probabilities.items(), key=lambda x: x[1])[0]
    
    def _create_trait_couplings(self, species_a_data: Dict[str, Any], 
                              species_b_data: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        Crée les couplages de traits entre deux espèces.
        
        Args:
            species_a_data: Données de la première espèce
            species_b_data: Données de la deuxième espèce
            
        Returns:
            Dict[str, Dict[str, float]]: Couplages de traits
        """
        trait_couplings = {}
        
        # Extraire les traits pertinents
        traits_a = species_a_data.get("traits", {})
        traits_b = species_b_data.get("traits", {})
        
        # Définir des paires de traits potentiellement couplés
        potential_couplings = [
            # Prédation
            ("attack_power", "defense_power", 0.7),
            ("speed", "agility", 0.6),
            ("sensory_acuity", "camouflage", 0.5),
            
            # Compétition
            ("foraging_efficiency", "foraging_efficiency", 0.6),
            ("growth_rate", "growth_rate", 0.5),
            
            # Mutualisme
            ("nectar_production", "pollination_efficiency", 0.8),
            ("root_system", "nitrogen_fixation", 0.7),
            
            # Parasitisme
            ("immune_system", "infection_ability", 0.8),
            ("toxin_production", "toxin_resistance", 0.7)
        ]
        
        # Créer les couplages
        for trait_a, trait_b, strength in potential_couplings:
            if trait_a in traits_a and trait_b in traits_b:
                if trait_a not in trait_couplings:
                    trait_couplings[trait_a] = {}
                trait_couplings[trait_a][trait_b] = strength
            
            # Couplage inverse
            if trait_b in traits_a and trait_a in traits_b:
                if trait_b not in trait_couplings:
                    trait_couplings[trait_b] = {}
                trait_couplings[trait_b][trait_a] = strength
        
        return trait_couplings

# Fonctions utilitaires pour créer des relations coévolutives prédéfinies
def create_predator_prey_relationship(predator_id: str, prey_id: str, strength: float = 0.7) -> CoevolutionaryRelationship:
    """
    Crée une relation prédateur-proie.
    
    Args:
        predator_id: ID de l'espèce prédatrice
        prey_id: ID de l'espèce proie
        strength: Force de l'interaction
        
    Returns:
        CoevolutionaryRelationship: Relation prédateur-proie
    """
    # Couplages de traits typiques d'une relation prédateur-proie
    trait_couplings = {
        # Traits du prédateur
        "speed": {"speed": 0.8},  # Vitesse du prédateur vs vitesse de la proie
        "attack_power": {"defense_power": 0.7},  # Attaque vs défense
        "sensory_acuity": {"camouflage": 0.6},  # Perception vs camouflage
        "metabolism_efficiency": {"energy_content": 0.5}  # Efficacité vs valeur énergétique
    }
    
    return CoevolutionaryRelationship(
        species_a_id=predator_id,
        species_b_id=prey_id,
        interaction_type=InteractionType.PREDATION,
        strength=strength,
        trait_couplings=trait_couplings,
        description=f"Relation prédateur-proie entre {predator_id} (prédateur) et {prey_id} (proie)"
    )

def create_plant_pollinator_relationship(plant_id: str, pollinator_id: str, strength: float = 0.6) -> CoevolutionaryRelationship:
    """
    Crée une relation plante-pollinisateur.
    
    Args:
        plant_id: ID de l'espèce végétale
        pollinator_id: ID de l'espèce pollinisatrice
        strength: Force de l'interaction
        
    Returns:
        CoevolutionaryRelationship: Relation plante-pollinisateur
    """
    # Couplages de traits typiques d'une relation plante-pollinisateur
    trait_couplings = {
        # Traits de la plante
        "flower_shape": {"mouth_parts": 0.9},  # Forme de la fleur vs pièces buccales
        "nectar_production": {"energy_efficiency": 0.8},  # Production de nectar vs efficacité énergétique
        "flower_color": {"color_perception": 0.7},  # Couleur de la fleur vs perception des couleurs
        "flowering_time": {"activity_pattern": 0.6}  # Période de floraison vs période d'activité
    }
    
    return CoevolutionaryRelationship(
        species_a_id=plant_id,
        species_b_id=pollinator_id,
        interaction_type=InteractionType.MUTUALISM,
        strength=strength,
        trait_couplings=trait_couplings,
        description=f"Relation mutualiste entre {plant_id} (plante) et {pollinator_id} (pollinisateur)"
    )

def create_host_parasite_relationship(host_id: str, parasite_id: str, strength: float = 0.7) -> CoevolutionaryRelationship:
    """
    Crée une relation hôte-parasite.
    
    Args:
        host_id: ID de l'espèce hôte
        parasite_id: ID de l'espèce parasite
        strength: Force de l'interaction
        
    Returns:
        CoevolutionaryRelationship: Relation hôte-parasite
    """
    # Couplages de traits typiques d'une relation hôte-parasite
    trait_couplings = {
        # Traits du parasite
        "infection_ability": {"immune_system": 0.9},  # Capacité d'infection vs système immunitaire
        "toxin_resistance": {"toxin_production": 0.8},  # Résistance aux toxines vs production de toxines
        "host_specificity": {"tissue_composition": 0.7},  # Spécificité d'hôte vs composition tissulaire
        "life_cycle": {"longevity": 0.6}  # Cycle de vie vs longévité
    }
    
    return CoevolutionaryRelationship(
        species_a_id=parasite_id,
        species_b_id=host_id,
        interaction_type=InteractionType.PARASITISM,
        strength=strength,
        trait_couplings=trait_couplings,
        description=f"Relation parasitaire entre {parasite_id} (parasite) et {host_id} (hôte)"
    )

def create_competitive_relationship(species_a_id: str, species_b_id: str, strength: float = 0.5) -> CoevolutionaryRelationship:
    """
    Crée une relation de compétition.
    
    Args:
        species_a_id: ID de la première espèce
        species_b_id: ID de la deuxième espèce
        strength: Force de l'interaction
        
    Returns:
        CoevolutionaryRelationship: Relation de compétition
    """
    # Couplages de traits typiques d'une relation de compétition
    trait_couplings = {
        # Traits de l'espèce A
        "foraging_efficiency": {"foraging_efficiency": 0.8},  # Efficacité de recherche de nourriture
        "growth_rate": {"growth_rate": 0.7},  # Taux de croissance
        "resource_utilization": {"resource_utilization": 0.9},  # Utilisation des ressources
        "territorial_behavior": {"territorial_behavior": 0.6}  # Comportement territorial
    }
    
    return CoevolutionaryRelationship(
        species_a_id=species_a_id,
        species_b_id=species_b_id,
        interaction_type=InteractionType.COMPETITION,
        strength=strength,
        trait_couplings=trait_couplings,
        description=f"Relation de compétition entre {species_a_id} et {species_b_id}"
    )

def create_coevolution_system() -> CoevolutionSystem:
    """
    Crée un système de coévolution de base.
    
    Returns:
        CoevolutionSystem: Système de coévolution
    """
    system = CoevolutionSystem()
    
    # Exemples de relations coévolutives
    predator_prey = create_predator_prey_relationship("wolf", "rabbit")
    plant_pollinator = create_plant_pollinator_relationship("flower", "bee")
    host_parasite = create_host_parasite_relationship("deer", "tick")
    competition = create_competitive_relationship("lion", "tiger")
    
    # Ajouter les relations au système
    system.add_relationship(predator_prey)
    system.add_relationship(plant_pollinator)
    system.add_relationship(host_parasite)
    system.add_relationship(competition)
    
    return system