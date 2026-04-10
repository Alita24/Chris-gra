import pygame
import random
import sys
import itertools
import os
import pickle

SAVE_FILE = "game_save.dat"

# --- USER LOGIC ---
class DNA:
    def __init__(self, seq):
        self.seq = seq

    def get_complement(self):
        complements = {'A': 'T', 'G': 'C', 'T': 'A', 'C': 'G'}
        s = map(complements.__getitem__, list(self.seq))
        return ''.join(s)

    def get_rna_complement(self):
        complements = {'A': 'U', 'G': 'C', 'T': 'A', 'C': 'G'}
        s = map(complements.__getitem__, list(self.seq))
        return ''.join(s)


class Aminoacid:
    def __init__(self, name: str, alias: str, abbr: str, codons: list[str]):
        self.name = name
        self.alias = alias
        self.abbr = abbr
        self.codons = codons

    def check_codon(self, codon: str) -> bool:
        return codon in self.codons

    def get_alias(self):
        return self.alias

    def get_abbr(self):
        return self.abbr


genetic_code_data = {
    "Alanine": ("A", "Ala", ["GCT", "GCC", "GCA", "GCG"]),
    "Arginine": ("R", "Arg", ["CGT", "CGC", "CGA", "CGG", "AGA", "AGG"]),
    "Asparagine": ("N", "Asn", ["AAT", "AAC"]),
    "Aspartic Acid": ("D", "Asp", ["GAT", "GAC"]),
    "Cysteine": ("C", "Cys", ["TGT", "TGC"]),
    "Glutamine": ("Q", "Gln", ["CAA", "CAG"]),
    "Glutamic Acid": ("E", "Glu", ["GAA", "GAG"]),
    "Glycine": ("G", "Gly", ["GGT", "GGC", "GGA", "GGG"]),
    "Histidine": ("H", "His", ["CAT", "CAC"]),
    "Isoleucine": ("I", "Ile", ["ATT", "ATC", "ATA"]),
    "Leucine": ("L", "Leu", ["TTA", "TTG", "CTT", "CTC", "CTA", "CTG"]),
    "Lysine": ("K", "Lys", ["AAA", "AAG"]),
    "Methionine": ("M", "Met", ["ATG"]),
    "Phenylalanine": ("F", "Phe", ["TTT", "TTC"]),
    "Proline": ("P", "Pro", ["CCT", "CCC", "CCA", "CCG"]),
    "Serine": ("S", "Ser", ["TCT", "TCC", "TCA", "TCG", "AGT", "AGC"]),
    "Threonine": ("T", "Thr", ["ACT", "ACC", "ACA", "ACG"]),
    "Tryptophan": ("W", "Trp", ["TGG"]),
    "Tyrosine": ("Y", "Tyr", ["TAT", "TAC"]),
    "Valine": ("V", "Val", ["GTT", "GTC", "GTA", "GTG"]),
    "STOP": ("*", "Stp", ["TAA", "TAG", "TGA"])
}

amino_acids = [
    Aminoacid(name, data[0], data[1], data[2])
    for name, data in genetic_code_data.items()
]

def choose_DNA():
    dataset = [
        "ATGGTGCTGTCTCCTGCCGACAAGACCAACGTCAAGGCCGCCTGGGGTAAGGTCGGCGCGCACGCTGGCGAGTATGGTGCGGAGGCCCTG",
        "AAGAAGGTGGCCGACGCGCTGACCAACGCCGTGGCGCACGTGGACGACATGCCCAACGCGCTGTCCGCCCTGAGCGACCTGCACGCGCAC",
        "AAGCTTCGGGTGGACCCGGTCAACTTCAAGCTCCTAAGCCACTGCCTGCTGGTGACCCTGGCCGCCCACCTCCCCGCCGAGTTCACCCCT",
        "CACCTCCCCGCCGAGTTCACCCCTGCGGTGCACGCTTCCCTGGACAAGTTCCTGGCTTCTGTGAGCACCGTGCTGACCTCCAAATACCGT"]
    return random.choice(dataset)


# --- PYGAME WRAPPER ---
pygame.init()
WIDTH, HEIGHT = 1400, 820
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Replikacja i Translacja")

LIGHT_PURPLE = (230, 210, 255)
DARK_PURPLE = (128, 0, 128)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEST = (0, 70, 255)

font_large = pygame.font.SysFont("monospace", 36, bold=True)
font_medium = pygame.font.SysFont("monospace", 24, bold=True)
font_small = pygame.font.SysFont("monospace", 16)
char_width = font_large.size("A")[0]


class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.randint(2, 6)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > WIDTH: self.vx *= -1
        if self.y < 0 or self.y > HEIGHT: self.vy *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, (200, 180, 230),
                           (int(self.x), int(self.y)), self.radius)


def get_random_color():
    return (
        random.randint(50, 200), random.randint(50, 200),
        random.randint(50, 200))


aa_color_map = {name: get_random_color() for name in genetic_code_data.keys()}


class DraggableAA:
    def __init__(self, name, abbr, target_index=-1):
        self.name = name
        self.abbr = abbr
        self.color = aa_color_map[self.name]
        self.x = random.randint(50, WIDTH - 150)
        if random.choice([True, False]):
            self.y = random.randint(50, HEIGHT // 2 - 150)
        else:
            self.y = random.randint(HEIGHT // 2 + 150, HEIGHT - 50)
        self.radius = 30
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.dragging = False
        self.locked = target_index >= 0
        self.chain_index = target_index

    def move(self):
        if not self.dragging and not self.locked:
            self.x += self.vx
            self.y += self.vy
            if self.x < self.radius or self.x > WIDTH - self.radius: self.vx *= -1
            if self.y < self.radius or self.y > HEIGHT - self.radius: self.vy *= -1

            center_top = HEIGHT // 2 - 140
            center_bottom = HEIGHT // 2 + 140
            if center_top < self.y < center_bottom:
                self.vy *= -1
                self.y = center_top if self.y < HEIGHT // 2 else center_bottom

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)),
                           self.radius)
        text = font_medium.render(self.abbr, True, BLACK)
        surface.blit(text, (
            self.x - text.get_width() // 2, self.y - text.get_height() // 2))


def draw_transparent_oval(surface, color, rect, alpha):
    temp_surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.ellipse(temp_surface, (*color, alpha), temp_surface.get_rect())
    surface.blit(temp_surface, (rect[0], rect[1]))


particles = [Particle() for _ in range(100)]
INPUT_LENGTH = 20
restart_button_rect = pygame.Rect(WIDTH - 150, 20, 130, 40)

start_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 60)

def reset_game():
    global full_rna_target, target_aa_sequence
    global target_aa_abbr_sequence, target_aa_names, input_sequence
    global pre_transcribed_len, dna_display, coding_dna_display, dna_pre_display, target_input, half_len
    global translation_index, target_codons_rna, floating_aas, dragged_item
    global stage, shake_frames, blast_executed
    global search_stage_start

    coding_dna = choose_DNA()
    template_dna = DNA(coding_dna).get_complement()

    full_rna_target = coding_dna.replace('T', 'U')

    target_aa_sequence = []
    target_aa_abbr_sequence = []
    target_aa_names = []

    for i in range(0, len(coding_dna), 3):
        for j in amino_acids:
            if j.check_codon(coding_dna[i:i + 3]):
                target_aa_sequence.append(j.get_alias())
                target_aa_abbr_sequence.append(j.get_abbr())
                target_aa_names.append(j.name)

    stage = 0  
    shake_frames = 0
    blast_executed = False
    input_sequence = ""
    pre_transcribed_len = len(template_dna) - INPUT_LENGTH

    dna_display = template_dna[-50:] 
    coding_dna_display = coding_dna[-50:]
    
    display_len = len(dna_display)
    half_len = display_len - INPUT_LENGTH
    
    dna_pre_display = coding_dna_display[:half_len]
    target_input = coding_dna_display[half_len:]

    translation_index = 20
    target_codons_rna = [full_rna_target[i:i + 3] for i in
                         range(0, len(full_rna_target), 3)]

    floating_aas = [DraggableAA(name, abbr, target_index=i if i < 20 else -1)
                    for i, (name, abbr) in
                    enumerate(zip(target_aa_names, target_aa_abbr_sequence))]
    random.shuffle(floating_aas)
    dragged_item = None
    search_stage_start = None

reset_game()

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(LIGHT_PURPLE)

    for p in particles:
        p.move()
        p.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if restart_button_rect.collidepoint(event.pos):
                reset_game()
                continue

        if 'stage' in globals() and stage == 0:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button_rect.collidepoint(event.pos):
                    stage = 1
                    continue
            continue

        if stage == 1:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_sequence = input_sequence[:-1]
                elif len(input_sequence) < INPUT_LENGTH:
                    char = event.unicode.upper()
                    if char in ['A', 'T', 'C', 'G']:
                        input_sequence += char

                if input_sequence == target_input:
                    stage = 2
           

        elif stage == 2:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for aa in reversed(floating_aas):
                        if not aa.locked and (event.pos[0] - aa.x) ** 2 + (
                                event.pos[1] - aa.y) ** 2 <= aa.radius ** 2:
                            aa.dragging = True
                            dragged_item = aa
                            break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragged_item:
                    ribosome_rect = pygame.Rect(WIDTH // 2 - 100,
                                                HEIGHT // 2 - 110, 200, 190)
                    if ribosome_rect.collidepoint(event.pos):
                        expected_name = target_aa_names[translation_index]
                        if dragged_item.name == expected_name:
                            dragged_item.locked = True
                            dragged_item.chain_index = translation_index
                            translation_index += 1
                            shake_frames = 6
                            if translation_index == len(target_aa_names):
                                stage = 3

                    dragged_item.dragging = False
                    dragged_item = None
            elif event.type == pygame.MOUSEMOTION:
                if dragged_item:
                    dragged_item.x, dragged_item.y = event.pos

    if 'stage' in globals() and stage == 0:
        intro_title = "Replikacja DNA i Translacja"
        intro_text_lines = [
            "Witaj w interaktywnym symulatorze przejścia informacji",
            "genetycznej od DNA do białka!",
            "",
            "W tej grze nauczysz się:",
            "- Jak powstaje nowa nić DNA (replikacja)",
            "- Jak z mRNA powstaje łańcuch aminokwasów (translacja)",
            "",
            "Przechodź przez kolejne etapy, klikaj i wpisuj to o co prosi ekran.",
            "Powodzenia!",
            ""
        ]
   

        intro_rect = pygame.Rect(WIDTH // 2 - 450, HEIGHT // 2 - 270, 900, 540)
        intro_panel = pygame.Surface((intro_rect.w, intro_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(intro_panel, (255, 255, 255, 210), (0, 0, intro_rect.w, intro_rect.h), border_radius=28)
        screen.blit(intro_panel, (intro_rect.x, intro_rect.y))

        title_surface = font_large.render(intro_title, True, DARK_PURPLE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, intro_rect.y + 32))

        for n, line in enumerate(intro_text_lines):
            y = intro_rect.y + 120 + n * 38
            color = DARK_PURPLE if (n==0 or n>=2) else BLACK
            font = font_medium if n==0 or (line and line.startswith("-")) or n==1 else font_small
            line_surface = font.render(line, True, color)
            screen.blit(line_surface, (intro_rect.x + 38, y))

        pygame.draw.rect(screen, (70, 120, 255), start_button_rect, border_radius=18)
        start_text = font_large.render("START", True, WHITE)
        screen.blit(start_text, (
            start_button_rect.x + start_button_rect.w // 2 - start_text.get_width() // 2,
            start_button_rect.y + start_button_rect.h // 2 - start_text.get_height() // 2))
        
        restart_surf = pygame.Surface((restart_button_rect.w, restart_button_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(restart_surf, (200, 50, 50, 100), (0, 0, restart_button_rect.w, restart_button_rect.h), border_radius=8)
        restart_text = font_medium.render("RESTART", True, (255,255,255,170))
        restart_surf.blit(restart_text, (15, 5))
        screen.blit(restart_surf, (restart_button_rect.x, restart_button_rect.y))
        pygame.display.flip()
        clock.tick(60)
        continue

    if stage == 1:
        legend_y = 40
        for comp in ["A <--> T", "C <--> G"]:
            legend_y += 50
            screen.blit(font_large.render(comp, True, BLACK), (20, legend_y))
        
        desc_text_lines = [
            "Etap 1: Replikacja DNA ",
            "",
            "Przepisuj kolejne nukleotydy, wpisując komplementarne zasady w dolnej sekwencji.",
            "",
            "Poprawnie wprowadź cały fragment, by przejść dalej!"
        ]
        desc_rect = pygame.Rect(WIDTH // 2 - 370, HEIGHT // 2 - 235, 740, 140)
   
        desc_panel = pygame.Surface((desc_rect.w, desc_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(desc_panel, (255, 255, 255, 210), (0, 0, desc_rect.w, desc_rect.h), border_radius=20)
        y_text = 18
        for line in desc_text_lines:
            font_sel = font_medium if line.startswith("Etap") else font_small
            color_sel = DARK_PURPLE if line.startswith("Etap") else BLACK
            desc_panel.blit(font_sel.render(line, True, color_sel), (24, y_text))
            y_text += 28 if line else 18  

        screen.blit(desc_panel, (desc_rect.x, desc_rect.y))
 
        start_x = 50
        y_template = HEIGHT // 2 - 30  
        y_complement = HEIGHT // 2 + 20 

        for i, char in enumerate(dna_display):
            screen.blit(font_large.render(char, True, BLACK),
                        (start_x + i * char_width, y_template))

        for i, char in enumerate(dna_pre_display):
            screen.blit(font_large.render(char, True, DARK_PURPLE),
                        (start_x + i * char_width, y_complement))

        input_start_x = start_x + half_len * char_width
        for i, char in enumerate(input_sequence):
            color = DARK_PURPLE if char == target_input[i] else RED
            screen.blit(font_large.render(char, True, color),
                        (input_start_x + i * char_width, y_complement))

        cursor_x = input_start_x + len(input_sequence) * char_width
        draw_transparent_oval(screen, TEST,
                              (cursor_x - 100, y_complement - 60, 200, 100), 100)

    elif stage == 2:
        desc_text_lines = [
            "Etap 2: Translacja",
            "",
            "Przeciągnij odpowiednie aminokwasy na właściwe miejsce,",
            "zgodnie z kodonem wskazanym powyżej.",
            "",
            "Poprawnie uzupełnij sekwencję, by przejść dalej!"
        ]
        desc_rect = pygame.Rect(WIDTH // 2 - 370, HEIGHT // 2 - 260, 740, 180)

        desc_panel = pygame.Surface((desc_rect.w, desc_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(desc_panel, (255, 255, 255, 210), (0, 0, desc_rect.w, desc_rect.h), border_radius=20)
        y_text = 18
        for line in desc_text_lines:
            font_sel = font_medium if line.startswith("Etap") else font_small
            color_sel = DARK_PURPLE if line.startswith("Etap") else BLACK
            desc_panel.blit(font_sel.render(line, True, color_sel), (24, y_text))
            y_text += 28 if line else 18  
       

        screen.blit(desc_panel, (desc_rect.x, desc_rect.y))
   
        draw_transparent_oval(screen, DARK_PURPLE,
                              (WIDTH // 2 - 100, HEIGHT // 2 - 110, 200, 120),
                              120)

        codon_start_x = WIDTH // 2 - int(char_width * 1.5)
        base_x = codon_start_x - (translation_index * 3 * char_width)

        for i, char in enumerate(full_rna_target):
            x_pos = base_x + i * char_width
            if 0 < x_pos < WIDTH:
                if translation_index * 3 <= i < (translation_index + 1) * 3:
                    screen.blit(font_large.render(char, True, RED),
                                (x_pos, HEIGHT // 2 - 20))
                else:
                    screen.blit(font_large.render(char, True, BLACK),
                                (x_pos, HEIGHT // 2 - 20))

        draw_transparent_oval(screen, DARK_PURPLE,
                              (WIDTH // 2 - 80, HEIGHT // 2 + 5, 160, 90),
                              120)

        if translation_index < len(target_aa_names):
            expected_abbr = target_aa_abbr_sequence[translation_index]

            target_x = WIDTH // 2
            target_y = HEIGHT // 2 - 60

            stencil_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(stencil_surface, (255, 255, 255, 255),
                               (30, 30), 30, width=3)

            stencil_text = font_medium.render(expected_abbr, True,
                                              (255, 255, 255, 220))
            stencil_surface.blit(stencil_text, (
                30 - stencil_text.get_width() // 2,
                30 - stencil_text.get_height() // 2))

            screen.blit(stencil_surface, (target_x - 30, target_y - 30))

        for aa in floating_aas:
            if aa.locked:
                aa.x = (WIDTH // 2) + (aa.chain_index - translation_index) * 60
                aa.y = HEIGHT // 2 - 60
            aa.move()
            aa.draw(screen)

        if dragged_item:
            dragged_item.draw(screen)

    elif stage == 3:
        wait_time = 5000
        current_ticks = pygame.time.get_ticks()
        
        if search_stage_start is None:
            search_stage_start = current_ticks

        if current_ticks - search_stage_start < wait_time:
            text = font_large.render("Szukam białka w bazie...", True, DARK_PURPLE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 ))
        else:
            # UWAGA: Pygame nie obsługuje "\n", dzielimy tekst na dwie zmienne
            text1 = font_large.render("Znaleziono białko!", True, DARK_PURPLE)
            text2 = font_large.render("Wciśnij  Enter, aby zobaczyć jego strukturę.", True, DARK_PURPLE)
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 ))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 30))
            
            # Bezpośrednie odpytanie klawiatury - rozwiązuje problem podwójnego event.get()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                stage = 4
                
                # Ładujemy i skalujemy obraz TYLKO RAZ przy zmianie etapu
                if "AUGGCCAUGGCG" in full_rna_target:
                    protein_image = pygame.image.load("hemo1.png")
                elif "UUUAAACCCGGG" in full_rna_target:
                    protein_image = pygame.image.load("hemo2.png")
                elif "CCGAUGUUUAAA" in full_rna_target:
                    protein_image = pygame.image.load("hemo3.png")
                else:
                    protein_image = pygame.image.load("hemo4.png")
                
                max_dim = 550  
                img_w, img_h = protein_image.get_size()
                scale = min(max_dim / img_w, max_dim / img_h, 1)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                
                # Zapisujemy do zmiennej globalnej, aby etap 4 mógł to po prostu narysować
                global scaled_protein
                scaled_protein = pygame.transform.smoothscale(protein_image, (new_w, new_h))
                global draw_x, draw_y
                draw_x = WIDTH // 2 - new_w // 2
                draw_y = HEIGHT // 2 - new_h // 2

    elif stage == 4:
        # Po prostu wyświetla to, co załadowano ułamek sekundy wcześniej
        if 'scaled_protein' in globals():
            screen.blit(scaled_protein, (draw_x, draw_y))

    # Draw RESTART button
    pygame.draw.rect(screen, (200, 50, 50), restart_button_rect,
                     border_radius=8)
    restart_text = font_medium.render("RESTART", True, WHITE)
    screen.blit(restart_text,
                (restart_button_rect.x + 15, restart_button_rect.y + 5))

    if shake_frames > 0:
        shake_x = random.randint(-2, 2)
        shake_y = random.randint(-2, 2)
        screen_copy = screen.copy()
        screen.fill(LIGHT_PURPLE)
        screen.blit(screen_copy, (shake_x, shake_y))
        shake_frames -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
