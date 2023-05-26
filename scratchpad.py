str = []
with open("npc.txt", "r") as f:
	str = f.readlines()

dict = {0: "", 1: ""}
i = 0
for x in str:
	if str.index(x) % 7 == 0:
		str[str.index(x)] = x.title()
	elif x == "":
		pass
	else:
		str[str.index(x)] = "**" + x.replace(":", "**").replace("\n", "\\n")

with open("npc.txt", "a") as f:
	for x in str:
		raw = r'{}'.format(x)
		f.write(raw)
		if ((str.index(x)-5) % 7 == 0):
			f.write('\n')