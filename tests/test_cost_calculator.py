
import unittest

from tools.cost_calculator import calculate_monthly_llm_cost


class TestMonthlyLLMCost(unittest.TestCase):

    def test_normal_cost(self):
        result = calculate_monthly_llm_cost.invoke({
            "daily_queries": 200,
            "input_tokens_per_query": 3000,
            "output_tokens_per_query": 500,
            "input_price_per_million": 2,
            "output_price_per_million": 8,
        })

        self.assertEqual(result["input_cost_per_query"], 0.006)
        self.assertEqual(result["output_cost_per_query"], 0.004)
        self.assertEqual(result["total_cost_per_query"], 0.01)
        self.assertEqual(result["monthly_cost_30_days"], 60.0)

    def test_zero_daily_queries(self):
        result = calculate_monthly_llm_cost.invoke({
            "daily_queries": 0,
            "input_tokens_per_query": 3000,
            "output_tokens_per_query": 500,
            "input_price_per_million": 2,
            "output_price_per_million": 8,
        })

        self.assertEqual(result["monthly_cost_30_days"], 0.0)

    def test_negative_daily_queries(self):
        with self.assertRaises(ValueError):
            calculate_monthly_llm_cost.invoke({
                "daily_queries": -1,
                "input_tokens_per_query": 3000,
                "output_tokens_per_query": 500,
                "input_price_per_million": 2,
                "output_price_per_million": 8,
            })

    def test_zero_tokens(self):
        result = calculate_monthly_llm_cost.invoke({
            "daily_queries": 200,
            "input_tokens_per_query": 0,
            "output_tokens_per_query": 0,
            "input_price_per_million": 2,
            "output_price_per_million": 8,
        })

        self.assertEqual(result["total_cost_per_query"], 0)
        self.assertEqual(result["monthly_cost_30_days"], 0)

    def test_negative_tokens(self):
        with self.assertRaises(ValueError):
            calculate_monthly_llm_cost.invoke({
                "daily_queries": 200,
                "input_tokens_per_query": -1,
                "output_tokens_per_query": 500,
                "input_price_per_million": 2,
                "output_price_per_million": 8,
            })

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            calculate_monthly_llm_cost.invoke({
                "daily_queries": 200,
                "input_tokens_per_query": 3000,
                "output_tokens_per_query": 500,
                "input_price_per_million": -2,
                "output_price_per_million": 8,
            })


if __name__ == "__main__":
    unittest.main()
