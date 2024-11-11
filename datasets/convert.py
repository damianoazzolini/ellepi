dataset = "bupa.pl"

fp = open(dataset, "r")
lines = fp.read().splitlines()
fp.close()

model_n = -1

for line in lines:
    if line.startswith("begin(model"):
        line_t = line.split("begin(model(")[1]
        line_t = line_t.split("))")[0]
        model_n = line_t
    elif line.startswith("end(model"):
        model_n = -1
    else:
        if model_n != -1:
            # add the model as first argument
            if line.startswith("neg("):
                neg, name, arguments = line.split('(',maxsplit=2)
                line = f"neg({name}({model_n},{arguments}"
            else:
                name, arguments = line.split('(',maxsplit=1)
                line = f"{name}({model_n},{arguments}"
            print(line)
        else:
            print(line)