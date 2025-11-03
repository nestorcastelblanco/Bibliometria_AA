"""
Módulo de definición de términos semilla (ground truth) para análisis.

Define categoría de investigación y palabras clave asociadas que sirven como
referencia (ground truth) para evaluación de términos auto-generados.

Parte del Requerimiento 3: Análisis de frecuencia y evaluación de términos.
"""

# Categoría y lista de palabras asociadas dadas (ground truth)
CATEGORY_NAME = "Concepts of Generative AI in Education"
"""
str: Categoría temática de investigación.

Define el dominio específico de análisis para el corpus bibliográfico.
En este caso, conceptos de IA Generativa aplicados a educación.
"""

SEED_WORDS = [
    "Generative models",
    "Prompting",
    "Machine learning",
    "Multimodality",
    "Fine-tuning",
    "Training data",
    "Algorithmic bias",
    "Explainability",
    "Transparency",
    "Ethics",
    "Privacy",
    "Personalization",
    "Human-AI interaction",
    "AI literacy",
    "Co-creation",
]
"""
List[str]: Términos semilla (ground truth) para evaluación.

Lista curada de palabras clave relevantes para la categoría de investigación.
Sirven como referencia para:
- Calcular frecuencias de términos conocidos
- Evaluar calidad de términos auto-generados
- Baseline para análisis de cobertura temática

Grupos conceptuales:
- Técnicos: Generative models, Machine learning, Fine-tuning, Training data
- Interacción: Prompting, Human-AI interaction, Co-creation
- Capacidades: Multimodality, Personalization
- Ética: Algorithmic bias, Ethics, Privacy, Transparency, Explainability
- Educación: AI literacy

Notas:
    - Términos definidos por expertos del dominio
    - Balancean aspectos técnicos, éticos y educativos
    - Algunos son unigramas, otros bigramas
    - Serán normalizados antes de uso para matcheo robusto
"""
