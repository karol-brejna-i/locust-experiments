def mark(category, message):
    import datetime
    now = datetime.datetime.now()

    new_path = f"./{category}.txt"
    with open(new_path, 'a') as file:
        file.write(f"{now}\t{message}\n")
