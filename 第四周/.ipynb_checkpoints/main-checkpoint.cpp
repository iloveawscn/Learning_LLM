#include <chrono>
#include <cstdio>

static inline double calculate(int iterations, int param1, int param2) noexcept {
    double result = 1.0;
    for (int i = 1; i <= iterations; ++i) {
        int j = i * param1 - param2;
        result -= 1.0 / static_cast<double>(j);
        j = i * param1 + param2;
        result += 1.0 / static_cast<double>(j);
    }
    return result;
}

int main() {
    const int iterations = 200000000;
    const int param1 = 4;
    const int param2 = 1;

    auto start_time = std::chrono::steady_clock::now();
    double result = calculate(iterations, param1, param2) * 4.0;
    auto end_time = std::chrono::steady_clock::now();

    double elapsed = std::chrono::duration<double>(end_time - start_time).count();

    std::printf("结果: %.12f\n", result);
    std::printf("执行时间: %.6f 秒\n", elapsed);
    return 0;
}