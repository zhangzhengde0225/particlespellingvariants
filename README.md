# Particle Spelling Variants

A Python library for generating and managing particle spelling variants using PDG database and AI API.

## Features

1. **Generate variants**: Query by MCID from API to generate particle variants
2. **Merge data**: Merge existing and newly generated MCID data

## File Structure

```
particlespellingvariants/
   main.py                 # Main script
   generator.py            # Particle variant generator
   data_merger.py          # Data merger
   particle_variants.json  # Data storage
   README.md              # Documentation
```

## Dependencies

```bash
pip install pdg hepai particle
```

## Usage

### 1. Generate particle data

```bash
# Generate all standard particles
python main.py --mode generate

# Generate specific MCIDs
python main.py --mode generate --mcids 11 -11 211 -211
```

### 2. Merge data files

```bash
# Merge two specific files
python main.py --mode merge --input old_data.json new_data.json --output merged.json

# Alternative syntax with --new-data
python main.py --mode merge --input old_data.json --new-data new_data.json --output merged.json
```

### 3. Generate and merge in one step

```bash
# Generate new data and merge with existing
python main.py --mode both --input particle_variants.json --output final_variants.json
```

## Data Format

Each particle record contains:

```json
{
  "name": "Particle name",
  "mcid": "Particle ID (int)",
  "programmatic_name": "Code name",
  "latex_name": "LaTeX name", 
  "evtgen_name": "EvtGen name",
  "html_name": "HTML name",
  "unicode_name": "Unicode name",
  "aliases": ["alias1", "alias2"],
  "typo": ["typo1", "typo2"]
}
```

## API Configuration

Set environment variable:
```bash
export HEPAI_API_KEY="your-api-key"
```

Configure API base URL if needed.

## Features

- Uses PDG and Particle libraries for particle information
- AI-powered variant generation using LLM
- Intelligent data merging and deduplication
- MCID-based particle identification
- Data validation and quality checks
- Comprehensive error handling