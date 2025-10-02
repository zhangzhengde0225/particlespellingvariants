# Particle Spelling Variants

A Python library for generating and managing particle spelling variants using PDG database and AI API.

粒子拼写变体及物理性质工具

同一个粒子或共振态有不同的拼写方法，本工具适配了692种粒子的编程名、LaTex名、EvtGen名、HTML名、Unicode名以及其他别名，基本涵盖粒子名称。使用本工具，可根据粒子名称准确获取某个粒子的基本标识、多种拼写变体、物理属性、量子数、类型标识、衰变分支比等信息，为物理分析智能体提供支持。

## Features

1. **Generate variants**: Query by MCID ([Monte Carlo ID](./docs/what_is_MCID.md)) from API to generate particle variants
2. **Merge data**: Merge existing and newly generated MCID data
3. **MCP Supported**: Can be used as a plugin for large language models via Model Context Protocol (MCP)

## File Structure

```
particlespellingvariants/
   main.py                 # Main script
   generator.py            # Particle variant generator (modify `_call_llm_api()` if needed)
   data_merger.py          # Data merging tool
   particle_variants.json  # Data storage file
   README.md               # Documentation
   Usage/Particle.py       # Used to create Particle object
```

## Dependencies

```bash
pip install pdg particle hepai
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
python main.py --mode both --mcids 321 -321 --input particle_variants.json --output final_variants.json
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