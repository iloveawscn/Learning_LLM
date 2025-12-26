use std::time::Instant;

// LCG (线性同余生成器) 状态和参数。
// M = 2^32 由 u32 的回绕算术隐式处理。
struct Lcg {
    state: u32,
}

impl Lcg {
    const A: u32 = 1664525;
    const C: u32 = 1013904223;

    fn new(seed: u32) -> Self {
        Lcg { state: seed }
    }
}

impl Iterator for Lcg {
    type Item = u32;

    #[inline(always)]
    fn next(&mut self) -> Option<Self::Item> {
        // 使用回绕算术模拟 (a * x + c) % 2^32
        self.state = Self::A.wrapping_mul(self.state).wrapping_add(Self::C);
        Some(self.state)
    }
}

/// 为 n 个伪随机数序列计算最大子数组和。
/// 此实现使用 Kadane 算法，具有 O(n) 的性能，
/// 这比原始 Python 代码中的 O(n^2) 方法快得多，
/// 同时产生完全相同的数学结果。
/// 随机数是即时生成和处理的，以避免分配数组。
fn max_subarray_sum(n: usize, seed: u32, min_val: i64, max_val: i64) -> i64 {
    let mut lcg = Lcg::new(seed);
    let range = max_val - min_val + 1;

    // 处理第一个元素以初始化 Kadane 算法的变量。
    let first_val = lcg.next().unwrap() as i64 % range + min_val;
    let mut max_so_far = first_val;
    let mut max_ending_here = first_val;

    // 处理剩余的 n-1 个元素。
    for _ in 1..n {
        let x = lcg.next().unwrap() as i64 % range + min_val;
        max_ending_here = x.max(max_ending_here + x);
        max_so_far = max_so_far.max(max_ending_here);
    }
    
    max_so_far
}

/// 使用不同的种子运行 max_subarray_sum 模拟 20 次，
/// 并返回它们结果的总和。
fn total_max_subarray_sum(n: usize, initial_seed: u32, min_val: i64, max_val: i64) -> i64 {
    let mut total_sum: i64 = 0;
    let mut lcg = Lcg::new(initial_seed);

    // 外层循环运行 20 次，与 Python 脚本中相同。
    for _ in 0..20 {
        let seed = lcg.next().unwrap();
        total_sum += max_subarray_sum(n, seed, min_val, max_val);
    }
    
    total_sum
}

fn main() {
    // 来自 Python 脚本的参数。
    const N: usize = 10000;
    const INITIAL_SEED: u32 = 42;
    const MIN_VAL: i64 = -10;
    const MAX_VAL: i64 = 10;

    let start_time = Instant::now();
    let result = total_max_subarray_sum(N, INITIAL_SEED, MIN_VAL, MAX_VAL);
    let end_time = start_time.elapsed();

    // 打印结果和执行时间，格式与 Python 脚本相同。
    println!("最大子数组总和（20次运行）： {}", result);
    println!("执行时间：{:.6f} 秒", end_time.as_secs_f64());
}