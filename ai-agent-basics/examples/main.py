def main():
    while True:
        try:
            user_input = input("Enter a command (or 'exit' to quit): ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            else:
                print(f"You entered: {user_input}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
