use crate::lootbox::models::WeightedItem;

pub fn weighted_random(items: &Vec<WeightedItem>, weights: &Vec<i32>) -> Option<WeightedItem> {
    use rand::Rng;
    use rand::rngs::OsRng;
    use std::cmp::Ordering;

    fn bisect_right(arr: &Vec<i32>, x: i32) -> usize {
        arr.binary_search_by(|&item| {
            if item <= x {
                Ordering::Less
            } else {
                Ordering::Greater
            }
        }).unwrap_or_else(|i| i)
    }

    let mut rng = OsRng;
    let cumulative_weights: Vec<i32> = weights
        .iter()
        .scan(0, |sum, &x| {
            *sum += x;
            Some(*sum)
        })
        .collect();
    let total = cumulative_weights.last().copied().unwrap_or(0);
    let random_value = rng.gen_range(0..=total);
    let index = bisect_right(&cumulative_weights, random_value);

    items.get(index).cloned() // Возвращаем клонированный элемент
}
