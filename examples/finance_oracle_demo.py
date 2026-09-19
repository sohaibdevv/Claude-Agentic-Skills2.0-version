"""
AgentOS 2.0 — FinanceOracle Demo
Activate the finance-oracle skill via the Claude API
"""
import anthropic
from pathlib import Path


def load_skill(skill_name: str) -> str:
    skill_path = Path(__file__).parent.parent / skill_name / "SKILL.md"
    return skill_path.read_text()


def run_finance_oracle(question: str) -> str:
    skill = load_skill("finance-oracle")
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8096,
        system=skill,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


def black_scholes_demo() -> None:
    """Run Black-Scholes options analysis via FinanceOracle"""
    print("=== FinanceOracle: Options Analysis ===\n")

    question = """
    Analyze NVDA options for an earnings play this week.
    Current price: $875. Use Black-Scholes to price an ATM call expiring in 5 days.
    Risk-free rate: 5.3%. IV: 68%. Factor in vol crush risk post-earnings.
    Recommend a strategy and calculate the Greeks.
    """

    result = run_finance_oracle(question)
    print(result)


def portfolio_optimization_demo() -> None:
    """Run Black-Litterman portfolio construction via FinanceOracle"""
    print("=== FinanceOracle: Portfolio Optimization ===\n")

    question = """
    Build a Black-Litterman optimized portfolio with these assets:
    SPY (40%), QQQ (20%), TLT (20%), GLD (10%), BTC (10%).
    My view: QQQ will outperform by 3% over the next quarter (confidence 65%).
    Use delta=2.5, tau=0.05. Show the math and optimal weights.
    """

    result = run_finance_oracle(question)
    print(result)


if __name__ == "__main__":
    # Uncomment to run:
    # black_scholes_demo()
    # portfolio_optimization_demo()

    print("AgentOS 2.0 — FinanceOracle ready.")
    print("Set ANTHROPIC_API_KEY and uncomment a demo function to run.")
