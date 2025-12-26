
#include <iostream>
#include <iomanip>
#include <chrono>
#include <cstdint>

inline double calculate(std::int64_t iterations, double param1, double param2) {
    double result = 1.0;
    for (std::int64_t i = 1; i <= iterations; ++i) {
        double j = i * param1 - param2;
        result -= 1.0 / j;
        j = i * param1 + param2;
        result += 1.0 / j;
    }
    return result;
}

int main() {
    const std::int64_t iterations = 200'000'000;
    const double param1 = 4.0;
    const double param2 = 1.0;

    auto start = std::chrono::high_resolution_clock::now();
    double result = calculate(iterations, param1, param2) * 4.0;
    auto end = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> elapsed = end - start;
    double seconds = elapsed.count();

    std::cout << "结果: " << std::fixed << std::setprecision(12) << result << "\n";
    std::cout << "执行时间: " << std::fixed << std::setprecision(6) << seconds << " 秒\n";
    return 0;
}
