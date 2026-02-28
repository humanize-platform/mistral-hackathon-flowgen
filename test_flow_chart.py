from generate_flow_chart import generate_flow_chart


def main():
    content = "I go to market, buy veg, return home"
    print("Input content:", content)
    print("Generating flow chart...\n")

    result = generate_flow_chart(content)
    print("Generated XML:\n")
    print(result)


if __name__ == "__main__":
    main()
