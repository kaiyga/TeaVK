import sys
URL= sys.argv[1]
p2 = "".join(URL.split("#access_token=")[1])
p3 = p2.split("&")[0]
print('\n\n',p3)