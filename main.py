from title import title
from src.odds.odds import get_odds, calculate_margins

def main():
    #ascii title
    title()

    #prompt user for input
    print("What sport would you like to see the best arbing opportunities for?")
    print("|  Input  |  Sport    |")

    options = {1: "basketball_nba", 2: "baseball_mlb"}
    for key, value in options.items():
        print(f"|    {key}    |  {value}   |")
    
    key = input()

    df = get_odds(options[int(key)])
    print(df)
    result = calculate_margins(df)
    print("Top 5 values sorted by best arbing opportunities:")
    print(result)


if __name__ == "__main__":
    main()