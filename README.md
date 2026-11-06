# DNA Replication and Translation

A small interactive biology game built with Python and Pygame. Its Polish-language interface guides players through copying a DNA sequence and assembling an amino-acid chain from mRNA codons.

## Requirements

- Python 3.9 or later
- Pygame

## Run the game

From the project directory, install Pygame and start the game:

```bash
python -m pip install pygame
python CHRISgra.py
```

Keep the four `hemo*.png` image files beside `CHRISgra.py`; the game loads them when showing the protein illustration at the end.

## How to play

1. Select **START**.
2. **DNA replication:** type the missing nucleotide sequence using `A`, `T`, `C`, and `G`. Use **Backspace** to correct an entry. The game advances when the sequence is complete.
3. **Translation:** drag the amino acid matching the highlighted codon into the ribosome area. Continue until the chain is complete.
4. After the protein search animation, press **Enter** or **Space** to view a protein illustration.

Select **RESTART** at any time to begin again with a randomly selected DNA sequence. Close the game window to quit.

## Project files

- `CHRISgra.py` — game logic, interface, and genetic code data.
- `hemo1.png` through `hemo4.png` — protein illustrations used in the final screen.
