# 🎬 Outil de traduction de sous-titres vidéo

Transcription automatique de l'audio vidéo, traduction dans la langue cible et génération de fichiers de sous-titres ou intégration dans les vidéos. **Prend en charge la traduction entre 18 langues**.

[English](README.md) | [中文文档](README.zh.md) | [日本語ドキュメント](README.ja.md) | [한국어 문서](README.ko.md) | [Deutsch](README.de.md)

## ✨ Fonctionnalités

- 🎤 **Reconnaissance vocale** : Reconnaissance vocale haute précision avec OpenAI Whisper
- 🌐 **Traduction multilingue** : Traduction entre 18 langues (chinois, anglais, japonais, coréen, français, allemand, espagnol, etc.)
- 🤖 **Multi-moteurs** : Prise en charge de DeepSeek, OpenAI et d'autres moteurs de traduction
- 📄 **Génération de sous-titres** : Formats multiples : SRT, VTT, ASS
- 🎥 **Intégration de sous-titres** : Sous-titres souples et incrustés (hard sub)
- 🌍 **Sous-titres bilingues** : Génération optionnelle de sous-titres bilingues
- 📝 **Résumé vidéo** : Résumé du contenu vidéo par LLM avec points clés, sujets et chronologie
- ⚡ **Accélération matérielle** : Détection automatique de l'encodage matériel (VideoToolbox/NVENC/QSV/AMF) pour un rendu plus rapide des sous-titres incrustés
- 🖥️ **Intégration GUI** : Sortie de progression au format JSON pour une intégration transparente avec les interfaces graphiques
- 💰 **Rapport qualité-prix** : L'API DeepSeek offre des tarifs abordables avec une excellente qualité de traduction
- 🏗️ **Conception modulaire** : Facile à étendre et à maintenir

## 🌍 Langues prises en charge

| Code | Langue | Code | Langue |
|------|--------|------|--------|
| `zh` | 中文 (Chinois) | `en` | English (Anglais) |
| `ja` | 日本語 (Japonais) | `ko` | 한국어 (Coréen) |
| `fr` | Français | `de` | Deutsch (Allemand) |
| `es` | Español (Espagnol) | `ru` | Русский (Russe) |
| `pt` | Português (Portugais) | `it` | Italiano (Italien) |
| `nl` | Nederlands (Néerlandais) | `pl` | Polski (Polonais) |
| `tr` | Türkçe (Turc) | `ar` | العربية (Arabe) |
| `hi` | हिन्दी (Hindi) | `th` | ไทย (Thaï) |
| `vi` | Tiếng Việt (Vietnamien) | `id` | Bahasa Indonesia (Indonésien) |

Utilisez `video-translate --list-languages` pour afficher la liste complète.

## 📁 Structure du projet

```
video-translate/
├── src/
│   └── video_translate/
│       ├── __init__.py      # Initialisation du paquet
│       ├── __main__.py      # Point d'entrée
│       ├── cli.py           # Interface en ligne de commande
│       ├── config.py        # Gestion de la configuration
│       ├── models.py        # Modèles de données
│       ├── transcriber.py   # Module de reconnaissance vocale
│       ├── translator.py    # Module de traduction
│       ├── summarizer.py    # Module de résumé du contenu vidéo
│       ├── subtitle.py      # Module de traitement des sous-titres
│       ├── video.py         # Module de traitement vidéo
│       ├── pipeline.py      # Pipeline de traitement
│       └── utils.py         # Fonctions utilitaires
├── pyproject.toml           # Configuration du projet
├── requirements.txt         # Dépendances
├── LICENSE                  # Licence MIT
├── .gitignore               # Fichier Git ignore
└── README.md
```

## 📦 Installation

### Prérequis

FFmpeg est requis pour le traitement vidéo. Installez-le d'abord :

**macOS :**
```bash
# Installation de base (suffisante pour les sous-titres souples)
brew install ffmpeg

# Pour les sous-titres incrustés (--hard-sub), FFmpeg avec support libass est nécessaire :
brew install ffmpeg-full
echo 'export PATH="/opt/homebrew/opt/ffmpeg-full/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

> **Note** : L'installation standard `brew install ffmpeg` n'inclut pas le support libass, requis pour la fonction `--hard-sub`. Si vous rencontrez l'erreur « No option name near force_style », installez `ffmpeg-full`.

**Ubuntu/Debian :**
```bash
sudo apt update && sudo apt install ffmpeg
```
> Le paquet apt inclut généralement le support libass. Si vous rencontrez l'erreur « No option name near force_style » avec `--hard-sub`, installez libass : `sudo apt install libass-dev` puis réinstallez ffmpeg.

**Windows :**
Téléchargez et installez [FFmpeg](https://ffmpeg.org/download.html) (recommandé : build complet de [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) ou builds de [BtbN](https://github.com/BtbN/FFmpeg-Builds/releases), qui incluent le support libass)

### Installation rapide (recommandé)

```bash
pip install video-translate
```

Ou utilisez [uv](https://github.com/astral-sh/uv) (plus rapide) :

```bash
uv pip install video-translate
```

### Installation de développement

Si vous souhaitez contribuer au développement ou modifier le code :

```bash
# 1. Cloner le projet
git clone https://github.com/innovationmech/video-translate.git
cd video-translate

# 2. Installer uv (si pas encore installé)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Installer les dépendances (y compris les outils de développement)
uv sync --dev

# Ou installer avec pip en mode éditable
pip install -e ".[dev]"
```

### Configuration de la clé API

Inscrivez-vous et obtenez une clé API sur [DeepSeek Open Platform](https://platform.deepseek.com/) :

```bash
export DEEPSEEK_API_KEY='your-api-key-here'
```

Ou utilisez OpenAI :
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 Utilisation

### Utilisation en ligne de commande

```bash
# Utilisation de base (anglais → chinois)
video-translate video.mp4

# Ou avec python -m
python -m video_translate video.mp4
```

### Exemples de traduction multilingue

```bash
# Anglais → Chinois (par défaut)
video-translate video.mp4

# Japonais → Chinois
video-translate video.mp4 --source ja --target zh

# Anglais → Japonais
video-translate video.mp4 --source en --target ja

# Chinois → Anglais
video-translate video.mp4 --source zh --target en

# Coréen → Japonais
video-translate video.mp4 --source ko --target ja

# Français → Allemand
video-translate video.mp4 --source fr --target de
```

### Options de la ligne de commande

**Options de base :**

| Option | Description |
|--------|-------------|
| `-s, --source` | Code de la langue source (par défaut : en) |
| `-t, --target` | Code de la langue cible (par défaut : zh) |
| `--list-languages` | Lister toutes les langues prises en charge |
| `-o, --output` | Spécifier le répertoire de sortie |
| `-m, --model` | Taille du modèle Whisper (tiny/base/small/medium/large) |
| `-v, --version` | Afficher la version |
| `--verbose` | Afficher les journaux détaillés |

**Options de traduction :**

| Option | Description |
|--------|-------------|
| `--translator` | Moteur de traduction (deepseek/openai) |
| `--api-key` | Clé API de traduction |
| `--api-base` | URL de base de l'API (optionnel, pour les points d'accès personnalisés) |
| `--llm-model` | Nom du modèle LLM (optionnel, remplace le modèle par défaut) |

**Options de sous-titres :**

| Option | Description |
|--------|-------------|
| `--target-only` | Sortir uniquement les sous-titres de la langue cible, sans le texte source |
| `--source-first` | Langue source en haut, langue cible en bas |

**Options vidéo :**

| Option | Description |
|--------|-------------|
| `--no-embed` | Ne pas intégrer les sous-titres dans la vidéo, générer uniquement les fichiers de sous-titres |
| `--hard-sub` | Utiliser les sous-titres incrustés (gravés dans la vidéo) |
| `--font-size` | Taille de police des sous-titres incrustés (par défaut : 24) |
| `--hw-accel` | Accélération matérielle pour l'encodage des sous-titres incrustés (auto/none/videotoolbox/nvenc/qsv/amf, par défaut : auto) |
| `--video-quality` | Qualité vidéo des sous-titres incrustés, valeur CRF (0-51, plus bas = meilleur, par défaut : 23) |

**Options de résumé :**

| Option | Description |
|--------|-------------|
| `--no-summary` | Désactiver le résumé du contenu vidéo |
| `--summary-lang` | Code de langue du résumé (par défaut : suit la langue cible) |
| `--max-key-points` | Nombre maximum de points clés dans le résumé (par défaut : 5) |
| `--no-timeline` | Exclure la chronologie du résumé |

**Options avancées :**

| Option | Description |
|--------|-------------|
| `--json-progress` | Sortie de progression au format JSON (pour l'intégration GUI) |

### Plus d'exemples

```bash
# Utiliser un modèle plus grand pour une meilleure précision
video-translate video.mp4 --model large

# Générer uniquement les fichiers de sous-titres, sans intégrer dans la vidéo
video-translate video.mp4 --no-embed

# Générer des sous-titres incrustés (gravés dans la vidéo)
video-translate video.mp4 --hard-sub

# Sous-titres incrustés avec accélération matérielle NVIDIA et haute qualité
video-translate video.mp4 --hard-sub --hw-accel nvenc --video-quality 18

# Sortir uniquement les sous-titres de la langue cible
video-translate video.mp4 --target-only

# Utiliser la traduction OpenAI
video-translate video.mp4 --translator openai

# Utiliser un point d'accès API et un modèle personnalisés
video-translate video.mp4 --api-base https://your-api.com/v1 --llm-model your-model

# Désactiver le résumé du contenu vidéo
video-translate video.mp4 --no-summary

# Générer un résumé en anglais avec jusqu'à 10 points clés
video-translate video.mp4 --summary-lang en --max-key-points 10

# Spécifier le répertoire de sortie
video-translate video.mp4 -o ./output

# Sortie de progression JSON pour l'intégration GUI
video-translate video.mp4 --json-progress
```

### Utilisation en tant que bibliothèque

```python
from video_translate import (
    Config,
    TranscriberConfig,
    TranslatorConfig,
    TranslationPipeline,
    WhisperModel,
    TranslatorType,
    Language,
)
from video_translate.config import SummaryConfig, VideoConfig, HardwareAccel

# Créer la configuration - traduction du japonais vers le chinois
config = Config(
    transcriber=TranscriberConfig(
        model=WhisperModel.BASE,
        language="ja"  # Langue source
    ),
    translator=TranslatorConfig(
        type=TranslatorType.DEEPSEEK,
        api_key="your-api-key",
        source_language=Language.JAPANESE,
        target_language=Language.CHINESE,
    ),
    video=VideoConfig(
        embed_subtitle=True,
        soft_subtitle=False,  # Utiliser les sous-titres incrustés
        hardware_accel=HardwareAccel.AUTO,
    ),
    summary=SummaryConfig(
        enabled=True,
        max_key_points=5,
        include_timeline=True,
    ),
)

# Créer le pipeline de traitement
pipeline = TranslationPipeline(config)

# Traiter la vidéo
result = pipeline.process("video.mp4")

print(f"Fichier de sous-titres : {result['subtitle_file']}")
print(f"Vidéo de sortie : {result['output_video']}")
print(f"Fichier de résumé : {result['summary_file']}")

# Accéder aux données du résumé
if result['summary']:
    summary = result['summary']
    print(f"Titre : {summary.title}")
    print(f"Aperçu : {summary.overview}")
    for point in summary.key_points:
        print(f"  - {point}")
```

## 🤖 Sélection du modèle Whisper

| Modèle | Taille | Mémoire | Vitesse | Précision |
|--------|--------|---------|---------|-----------|
| tiny | 39M | ~1 Go | La plus rapide | Faible |
| base | 74M | ~1 Go | Rapide | Moyenne |
| small | 244M | ~2 Go | Moyenne | Bonne |
| medium | 769M | ~5 Go | Lente | Élevée |
| large | 1550M | ~10 Go | La plus lente | La plus élevée |

Recommandations :
- Aperçu rapide : Utilisez `tiny` ou `base`
- Utilisation en production : Utilisez `small` ou `medium`
- Qualité maximale : Utilisez `large`

## 🔌 Extension des moteurs de traduction

Le projet utilise une conception modulaire, facilitant l'ajout de nouveaux moteurs de traduction :

```python
from video_translate.translator import BaseTranslator

class MyTranslator(BaseTranslator):
    @property
    def name(self) -> str:
        return "MyTranslator"

    def translate_text(self, text: str, context: str = "") -> str:
        # Implémenter la logique de traduction
        pass

    def translate_batch(self, texts: list[str]) -> list[str]:
        # Implémenter la logique de traduction par lot
        pass
```

## 📁 Fichiers de sortie

- `nomvideo_{code_langue}.srt` - Fichier de sous-titres (ex. : `video_zh.srt`, `video_ja.srt`)
- `nomvideo_{code_langue}_summary.json` - Résumé du contenu vidéo au format JSON (titre, aperçu, points clés, sujets, chronologie)
- `nomvideo_{code_langue}.mp4` - Vidéo avec sous-titres intégrés (si l'intégration est sélectionnée)

## ⚠️ Notes

1. **La première exécution** téléchargera automatiquement le modèle Whisper, veuillez assurer une connexion Internet stable
2. **Les sous-titres incrustés** réencodent la vidéo, ce qui prend plus de temps ; utilisez `--hw-accel` pour activer l'accélération matérielle et accélérer l'encodage
3. **Les sous-titres souples** ne font que copier les flux, plus rapide mais peut ne pas être pris en charge par certains lecteurs
4. Assurez-vous que FFmpeg est installé sur votre système
5. Les Mac Apple Silicon utilisent automatiquement l'accélération MPS pour Whisper et VideoToolbox pour l'encodage vidéo
6. **Le résumé vidéo** est activé par défaut et utilise la même API LLM que la traduction ; utilisez `--no-summary` pour le désactiver

## 🛠️ Développement

```bash
# Installer les dépendances de développement
uv sync --dev

# Exécuter les tests
uv run pytest

# Formatage du code
uv run black src/

# Vérification du code
uv run ruff check src/

# Vérification des types
uv run mypy src/
```

## 📄 Licence

Ce projet est distribué sous la [Licence MIT](LICENSE).

Copyright (c) 2026 innovationmech
