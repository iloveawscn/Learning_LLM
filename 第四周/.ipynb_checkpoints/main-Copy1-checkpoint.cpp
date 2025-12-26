#include <iostream>
#include <iomanip>
#include <chrono>
#include <cstdint>

static inline double calculate(uint64_t iterations, double param1, double param2) {
    double result = 1.0;
    double jneg = param1 - param2;
    double jpos = param1 + param2;
    const double step = param1;

    uint64_t i = 0;
    const uint64_t unroll = 8;
    const uint64_t limit = (iterations / unroll) * unroll;

    for (; i < limit; i += unroll) {
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;

        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
        result -= 1.0 / jneg; result += 1.0 / jpos; jneg += step; jpos += step;
    }
    for (; i < iterations; ++i) {
        result -= 1.0 / jneg;
        result += 1.0 / jpos;
        jneg += step;
        jpos += step;
    }
    return result;
}

int main() {
    using clock = std::chrono::steady_clock;
    auto start_time = clock::now();

    double result = calculate(200000000ULL, 4.0, 1.0) * 4.0;

    auto end_time = clock::now();
    double seconds = std::chrono::duration<double>(end_time - start_time).count();

    std::cout.setf(std::ios::fixed);
    std::cout << "结果: " << std::setprecision(12) << result << "\n";
    std::cout << "执行时间: " << std::setprecision(6) << seconds << " 秒\n";
    return 0;
}