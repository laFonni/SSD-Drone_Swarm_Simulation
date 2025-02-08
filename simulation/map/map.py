from simulation.map.sector import Sector

class Map:
    def __init__(self, width, height, rows=10, columns=10):
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.sectors = [
            [Sector(row, col, width // columns) for col in range(columns)]
            for row in range(rows)
        ]
        self.best_sector = None
        self.__add_neighbours_to_sectors()

    def __add_neighbours_to_sectors(self, radius=2):
        """
        Dodaje sąsiednie sektory do listy sąsiadów w zadanym promieniu.

        :param radius: Zasięg, do którego mają być dodawani sąsiedzi (1 oznacza bezpośrednich sąsiadów, 2 dalszych itd.).
        """
        for row_idx, row in enumerate(self.sectors):
            for col_idx, sector in enumerate(row):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if dx == 0 and dy == 0:
                            continue  # Pomijamy sam sektor

                        neighbor_row = row_idx + dy
                        neighbor_col = col_idx + dx

                        if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.columns:
                            sector.add_neighbor(self.sectors[neighbor_row][neighbor_col])

    def draw(self, screen):
        for row in self.sectors:
            for sector in row:
                sector.draw(screen)

    def update_attractiveness(self):
        """
        Aktualizuje atrakcyjność sektorów i usuwa sprawdzone sektory.
        """
        self.sectors = [sector for sector in self.sectors if not sector.searched]  # Usuwamy sprawdzone sektory

        for sector in self.sectors:
            sector.calculate_attractiveness()