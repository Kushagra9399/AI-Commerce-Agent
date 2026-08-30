from app.agent.agent import chat


def main():

    queries = [
        "I need a Sony 55 inch 4K TV under 60000"
    ]

    for query in queries:

        print("\n" + "=" * 70)
        print("USER:")
        print(query)

        response = chat(query)

        print("\nAGENT:")
        print(response)


if __name__ == "__main__":
    main()