import sys

# The 8 possible L-shaped moves of a knight: (dx, dy)
MOVES = [(1, 2), (2, 1), (2, -1), (1, -2),
         (-1, -2), (-2, -1), (-2, 1), (-1, 2)]


def solve_knights_tour(cols, rows, start_x, start_y):
    """Return a list of (x, y) covering every square exactly once, or None."""
    total = cols * rows

    if total % 2 == 1 and (start_x + start_y) % 2 == 1:
        return None

    visited = [[False] * cols for _ in range(rows)]

    def on_board(x, y):
        return 0 <= x < cols and 0 <= y < rows

    def free_neighbours(x, y):
        """Unvisited squares a knight on (x, y) can jump to."""
        result = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if on_board(nx, ny) and not visited[ny][nx]:
                result.append((nx, ny))
        return result

    path = []

    def backtrack(x, y):
        visited[y][x] = True
        path.append((x, y))

        if len(path) == total:          # every square visited -> success
            return True

        candidates = free_neighbours(x, y)

        # Warnsdorff's rule: try the square with the FEWEST onward moves first (ties broken by distance from the board centre, which pushes the knight to finish the edges/corners first).
        cx, cy = (cols - 1) / 2, (rows - 1) / 2
        candidates.sort(key=lambda p: (len(free_neighbours(*p)),
                                       -(abs(p[0] - cx) + abs(p[1] - cy))))

        for nx, ny in candidates:
            if backtrack(nx, ny):
                return True

        # Dead end: undo this move and let the caller try another branch.
        visited[y][x] = False
        path.pop()
        return False

    return path if backtrack(start_x, start_y) else None


def print_board(path, cols, rows):
    """Show the order in which each square is visited (1 = start)."""
    order = [[0] * cols for _ in range(rows)]
    for step, (x, y) in enumerate(path, start=1):
        order[y][x] = step
    width = len(str(cols * rows))
    for row in order:
        print(" ".join(str(n).rjust(width) for n in row))


def main():
    # Input format:
    #   line 1: columns rows      (e.g. "5 5")
    #   line 2: start_x start_y   (e.g. "2 2")
    cols, rows = map(int, input().split())
    start_x, start_y = map(int, input().split())

    if not (0 <= start_x < cols and 0 <= start_y < rows):
        print("path not found")
        return

    sys.setrecursionlimit(max(10000, cols * rows * 2))
    path = solve_knights_tour(cols, rows, start_x, start_y)

    if path is None:
        print("path not found")
        return

    for x, y in path:
        print(f"{x},{y}")

    print()
    print("Visit order on the board:")
    print_board(path, cols, rows)


if __name__ == "__main__":
    main()
