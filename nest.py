import json


def recursive_f(d, output, level, levels):
    for key, value in d.items():
        if key == levels[level]:
            del d[key]
            output[value] = {}

            level += 1
            if level == len(levels):
                output[value] = [d]
                return
            break

    recursive_f(d, output[value], level, levels)


def nest(json_data, levels):
    nested_result = {}

    for d in json_data:
        if len(levels) > len(d) - 1:
            return "Too many nesting levels specified, for this input maximum is 3", False

        for level in levels:
            if level not in d:
                return f"Invalid key provided, '{level}' does not exist in input", False

        recursive_f(d, nested_result, 0, levels)

    return nested_result, True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="""
        Create a nested dictionary of dictionaries of array from a JSON input
        """
    )

    parser.add_argument("levels", nargs="+",
                        help="Keys on which to nest starting from highest level")

    args = parser.parse_args()

    with open('input.json') as js:
        result, successful = nest(json.load(js), args.levels)

        print(result)
