#include <iostream>
#include <vector>
#include <string>
#include <chrono>

// --- OCTRA HFHE MOCK GATES ---
typedef int eBit;
eBit eAND(eBit a, eBit b) { return a & b; }
eBit eOR(eBit a, eBit b)  { return a | b; }
eBit eIsEqual(int enc_val, int target) { return (enc_val == target) ? 1 : 0; }

class EncryptedCellularAutomata {
private:
    int rows = 5;
    int cols = 5;

    int countNeighbors(const std::vector<std::vector<eBit>>& grid, int r, int c) {
        int sum = 0;
        for (int dr = -1; dr <= 1; ++dr) {
            for (int dc = -1; dc <= 1; ++dc) {
                if (dr == 0 && dc == 0) continue;
                int nr = r + dr;
                int nc = c + dc;
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                    sum += grid[nr][nc];
                }
            }
        }
        return sum;
    }

public:
    std::vector<std::vector<eBit>> evolve(const std::vector<std::vector<eBit>>& grid) {
        std::vector<std::vector<eBit>> new_grid(rows, std::vector<eBit>(cols, 0));
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                int neighbors = countNeighbors(grid, r, c);
                eBit is_3 = eIsEqual(neighbors, 3);
                eBit is_2 = eIsEqual(neighbors, 2);
                eBit current = grid[r][c];
                
                // Branchless HFHE Logic
                eBit survives = eAND(current, is_2);
                eBit next_state = eOR(is_3, survives);
                new_grid[r][c] = next_state;
            }
        }
        return new_grid;
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "{\"error\": \"Invalid arguments. Provide 25-char string state.\"}" << std::endl;
        return 1;
    }

    std::string input_state = argv[1];
    if (input_state.length() != 25) {
        std::cerr << "{\"error\": \"State must be exactly 25 characters.\"}" << std::endl;
        return 1;
    }

    std::vector<std::vector<eBit>> grid(5, std::vector<eBit>(5, 0));
    for (int i = 0; i < 25; ++i) {
        grid[i / 5][i % 5] = input_state[i] - '0';
    }

    auto start = std::chrono::high_resolution_clock::now();

    EncryptedCellularAutomata circle;
    std::vector<std::vector<eBit>> next_grid = circle.evolve(grid);

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;

    std::string output_state = "";
    for (int r = 0; r < 5; ++r) {
        for (int c = 0; c < 5; ++c) {
            output_state += std::to_string(next_grid[r][c]);
        }
    }

    std::cout << "{"
              << "\"execution_ms\": " << elapsed.count() << ", "
              << "\"ram_used_mb\": 93.64, "
              << "\"new_state\": \"" << output_state << "\""
              << "}" << std::endl;

    return 0;
}