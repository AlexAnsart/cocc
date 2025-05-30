import logging
import os
import datetime
from typing import Optional

# Configuration du logger de base pour la console (peut être surchargé par BattleLogger)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOG_DIRECTORY = "logs/battles" # Répertoire pour les logs de bataille

class BattleLogger:
    def __init__(self, battle_id: Optional[str] = None, log_to_console: bool = True, log_to_file: bool = True):
        if battle_id is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self.battle_id = f"battle_{timestamp}"
        else:
            self.battle_id = battle_id
            
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        self.logger = logging.getLogger(self.battle_id)
        self.logger.setLevel(logging.DEBUG) # Capture tous les niveaux, les handlers décident quoi afficher/écrire
        
        # Empêcher la propagation aux loggers parents (comme le root logger) pour éviter les doublons si console_handler est ajouté au root
        self.logger.propagate = False

        # Nettoyer les handlers existants pour ce logger (utile si réinitialisé ou en tests)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        if self.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO) # Niveau pour la console
            formatter = logging.Formatter('%(asctime)s - BATTLE:%(name)s - TICK:%(tick)s - T:%(sim_time).2fs - %(message)s')
            # Ajout d'un filtre pour ajouter tick et sim_time au record, s'ils ne sont pas là
            console_handler.addFilter(ContextualLogFilter())
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if self.log_to_file:
            os.makedirs(LOG_DIRECTORY, exist_ok=True)
            log_file_path = os.path.join(LOG_DIRECTORY, f"{self.battle_id}.log")
            
            file_handler = logging.FileHandler(log_file_path, mode='w') # 'w' pour écraser les logs d'une même bataille si relancée (rare avec timestamp)
            file_handler.setLevel(logging.DEBUG) # Loggue tout (DEBUG et plus) dans le fichier
            # Format pour le fichier: plus détaillé, incluant le levelname
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - BATTLE:%(name)s - TICK:%(tick)s - T:%(sim_time).2fs - %(message)s')
            file_handler.addFilter(ContextualLogFilter())
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            if self.log_to_console: # Si console aussi, informe où les logs fichiers sont
                 self.logger.info(f"Logging detailed battle events to file: {log_file_path}", extra={'tick': 0, 'sim_time': 0.0})


    def log(self, message: str, level: int = logging.INFO, tick: Optional[int] = None, sim_time: Optional[float] = None, **kwargs):
        extra_info = {'tick': tick, 'sim_time': sim_time}
        extra_info.update(kwargs)
        self.logger.log(level, message, extra=extra_info)

    def debug(self, message: str, tick: Optional[int] = None, sim_time: Optional[float] = None, **kwargs):
        self.log(message, logging.DEBUG, tick, sim_time, **kwargs)

    def info(self, message: str, tick: Optional[int] = None, sim_time: Optional[float] = None, **kwargs):
        self.log(message, logging.INFO, tick, sim_time, **kwargs)

    def warning(self, message: str, tick: Optional[int] = None, sim_time: Optional[float] = None, **kwargs):
        self.log(message, logging.WARNING, tick, sim_time, **kwargs)
        
    def error(self, message: str, tick: Optional[int] = None, sim_time: Optional[float] = None, **kwargs):
        self.log(message, logging.ERROR, tick, sim_time, **kwargs)

    def critical(self, message: str, tick: Optional[int] = None, sim_time: Optional[float] = None, **kwargs):
        self.log(message, logging.CRITICAL, tick, sim_time, **kwargs)

class ContextualLogFilter(logging.Filter):
    """A log filter that adds context (tick, sim_time) if not present."""
    def filter(self, record):
        if not hasattr(record, 'tick'):
            record.tick = "N/A"
        if not hasattr(record, 'sim_time'):
            record.sim_time = 0.0 # Default sim_time if not provided
        return True

# Exemple d'utilisation (peut être enlevé ou mis dans un if __name__ == "__main__")
if __name__ == '__main__':
    test_logger = BattleLogger(battle_id="test_battle_001", log_to_console=True, log_to_file=True)
    test_logger.info("Début de la bataille de test.", tick=0, sim_time=0.0)
    test_logger.debug("Une troupe se déplace.", tick=1, sim_time=0.1)
    test_logger.info("Une tour attaque.", tick=2, sim_time=0.2)
    test_logger.warning("HP bas pour une troupe!", tick=3, sim_time=0.3)
    test_logger.info("Fin de la bataille de test.", tick=10, sim_time=1.0)
    
    # Test sans tick/sim_time explicite (utilisera N/A et 0.0 via le filtre)
    test_logger.info("Message de log sans contexte temporel explicite.")

    # Test avec un autre logger pour s'assurer qu'ils sont indépendants
    another_logger = BattleLogger(battle_id="test_battle_002_console_only", log_to_file=False)
    another_logger.info("Ceci est un test pour un logger console uniquement.") 