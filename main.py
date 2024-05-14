from title import title
from src.odds.odds import get_nba_odds, calculate_margins

def main():
    title()


    df = get_nba_odds()
    print(df)
    result = calculate_margins(df)
    print("Top 5 values sorted by best arbing opportunities:")
    print(result)


if __name__ == "__main__":
    main()